import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# ✅ Global dictionary to store conversations by session/user_id
conversations = {}

def chat_with_gemini(user_input: str, session_id: str = "default"):
    """
    Chat with Gemini and remember conversation history per session.
    """
    # Get history for this session, or create new
    history = conversations.get(session_id, [])

    # Start chat with previous history
    chat = model.start_chat(history=history)
    response = chat.send_message(user_input)

    # Save back the updated history
    conversations[session_id] = chat.history

    return response.text
