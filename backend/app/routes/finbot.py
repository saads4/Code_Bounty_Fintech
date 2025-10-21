from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.routes.utils import auth_user
from app.core.config import settings

router = APIRouter()

class ChatIn(BaseModel):
    message: str

def _llm_call(prompt: str)->str:
    if not settings.LLM_API_KEY:
        if "tax" in prompt.lower():
            return "For Indian taxes, compare new vs old regime. Provide income and deductions; I’ll estimate your liability."
        if "budget" in prompt.lower():
            return "A simple 50/30/20 split can work: essentials/wants/savings respectively."
        return "I'm FinBot. Connect an LLM key in backend .env for richer answers."
    return "LLM response placeholder (connect provider to enable)."

@router.post("/chat")
def chat(inp: ChatIn, user = Depends(auth_user)):
    reply = _llm_call(inp.message)
    return {"reply": reply}
