import sys
import os
sys.path.append(os.getcwd())

try:
    print("Importing config...")
    from app.core.config import settings
    print("Config imported.")
    
    print("Importing main...")
    from main import app
    print("Main imported.")
    
    print("Importing ImageProcessor...")
    from app.services.image_processor import ImageProcessor
    print("ImageProcessor imported.")
    
    print("Importing AITranslator...")
    from app.services.ai_translator import AITranslator
    print("AITranslator imported.")

except Exception as e:
    import traceback
    traceback.print_exc()
