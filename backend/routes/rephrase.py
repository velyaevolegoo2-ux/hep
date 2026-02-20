from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import anthropic
import os

router = APIRouter()

class RephraseRequest(BaseModel):
    text: str

@router.post("/rephrase/")
async def rephrase_text(request: RephraseRequest):
    """
    Rephrase text using Claude API
    """
    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"Перефразируй следующий текст по-другому, сохраняя смысл, тон и язык. Верни ТОЛЬКО перефразированный текст, без пояснений:\n\n{request.text}"
            }]
        )
        
        rephrased = message.content[0].text
        
        return {
            "success": True,
            "rephrased_text": rephrased
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
