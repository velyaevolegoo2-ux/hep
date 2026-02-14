"""
Translation API routes using Claude
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from anthropic import Anthropic
import os

router = APIRouter(prefix="/api/translate", tags=["translate"])

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

class TranslateRequest(BaseModel):
    text: str
    order_number: str

@router.post("/")
async def translate_text(request: TranslateRequest):
    """
    Translate text with auto language detection
    EN → RU or RU → EN
    """
    try:
        # Auto-detect language and translate
        prompt = f"""Определи язык текста и переведи:
- Если текст на английском → переведи на русский
- Если текст на русском → переведи на английский

Контекст: заказ костюма №{request.order_number}

Текст для перевода:
{request.text}

Верни ТОЛЬКО перевод, без пояснений."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        translation = message.content[0].text.strip()
        
        return {
            "translation": translation,
            "order_number": request.order_number
        }
    
    except Exception as e:
        print(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
