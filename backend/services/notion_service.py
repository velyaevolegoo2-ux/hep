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
    Fetch all orders from Notion database with pagination
    
    IMPORTANT: Notion uses RUSSIAN field names!
    - "Task name" - order number (а511)
    - "Status" - status (В работе)
    - "Нужен к" - deadline
    - "Дата мастера" - master_date
    - "Мастер" - master (Multi-select field!)
    - "Сумма" - sum_total (Formula field!)
    - "Сумма Etsy" - sum_etsy (Text/Rich text field!)
    - "Теги" - tags
    - "Состав" - composition
    - "Etsy" - etsy_link
    
    Returns:
        List of order dictionaries
    """
    try:
        orders = []
        has_more = True
        start_cursor = None
        
        # Paginate through all results
        while has_more:
            # Query database with cursor
            if start_cursor:
                response = notion.databases.query(
                    database_id=DATABASE_ID,
                    start_cursor=start_cursor
                )
            else:
                response = notion.databases.query(database_id=DATABASE_ID)
            
            # Process this page of results
            for page in response.get("results", []):
                properties = page.get("properties", {})
                
                # Parse fields (handle Russian names and correct types!)
                order = {
                    "notion_page_id": page["id"],
                    "order_number": _get_title(properties.get("Task name")),
                    "status": _get_status(properties.get("Status")),
                    "deadline": _get_date(properties.get("Нужен к")),
                    "master_date": _get_date(properties.get("Дата мастера")),
                    "master": _get_multi_select(properties.get("Мастер")),
                    "sum_total": _get_formula(properties.get("Сумма")),
                    "sum_etsy": _get_rich_text(properties.get("Сумма Etsy")),
                    "tags": _get_multi_select(properties.get("Теги")),
                    "composition": _get_rich_text(properties.get("Состав")),
                    "etsy_link": _get_url(properties.get("Etsy")),
                }
                
                orders.append(order)
            
            # Check if there are more pages
            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")
        
        print(f"✓ Fetched {len(orders)} orders from Notion")
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

def _get_number(prop) -> str:
    """Extract number as string"""
    if not prop or prop.get("type") != "number":
        return ""
    number = prop.get("number")
    if number is not None:
        return str(number)
    return ""

def _get_formula(prop) -> str:
    """Extract formula result as string"""
    if not prop or prop.get("type") != "formula":
        return ""
    formula = prop.get("formula", {})
    formula_type = formula.get("type")
    
    if formula_type == "number":
        number = formula.get("number")
        if number is not None:
            return str(number)
    elif formula_type == "string":
        return formula.get("string", "")
    
    return ""

def _get_people(prop) -> str:
    """Extract people/person field - returns name of first person"""
    if not prop or prop.get("type") != "people":
        return ""
    people = prop.get("people", [])
    if people and len(people) > 0:
        person = people[0]
        return person.get("name", "")
    return ""

def _get_url(prop) -> str:
    """Extract URL"""
    if not prop or prop.get("type") != "url":
        return ""
    return prop.get("url", "")
