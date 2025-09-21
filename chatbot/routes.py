from fastapi import APIRouter, Form
from .controller import chat_with_gemini

router = APIRouter()

@router.post("/chat")
async def chat_api(
    user_input: str = Form(...),
    session_id: str = Form("default")  # ✅ optional: use "default" if not given
):
    reply = chat_with_gemini(user_input, session_id=session_id)
    return {"reply": reply, "session_id": session_id}
