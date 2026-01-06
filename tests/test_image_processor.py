import pytest
import numpy as np
import cv2
from app.services.image_processor import ImageProcessor

# Create a sample image for testing
@pytest.fixture
def sample_image():
    # White background 100x100
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    # Add some black text "TEST"
    cv2.putText(img, "TEST", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    # Encode
    success, encoded_img = cv2.imencode('.jpg', img)
    return encoded_img.tobytes()

@pytest.fixture
def sample_blocks():
    # Block covering "TEST"
    return [{
        "text": "TEST",
        "coords": [10, 20, 80, 40], # x, y, w, h
        "confidence": 0.99
    }]

def test_clean_image(sample_image, sample_blocks):
    processor = ImageProcessor()
    
    # Run clean
    cleaned = processor.clean_image(sample_image, sample_blocks)
    
    # Verify output is bytes
    assert isinstance(cleaned, bytes)
    assert len(cleaned) > 0
    
    # decode and check
    nparr = np.frombuffer(cleaned, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    assert img is not None
    assert img.shape == (100, 100, 3)

def test_render_text(sample_image, sample_blocks):
    processor = ImageProcessor()
    
    # Translate "TEST" -> "DENEME"
    translations = ["DENEME"]
    
    # Render
    rendered = processor.render_text(sample_image, sample_blocks, translations)
    
    assert isinstance(rendered, bytes)
    assert len(rendered) > 0

def test_process_image_full_flow(sample_image, sample_blocks):
    processor = ImageProcessor()
    translations = ["DENEME"]
    
    # Run full flow
    result = processor.process_image(sample_image, sample_blocks, translations)
    
    assert isinstance(result, bytes)
    assert len(result) > 0
