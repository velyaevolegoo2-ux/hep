"""
Orders routes for Hep
Handles order management and Notion sync
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import OrderCache
from services.notion_service import sync_orders_from_notion
from datetime import datetime

router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.get("/")
async def get_orders(search: str = None, db: Session = Depends(get_db)):
    """
    Get all orders from cache
    
    Args:
        search: Optional search query (filters by order_number or etsy_link)
    
    Returns:
        List of orders
    """
    query = db.query(OrderCache)
    
    if search:
        # Search by order number OR Etsy link
        search_term = f"%{search}%"
        query = query.filter(
            (OrderCache.order_number.ilike(search_term)) | 
            (OrderCache.etsy_link.ilike(search_term))
        )
    
    orders = query.all()
    
    return [
        {
            "id": order.id,
            "order_number": order.order_number,
            "master": order.master,
            "status": order.status,
            "deadline": order.deadline,
            "master_date": order.master_date,
            "sum_total": order.sum_total,
            "sum_etsy": order.sum_etsy,
            "tags": order.tags,
            "composition": order.composition,
            "etsy_link": order.etsy_link,
            "last_synced": order.last_synced.isoformat() if order.last_synced else None
        }
        for order in orders
    ]

@router.get("/{order_number}")
async def get_order(order_number: str, db: Session = Depends(get_db)):
    """
    Get single order by order number
    
    Args:
        order_number: Order number (e.g., а511)
    
    Returns:
        Order details
    """
    order = db.query(OrderCache).filter(
        OrderCache.order_number == order_number
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {
        "id": order.id,
        "order_number": order.order_number,
        "master": order.master,
        "status": order.status,
        "deadline": order.deadline,
        "master_date": order.master_date,
        "sum_total": order.sum_total,
        "sum_etsy": order.sum_etsy,
        "tags": order.tags,
        "composition": order.composition,
        "etsy_link": order.etsy_link,
        "notion_page_id": order.notion_page_id,
        "last_synced": order.last_synced.isoformat() if order.last_synced else None
    }

@router.post("/sync-notion")
async def sync_notion(db: Session = Depends(get_db)):
    """
    Sync orders from Notion to local cache
    
    Returns:
        {
            "success": true,
            "synced_count": int
        }
    """
    try:
        # Fetch from Notion
        orders = await sync_orders_from_notion()
        
        synced_count = 0
        
        for order_data in orders:
            # Check if order exists
            existing = db.query(OrderCache).filter(
                OrderCache.order_number == order_data["order_number"]
            ).first()
            
            if existing:
                # Update existing
                for key, value in order_data.items():
                    if key != "notion_page_id":  # Don't update page ID
                        setattr(existing, key, value)
                existing.last_synced = datetime.utcnow()
            else:
                # Create new
                new_order = OrderCache(**order_data)
                db.add(new_order)
            
            synced_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "synced_count": synced_count
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
