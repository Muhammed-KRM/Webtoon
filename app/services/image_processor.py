"""
Image Processor Service - In-painting and text rendering
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap
from typing import List, Dict, Optional
from pathlib import Path
from loguru import logger
from app.core.config import settings


class ImageProcessor:
    """Service for image processing: in-painting and text rendering"""
    
    def __init__(self):
        """Initialize image processor"""
        self.font_path = self._find_font()
        self.default_font_size = settings.DEFAULT_FONT_SIZE
        self.min_font_size = settings.MIN_FONT_SIZE
        self.max_font_size = settings.MAX_FONT_SIZE
    
    def _find_font(self) -> Optional[str]:
        """Find a suitable font file"""
        # Check fonts directory first
        fonts_dir = Path(settings.FONTS_PATH)
        if fonts_dir.exists():
            # Look for common font files
            font_extensions = ['.ttf', '.otf']
            for ext in font_extensions:
                for font_file in fonts_dir.glob(f'*{ext}'):
                    return str(font_file)
        
        # Try system fonts (Windows)
        system_fonts = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "C:/Windows/Fonts/times.ttf",
        ]
        
        for font_path in system_fonts:
            if Path(font_path).exists():
                return font_path
        
        return None
    
    def _load_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Load font with given size"""
        try:
            if self.font_path:
                return ImageFont.truetype(self.font_path, size)
            else:
                return ImageFont.load_default()
        except Exception as e:
            logger.warning(f"Error loading font: {e}, using default")
            return ImageFont.load_default()
    
    def _calculate_font_size(
        self,
        text: str,
        max_width: int,
        max_height: int,
        font_path: Optional[str] = None
    ) -> tuple[int, ImageFont.FreeTypeFont]:
        """
        Calculate optimal font size to fit text in bounding box
        
        Returns:
            (font_size, font_object)
        """
        # Start with default size
        font_size = self.default_font_size
        
        # Binary search for optimal size
        min_size = self.min_font_size
        max_size = self.max_font_size
        
        best_font = None
        best_size = min_size
        
        while min_size <= max_size:
            test_size = (min_size + max_size) // 2
            font = self._load_font(test_size)
            
            # Wrap text to fit width
            wrapped_lines = self._wrap_text(text, max_width, font)
            
            # Calculate total height
            line_height = font.getsize("A")[1] if hasattr(font, 'getsize') else 20
            total_height = len(wrapped_lines) * line_height * 1.2  # 1.2 for line spacing
            
            if total_height <= max_height and self._text_fits_width(wrapped_lines, max_width, font):
                best_size = test_size
                best_font = font
                min_size = test_size + 1
            else:
                max_size = test_size - 1
        
        if best_font is None:
            best_font = self._load_font(best_size)
        
        return best_size, best_font
    
    def _wrap_text(self, text: str, max_width: int, font: ImageFont.FreeTypeFont) -> List[str]:
        """
        Wrap text to fit within max_width with accurate width calculation
        
        Uses textwrap for better handling of long words and proper wrapping
        """
        # Use textwrap for better word breaking
        wrapped = textwrap.wrap(
            text,
            width=max_width // (font.size if hasattr(font, 'size') else 10) if max_width > 0 else 50,
            break_long_words=True,
            break_on_hyphens=True
        )
        
        # Verify each line fits (with accurate measurement)
        lines = []
        for line in wrapped:
            # Get accurate width using font metrics
            if hasattr(font, 'getsize'):
                line_width = font.getsize(line)[0]
            else:
                # Fallback: approximate (0.6 is average character width ratio)
                line_width = len(line) * (font.size if hasattr(font, 'size') else 10) * 0.6
            
            if line_width <= max_width or not lines:  # Always add at least one line
                lines.append(line)
            else:
                # Line too wide, need to break further
                # Split by characters if needed
                chars_per_line = int(max_width / (font.size if hasattr(font, 'size') else 10) * 1.6)
                if chars_per_line > 0:
                    for i in range(0, len(line), chars_per_line):
                        lines.append(line[i:i+chars_per_line])
        
        return lines if lines else [text]
    
    def _text_fits_width(self, lines: List[str], max_width: int, font: ImageFont.FreeTypeFont) -> bool:
        """Check if text lines fit within max_width"""
        for line in lines:
            # Approximate width check
            width = len(line) * (font.size if hasattr(font, 'size') else 10)
            if width > max_width:
                return False
        return True
    
    def process_image(
        self,
        image_bytes: bytes,
        text_blocks: List[Dict],
        translated_texts: List[str]
    ) -> bytes:
        """
        Process image: remove original text and add translated text
        
        Args:
            image_bytes: Original image as bytes
            text_blocks: List of text blocks with coordinates
            translated_texts: List of translated texts
            
        Returns:
            Processed image as bytes
        """
        try:
            # 1. Convert bytes to OpenCV image
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                raise ValueError("Could not decode image")
            
            # 2. Create mask for in-painting
            mask = np.zeros(img.shape[:2], dtype=np.uint8)
            
            for block in text_blocks:
                x, y, w, h = block['coords']
                # Add padding to mask (slightly larger area)
                pad = 5
                x1 = max(0, x - pad)
                y1 = max(0, y - pad)
                x2 = min(img.shape[1], x + w + pad)
                y2 = min(img.shape[0], y + h + pad)
                
                cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
            
            # 3. In-paint to remove text
            clean_img = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
            
            # 4. Convert to PIL for text rendering
            img_pil = Image.fromarray(cv2.cvtColor(clean_img, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img_pil)
            
            # 5. Render translated text
            for i, block in enumerate(text_blocks):
                if i >= len(translated_texts):
                    continue
                
                x, y, w, h = block['coords']
                translated_text = translated_texts[i]
                
                if not translated_text:
                    continue
                
                # Calculate optimal font size
                font_size, font = self._calculate_font_size(translated_text, w, h)
                
                # Wrap text to fit
                wrapped_lines = self._wrap_text(translated_text, w, font)
                
                # Calculate text position (centered)
                line_height = font.getsize("A")[1] if hasattr(font, 'getsize') else font_size
                total_text_height = len(wrapped_lines) * line_height * 1.2
                
                # Start Y position (centered vertically)
                start_y = y + (h - total_text_height) // 2
                
                # Draw each line
                for line_idx, line in enumerate(wrapped_lines):
                    # Calculate line width for centering
                    if hasattr(font, 'getsize'):
                        line_width = font.getsize(line)[0]
                    else:
                        line_width = len(line) * font_size * 0.6  # Approximate
                    
                    line_x = x + (w - line_width) // 2
                    line_y = start_y + (line_idx * line_height * 1.2)
                    
                    # Draw text with outline for readability
                    # Outline
                    for adj in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                        draw.text(
                            (line_x + adj[0], line_y + adj[1]),
                            line,
                            fill=(255, 255, 255),
                            font=font
                        )
                    # Main text
                    draw.text(
                        (line_x, line_y),
                        line,
                        fill=(0, 0, 0),
                        font=font
                    )
            
            # 6. Convert back to bytes (WebP format for better compression)
            buf = io.BytesIO()
            if settings.USE_WEBP:
                try:
                    # Try WebP first (better compression, ~50% smaller)
                    img_pil.save(
                        buf,
                        format='WEBP',
                        quality=settings.IMAGE_QUALITY,
                        method=6  # Best compression method
                    )
                    logger.debug("Saved image as WebP format")
                except Exception as e:
                    # Fallback to JPEG if WebP not supported
                    logger.warning(f"WebP not supported, falling back to JPEG: {e}")
                    buf = io.BytesIO()
                    img_pil.save(buf, format='JPEG', quality=settings.IMAGE_QUALITY)
            else:
                # Use JPEG if WebP disabled
                img_pil.save(buf, format='JPEG', quality=settings.IMAGE_QUALITY)
            return buf.getvalue()
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise

