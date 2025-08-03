from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from database import get_db
from schemas import MenuItem, MenuItemCreate, MenuItemUpdate, MenuItemList, MenuItemWithRestaurant
from crud import MenuItemCRUD
from utils.cache_manager import CacheManager, CacheInvalidator, log_cache_performance, safe_cache

router = APIRouter(prefix="/menu-items", tags=["menu-items"])

# Note: Restaurant-specific menu item creation is handled in restaurants.py

@router.get("/", response_model=MenuItemList)
@safe_cache(namespace=CacheManager.MENU_ITEMS_NAMESPACE, expire=CacheManager.MENU_ITEMS_TTL)
@log_cache_performance("get_menu_items")
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
@safe_cache(namespace=CacheManager.SEARCH_RESULTS_NAMESPACE, expire=CacheManager.MENU_SEARCH_TTL)
@log_cache_performance("search_menu_items")
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
@safe_cache(namespace=CacheManager.MENU_ITEMS_NAMESPACE, expire=CacheManager.MENU_ITEMS_TTL)
@log_cache_performance("get_menu_item")
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
@safe_cache(namespace=CacheManager.MENU_ITEMS_NAMESPACE, expire=CacheManager.MENU_ITEMS_TTL)
@log_cache_performance("get_menu_item_with_restaurant")
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
        # Get the menu item first to find restaurant_id for cache invalidation
        existing_item = await MenuItemCRUD.get_menu_item(db, item_id)
        if not existing_item:
            raise HTTPException(status_code=404, detail="Menu item not found")

        menu_item = await MenuItemCRUD.update_menu_item(db, item_id, menu_item_update)

        # Invalidate menu and restaurant caches after update with advanced strategy
        await CacheInvalidator.invalidate_menu_caches(existing_item.restaurant_id, item_id)
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
        # Get the menu item first to find restaurant_id for cache invalidation
        existing_item = await MenuItemCRUD.get_menu_item(db, item_id)
        if not existing_item:
            raise HTTPException(status_code=404, detail="Menu item not found")

        success = await MenuItemCRUD.delete_menu_item(db, item_id)
        if success:
            # Invalidate menu and restaurant caches after deletion
            await CacheInvalidator.invalidate_menu_caches(existing_item.restaurant_id)

        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/dietary/{dietary_type}", response_model=MenuItemList)
@safe_cache(namespace=CacheManager.DIETARY_NAMESPACE, expire=CacheManager.DIETARY_SEARCH_TTL)
@log_cache_performance("get_dietary_menu_items")
async def get_dietary_menu_items(
    dietary_type: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get menu items by dietary preference (vegetarian, vegan, etc.)"""
    # Map dietary types to boolean fields
    dietary_filters = {
        "vegetarian": {"is_vegetarian": True},
        "vegan": {"is_vegan": True},
        "gluten-free": {"is_gluten_free": True}
    }

    if dietary_type not in dietary_filters:
        raise HTTPException(status_code=400, detail="Invalid dietary type")

    filters = dietary_filters[dietary_type]
    items, total = await MenuItemCRUD.get_menu_items(db, page=page, per_page=per_page, **filters)

    return {"items": items, "total": total, "page": page, "per_page": per_page}

@router.get("/category/{category}", response_model=MenuItemList)
@safe_cache(namespace=CacheManager.CATEGORIES_NAMESPACE, expire=CacheManager.CATEGORY_SEARCH_TTL)
@log_cache_performance("get_category_menu_items")
async def get_category_menu_items(
    category: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get menu items by category"""
    items, total = await MenuItemCRUD.get_menu_items(db, page=page, per_page=per_page, category=category)

    return {"items": items, "total": total, "page": page, "per_page": per_page}
