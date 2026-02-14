"""
Database models for Hep
Simplified version without Etsy chats
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from database import Base

class OrderCache(Base):
    """Cache of orders from Notion"""
    __tablename__ = "order_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)  # а511
    master = Column(String)  # К23 Ольга
    status = Column(String)  # В работе
    deadline = Column(String)  # Нужен к
    master_date = Column(String)  # Дата мастера
    sum_total = Column(String)  # Сумма
    sum_etsy = Column(String)  # Сумма етси
    tags = Column(String)  # Теги (comma-separated)
    composition = Column(Text)  # Состав
    etsy_link = Column(String)  # Ссылка на Etsy чат
    notion_page_id = Column(String)  # ID страницы в Notion
    last_synced = Column(DateTime(timezone=True), server_default=func.now())

class QuickReply(Base):
    """Quick reply templates"""
    __tablename__ = "quick_replies"
    
    id = Column(Integer, primary_key=True, index=True)
    label = Column(String)  # "Спасибо за заказ"
    text_russian = Column(Text)  # Текст на русском
    text_english = Column(Text)  # Текст на английском
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

class TelegramSend(Base):
    """History of messages sent to Telegram"""
    __tablename__ = "telegram_sends"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, index=True)  # а511
    destination = Column(String)  # 'K23', 'problems', 'pricing'
    message_text = Column(Text)  # Текст сообщения
    telegram_message_id = Column(String)  # ID сообщения в Telegram
    telegram_chat_id = Column(String)  # Chat ID в Telegram
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    cancelled_at = Column(DateTime(timezone=True), nullable=True)  # Если отменено
