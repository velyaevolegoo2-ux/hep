"""
Claude AI service for translations
Based on Hepler implementation
"""
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-20250514"

async def translate_to_russian(english_text: str, order_number: str = None) -> str:
    """
    Translate English to Russian for masters
    
    CRITICAL: Order number is added HERE, not in the service that sends to Telegram!
    This ensures user sees the FINAL text before sending.
    """
    prompt = f"""Переведи это сообщение от клиента на русский язык.

Сообщение на английском:
{english_text}

Инструкции:
- Переведи естественно, как живой человек
- Сохрани вежливый тон
- Если есть специфические термины (costume, wig, wings) - переведи контекстно

Ответь ТОЛЬКО переводом на русском, без пояснений."""

    message = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    translation = message.content[0].text.strip()
    
    # Add order number ONCE, at the beginning
    if order_number and not translation.startswith(order_number):
        translation = f"{order_number}\n{translation}"
    
    return translation

async def translate_to_english(russian_text: str) -> str:
    """
    Translate Russian to English for clients
    
    Note: Does NOT add order number (clients don't need it)
    """
    prompt = f"""Переведи это сообщение на английский язык.

Сообщение на русском:
{russian_text}

Инструкции:
- Переведи естественно, как живой человек
- Сохрани вежливый тон
- Сохрани профессиональный стиль

Ответь ТОЛЬКО переводом на английском, без пояснений."""

    message = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text.strip()
