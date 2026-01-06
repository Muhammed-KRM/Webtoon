"""
OCR Service - Text detection using EasyOCR
"""
import easyocr
import numpy as np
from typing import List, Dict, Any
from loguru import logger
from app.core.config import settings
import cv2

# Global OCR reader (lazy initialization)
_ocr_reader = None


def get_ocr_reader():
    """Get or create OCR reader (singleton)"""
    global _ocr_reader
    if _ocr_reader is None:
        logger.info("Initializing EasyOCR reader...")
        _ocr_reader = easyocr.Reader(
            settings.OCR_LANGUAGES,
            gpu=settings.OCR_GPU  # Use GPU if available
        )
        logger.info("EasyOCR reader initialized")
    return _ocr_reader


class OCRService:
    """Service for OCR operations"""
    
    def __init__(self):
        """Initialize OCR service"""
        self.reader = get_ocr_reader()
    
    def detect_text_blocks(
        self,
        image_bytes: bytes
    ) -> List[Dict[str, Any]]:
        """
        Detect text blocks in an image
        
        Args:
            image_bytes: Image bytes
            
        Returns:
            List of text blocks with coordinates and text
        """
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                logger.error("Failed to decode image")
                return []
            
            # Run OCR
            results = self.reader.readtext(img)
            
            # Format results
            text_blocks = []
            for (bbox, text, confidence) in results:
                # Filter low confidence results
                if confidence < 0.5:
                    continue
                
                # Convert bbox to (x, y, w, h) format
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                x = int(min(x_coords))
                y = int(min(y_coords))
                w = int(max(x_coords) - min(x_coords))
                h = int(max(y_coords) - min(y_coords))
                
                text_blocks.append({
                    "text": text.strip(),
                    "coords": [x, y, w, h],
                    "confidence": float(confidence)
                })
            
            logger.info(f"Detected {len(text_blocks)} text blocks")
            return text_blocks
            
        except Exception as e:
            logger.error(f"Error in OCR detection: {e}", exc_info=True)
            return []
