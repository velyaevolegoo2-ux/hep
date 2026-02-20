"""
Telegram Bot service for sending messages to masters
Based on Hepler implementation with CRITICAL principles
"""
import os
from telegram import Bot, InputMediaPhoto
from dotenv import load_dotenv
import base64
import io

load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

# Master chats
MASTER_CHATS = {
    "K23": os.getenv("TELEGRAM_MASTER_K23"),
    "P5": os.getenv("TELEGRAM_MASTER_P5"),
    "KR11": os.getenv("TELEGRAM_MASTER_KR11"),
    "K17": os.getenv("TELEGRAM_MASTER_K17"),
    "K48": os.getenv("TELEGRAM_MASTER_K48"),
}

# Special chats
CHAT_PROBLEMS = os.getenv("TELEGRAM_CHAT_PROBLEMS")
CHAT_PRICING = os.getenv("TELEGRAM_CHAT_PRICING")
CHAT_DELO = os.getenv("TELEGRAM_CHAT_DELO")

async def send_to_telegram(destination: str, message: str) -> dict:
    """
    Send text message to Telegram chat
    
    CRITICAL PRINCIPLE: "What you see is what gets sent"
    - NO emoji additions
    - NO headers ("New message", etc.)
    - NO links
    - NO modifications to message text
    - Message is sent EXACTLY as provided
    
    Args:
        destination: 'K23', 'P5', 'problems', 'pricing', etc.
        message: FINAL text to send (including order number if needed)
    
    Returns:
        {
            "success": bool,
            "telegram_message_id": str,
            "telegram_chat_id": str,
            "error": str (if failed)
        }
    """
    # Determine chat_id
    if destination == "problems":
        chat_id = CHAT_PROBLEMS
    elif destination == "pricing":
        chat_id = CHAT_PRICING
    elif destination == "delo":
        chat_id = CHAT_DELO
    elif destination in MASTER_CHATS:
        chat_id = MASTER_CHATS[destination]
    else:
        return {
            "success": False,
            "error": f"Unknown destination: {destination}"
        }
    
    if not chat_id:
        return {
            "success": False,
            "error": f"Chat ID not configured for destination: {destination}"
        }
    
    try:
        # Send message AS IS - NO modifications!
        telegram_message = await bot.send_message(
            chat_id=chat_id,
            text=message
        )
        
        return {
            "success": True,
            "telegram_message_id": str(telegram_message.message_id),
            "telegram_chat_id": str(chat_id)
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

async def send_media_group_to_telegram(destination: str, message: str, images: list) -> dict:
    """
    Send message with images as media group (album) to Telegram
    
    If more than 10 images - splits into multiple albums with same caption
    Images are sent with compression as album
    Caption is added to the first image of each album
    
    Args:
        destination: 'K23', 'P5', 'problems', 'pricing', etc.
        message: Text message (will be caption of first image in each album)
        images: List of base64 encoded images
    
    Returns:
        {
            "success": bool,
            "telegram_message_id": str,
            "telegram_chat_id": str,
            "error": str (if failed)
        }
    """
    # Determine chat_id
    if destination == "problems":
        chat_id = CHAT_PROBLEMS
    elif destination == "pricing":
        chat_id = CHAT_PRICING
    elif destination == "delo":
        chat_id = CHAT_DELO
    elif destination in MASTER_CHATS:
        chat_id = MASTER_CHATS[destination]
    else:
        return {
            "success": False,
            "error": f"Unknown destination: {destination}"
        }
    
    if not chat_id:
        return {
            "success": False,
            "error": f"Chat ID not configured for destination: {destination}"
        }
    
    try:
        # Split images into chunks of 10 (Telegram limit)
        chunk_size = 10
        image_chunks = [images[i:i + chunk_size] for i in range(0, len(images), chunk_size)]
        
        first_message_id = None
        
        # Send each chunk as separate media group
        for chunk_index, chunk in enumerate(image_chunks):
            media_group = []
            
            for i, img_base64 in enumerate(chunk):
                # Remove data URL prefix if present
                if ',' in img_base64:
                    img_base64 = img_base64.split(',')[1]
                
                # Decode base64 to bytes
                img_bytes = base64.b64decode(img_base64)
                img_file = io.BytesIO(img_bytes)
                img_file.name = f'image_{chunk_index}_{i}.jpg'
                
                # First image of each chunk gets the caption
                if i == 0:
                    # Add chunk number if multiple chunks
                    caption = message
                    if len(image_chunks) > 1:
                        caption = f"{message}\n\n[{chunk_index + 1}/{len(image_chunks)}]"
                    media_group.append(InputMediaPhoto(media=img_file, caption=caption))
                else:
                    media_group.append(InputMediaPhoto(media=img_file))
            
            # Send media group
            messages = await bot.send_media_group(
                chat_id=chat_id,
                media=media_group
            )
            
            # Save first message ID
            if first_message_id is None:
                first_message_id = str(messages[0].message_id)
        
        # Return first message ID
        return {
            "success": True,
            "telegram_message_id": first_message_id,
            "telegram_chat_id": str(chat_id)
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

async def delete_telegram_message(chat_id: str, message_id: str) -> bool:
    """
    Delete a message from Telegram (for undo functionality)
    
    Args:
        chat_id: Telegram chat ID
        message_id: Telegram message ID
    
    Returns:
        True if deleted, False if failed
    """
    try:
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
        return True
    except Exception as e:
        print(f"Failed to delete message: {e}")
        return False
