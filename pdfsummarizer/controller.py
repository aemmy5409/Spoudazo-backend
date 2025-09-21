# controller.py
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# ✅ Configure Gemini with API key
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def summarize_pdf_with_gemini(file_bytes: bytes, filename: str = "document.pdf") -> str:
    try:

        prompt = """
        You are an AI Study Assistant. Summarize this PDF document for students.

        - Highlight the key ideas clearly
        - Break into sections: 📖 Main Points, 📝 To Remember, ❓ Possible Exam Questions
        - Use simple, clear language (student-friendly)
        - Keep it concise but detailed enough for revision
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(
                data=file_bytes,
                mime_type='application/pdf',
                ),
            prompt]
        )

        return response.text.strip()

    except Exception as e:
        return f"⚠️ Gemini summarization failed: {str(e)}"

