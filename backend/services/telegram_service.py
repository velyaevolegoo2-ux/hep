"""
Telegram Bot service for sending messages to masters
Based on Hepler implementation with CRITICAL principles
"""
import os
from telegram import Bot
from dotenv import load_dotenv

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

async def send_to_telegram(destination: str, message: str) -> dict:
    """
    Send message to Telegram chat
    
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
            text=message  # EXACTLY as provided!
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
