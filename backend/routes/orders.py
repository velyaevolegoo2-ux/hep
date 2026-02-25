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
