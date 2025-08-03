from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from database import get_db
from schemas import MenuItem, MenuItemCreate, MenuItemUpdate, MenuItemList, MenuItemWithRestaurant
from crud import MenuItemCRUD

router = APIRouter(prefix="/menu-items", tags=["menu-items"])

# Note: Restaurant-specific menu item creation is handled in restaurants.py

@router.get("/", response_model=MenuItemList)
async def get_menu_items(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all menu items with pagination"""
    try:
        menu_items, total = await MenuItemCRUD.get_menu_items(db, skip, limit)
        return MenuItemList(
            menu_items=menu_items,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search", response_model=MenuItemList)
async def search_menu_items(
    category: Optional[str] = Query(None, description="Filter by category"),
    vegetarian: Optional[bool] = Query(None, description="Filter by vegetarian"),
    vegan: Optional[bool] = Query(None, description="Filter by vegan"),
    available: Optional[bool] = Query(None, description="Filter by availability"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Search menu items with filters"""
    try:
        menu_items, total = await MenuItemCRUD.search_menu_items(
            db, category, vegetarian, vegan, available, skip, limit
        )
        return MenuItemList(
            menu_items=menu_items,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{item_id}", response_model=MenuItem)
async def get_menu_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific menu item by ID"""
    try:
        menu_item = await MenuItemCRUD.get_menu_item(db, item_id)
        if not menu_item:
            raise HTTPException(status_code=404, detail="Menu item not found")
        return menu_item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{item_id}/with-restaurant", response_model=MenuItemWithRestaurant)
async def get_menu_item_with_restaurant(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a menu item with restaurant details"""
    try:
        menu_item = await MenuItemCRUD.get_menu_item_with_restaurant(db, item_id)
        if not menu_item:
            raise HTTPException(status_code=404, detail="Menu item not found")
        return menu_item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{item_id}", response_model=MenuItem)
async def update_menu_item(
    item_id: int,
    menu_item_update: MenuItemUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a menu item"""
    try:
        menu_item = await MenuItemCRUD.update_menu_item(db, item_id, menu_item_update)
        if not menu_item:
            raise HTTPException(status_code=404, detail="Menu item not found")
        return menu_item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{item_id}", status_code=204)
async def delete_menu_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a menu item"""
    try:
        success = await MenuItemCRUD.delete_menu_item(db, item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Menu item not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
