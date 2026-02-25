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
    Sync orders from Notion to local cache - OPTIMIZED VERSION
    
    Returns:
        {
            "success": true,
            "synced_count": int
        }
    """
    try:
        # Fetch from Notion
        orders = await sync_orders_from_notion()
        
        # Load ALL existing orders into memory at once (FAST!)
        existing_orders = {
            order.order_number: order 
            for order in db.query(OrderCache).all()
        }
        
        synced_count = 0
        new_orders = []
        now = datetime.utcnow()
        seen_in_notion = set()  # Track duplicates within Notion response
        
        # Process all orders
        for order_data in orders:
            order_number = order_data.get("order_number")
            if not order_number:
                continue
            
            # Skip duplicates within Notion response
            if order_number in seen_in_notion:
                print(f"Skipping duplicate in Notion: {order_number}")
                continue
            
            seen_in_notion.add(order_number)
            
            if order_number in existing_orders:
                # Update existing order
                existing = existing_orders[order_number]
                for key, value in order_data.items():
                    if key != "notion_page_id":
                        setattr(existing, key, value)
                existing.last_synced = now
            else:
                # Create new order
                new_order = OrderCache(**order_data, last_synced=now)
                new_orders.append(new_order)
            
            synced_count += 1
        
        # Bulk insert new orders
        if new_orders:
            db.bulk_save_objects(new_orders)
        
        # Single commit for everything
        db.commit()
        
        return {
            "success": True,
            "synced_count": synced_count
        }
    
    except Exception as e:
        db.rollback()
        print(f"Error during sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear-cache")
async def clear_cache(db: Session = Depends(get_db)):
    """
    Clear all cached orders (for debugging/maintenance)
    
    Returns:
        {
            "success": true,
            "deleted_count": int
        }
    """
    try:
        count = db.query(OrderCache).count()
        db.query(OrderCache).delete()
        db.commit()
        
        return {
            "success": True,
            "deleted_count": count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
