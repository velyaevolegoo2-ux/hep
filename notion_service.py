"""
Notion API service for syncing orders
Based on Hepler implementation
"""
import os
from notion_client import Client
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

notion = Client(auth=os.getenv("NOTION_API_KEY"))
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

async def sync_orders_from_notion() -> List[Dict]:
    """
    Fetch all orders from Notion database
    
    IMPORTANT: Notion uses RUSSIAN field names!
    - "Task name" - order number (а511)
    - "Status" - status (В работе)
    - "Нужен к" - deadline
    - "Дата мастера" - master_date
    - "Мастер" - master (К23 Ольга)
    - "Сумма" - sum_total
    - "Сумма етси" - sum_etsy  
    - "Теги" - tags
    - "Состав" - composition
    - "Etsy" - etsy_link
    
    Returns:
        List of order dictionaries
    """
    try:
        # Query all pages from database
        response = notion.databases.query(database_id=DATABASE_ID)
        
        orders = []
        for page in response.get("results", []):
            properties = page.get("properties", {})
            
            # Parse fields (handle Russian names!)
            order = {
                "notion_page_id": page["id"],
                "order_number": _get_title(properties.get("Task name")),
                "status": _get_status(properties.get("Status")),
                "deadline": _get_date(properties.get("Нужен к")),
                "master_date": _get_date(properties.get("Дата мастера")),
                "master": _get_rich_text(properties.get("Мастер")),
                "sum_total": _get_rich_text(properties.get("Сумма")),
                "sum_etsy": _get_rich_text(properties.get("Сумма етси")),
                "tags": _get_multi_select(properties.get("Теги")),
                "composition": _get_rich_text(properties.get("Состав")),
                "etsy_link": _get_url(properties.get("Etsy")),
            }
            
            orders.append(order)
        
        return orders
    
    except Exception as e:
        print(f"Error syncing from Notion: {e}")
        return []

def _get_title(prop) -> str:
    """Extract title text"""
    if not prop or prop.get("type") != "title":
        return ""
    title_array = prop.get("title", [])
    if title_array:
        return title_array[0].get("plain_text", "")
    return ""

def _get_rich_text(prop) -> str:
    """Extract rich text"""
    if not prop or prop.get("type") != "rich_text":
        return ""
    rich_text_array = prop.get("rich_text", [])
    if rich_text_array:
        return rich_text_array[0].get("plain_text", "")
    return ""

def _get_status(prop) -> str:
    """Extract status"""
    if not prop or prop.get("type") != "status":
        return ""
    status_obj = prop.get("status")
    if status_obj:
        return status_obj.get("name", "")
    return ""

def _get_date(prop) -> str:
    """Extract date"""
    if not prop or prop.get("type") != "date":
        return ""
    date_obj = prop.get("date")
    if date_obj:
        return date_obj.get("start", "")
    return ""

def _get_multi_select(prop) -> str:
    """Extract multi-select tags as comma-separated string"""
    if not prop or prop.get("type") != "multi_select":
        return ""
    tags = prop.get("multi_select", [])
    return ", ".join([tag.get("name", "") for tag in tags])

def _get_url(prop) -> str:
    """Extract URL"""
    if not prop or prop.get("type") != "url":
        return ""
    return prop.get("url", "")
