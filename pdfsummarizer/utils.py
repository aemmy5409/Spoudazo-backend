import fitz
import requests
from PIL import Image
import io
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get your API key from environment variable
OCR_API_KEY = os.getenv("OCR_API_KEY", "helloworld") 

def ocr_space_api(image_bytes, api_key='helloworld'):
    try:
        response = requests.post(
            'https://api.ocr.space/parse/image',
            files={'filename': ('image.png', image_bytes)},
            data={'apikey': api_key, 'language': 'eng'}
        )

        # DEBUG: Print status code and raw content
        print("🔁 OCR API Response Status:", response.status_code)
        print("📄 Raw Response Content:\n", response.text[:500])  # Limit output size

        # Try parsing JSON
        try:
            result = response.json()
        except Exception as e:
            raise RuntimeError("❌ Failed to parse JSON from OCR API") from e

        if result.get("IsErroredOnProcessing"):
            print("⚠️ OCR API error:", result)
            return ""

        return result['ParsedResults'][0]['ParsedText']

    except Exception as e:
        print("❌ Exception while calling OCR API:", e)
        return ""



def extract_text_from_pdf(file_bytes: bytes, api_key='helloworld') -> str:
    text = ""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    
    for page in doc:
        page_text = page.get_text("text")
        if page_text.strip():
            text += page_text + "\n"
        else:
            # Render the page as an image
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")

            # Use OCR.space to extract text from image bytes
            ocr_text = ocr_space_api(img_bytes, api_key=api_key)
            text += ocr_text + "\n"
    
    return text.strip()
