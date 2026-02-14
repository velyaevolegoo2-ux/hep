"""
Telegram routes for Hep
Handles sending messages to masters via Telegram
"""
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import TelegramSend
from services.telegram_service import send_to_telegram, send_media_group_to_telegram, delete_telegram_message
from datetime import datetime
from typing import List, Optional
import base64

router = APIRouter(prefix="/api/telegram", tags=["telegram"])

class SendRequest(BaseModel):
    order_number: str
    destination: str
    message: str
    images: Optional[List[str]] = None  # Base64 encoded images

class SendResponse(BaseModel):
    success: bool
    telegram_message_id: str = None
    send_id: int = None
    error: str = None

@router.post("/send", response_model=SendResponse)
async def send_message(request: SendRequest, db: Session = Depends(get_db)):
    """
    Send message to Telegram with optional images
    
    Images are sent as media group (album) with compression
    
    Args:
        order_number: Order number (for logging)
        destination: 'K23', 'P5', 'problems', 'pricing', etc.
        message: Text message
        images: Optional list of base64 encoded images
    
    Returns:
        {
            "success": true,
            "telegram_message_id": "12345",
            "send_id": 1
        }
    """
    try:
        # Send with or without images
        if request.images and len(request.images) > 0:
            # Send as media group with images
            result = await send_media_group_to_telegram(
                destination=request.destination,
                message=request.message,
                images=request.images
            )
        else:
            # Send text only
            result = await send_to_telegram(
                destination=request.destination,
                message=request.message
            )
        
        if not result["success"]:
            return SendResponse(
                success=False,
                error=result.get("error", "Unknown error")
            )
        
        # Save to database
        telegram_send = TelegramSend(
            order_number=request.order_number,
            destination=request.destination,
            message_text=request.message,
            telegram_message_id=result["telegram_message_id"],
            telegram_chat_id=result["telegram_chat_id"]
        )
        db.add(telegram_send)
        db.commit()
        db.refresh(telegram_send)
        
        return SendResponse(
            success=True,
            telegram_message_id=result["telegram_message_id"],
            send_id=telegram_send.id
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cancel/{send_id}")
async def cancel_message(send_id: int, db: Session = Depends(get_db)):
    """
    Cancel/delete a sent message (within 60 seconds)
    
    Args:
        send_id: ID of the send in our database
    
    Returns:
        {"success": true} or {"success": false, "error": "..."}
    """
    send = db.query(TelegramSend).filter(TelegramSend.id == send_id).first()
    
    if not send:
        raise HTTPException(status_code=404, detail="Send not found")
    
    if send.cancelled_at:
        raise HTTPException(status_code=400, detail="Already cancelled")
    
    # Check if within 60 seconds
    time_diff = (datetime.utcnow() - send.sent_at).total_seconds()
    if time_diff > 60:
        raise HTTPException(status_code=400, detail="Too late to cancel (>60 seconds)")
    
    # Delete from Telegram
    success = await delete_telegram_message(
        chat_id=send.telegram_chat_id,
        message_id=send.telegram_message_id
    )
    
    if success:
        send.cancelled_at = datetime.utcnow()
        db.commit()
        return {"success": True}
    else:
        return {"success": False, "error": "Failed to delete from Telegram"}

@router.get("/history/{order_number}")
async def get_history(order_number: str, db: Session = Depends(get_db)):
    """
    Get send history for an order
    
    Args:
        order_number: Order number (e.g., а511)
    
    Returns:
        List of sends
    """
    sends = db.query(TelegramSend).filter(
        TelegramSend.order_number == order_number
    ).order_by(TelegramSend.sent_at.desc()).all()
    
    return [
        {
            "id": send.id,
            "destination": send.destination,
            "message_text": send.message_text,
            "sent_at": send.sent_at.isoformat(),
            "cancelled_at": send.cancelled_at.isoformat() if send.cancelled_at else None
        }
        for send in sends
    ]
