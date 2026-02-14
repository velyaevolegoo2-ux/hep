"""
Translation routes for Hep
Handles EN <-> RU translations via Claude
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.claude_service import translate_to_russian, translate_to_english

router = APIRouter(prefix="/api/translate", tags=["translate"])

class TranslateRequest(BaseModel):
    text: str
    direction: str  # "to_russian" or "to_english"
    order_number: str = None  # Optional, only for to_russian

class TranslateResponse(BaseModel):
    translation: str
    original: str

@router.post("/", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    """
    Translate text between English and Russian
    
    CRITICAL BEHAVIOR:
    - For "to_russian": Adds order number at the beginning (if provided)
    - For "to_english": No order number needed
    
    Args:
        text: Text to translate
        direction: "to_russian" or "to_english"
        order_number: Order number (e.g., а511) - only for to_russian
    
    Returns:
        {
            "translation": "Translated text",
            "original": "Original text"
        }
    """
    try:
        if request.direction == "to_russian":
            translation = await translate_to_russian(
                request.text,
                order_number=request.order_number
            )
        elif request.direction == "to_english":
            translation = await translate_to_english(request.text)
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid direction. Must be 'to_russian' or 'to_english'"
            )
        
        return TranslateResponse(
            translation=translation,
            original=request.text
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
