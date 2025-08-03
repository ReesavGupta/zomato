from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database import get_db
from schemas import (
    Restaurant, RestaurantCreate, RestaurantUpdate, RestaurantList,
    RestaurantWithMenu, MenuItem, MenuItemCreate, MenuItemList
)
from crud import RestaurantCRUD, MenuItemCRUD

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.post("/", response_model=Restaurant, status_code=201)
async def create_restaurant(
    restaurant: RestaurantCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new restaurant"""
    try:
        return await RestaurantCRUD.create_restaurant(db, restaurant)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=RestaurantList)
async def get_restaurants(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all restaurants with pagination"""
    try:
        restaurants, total = await RestaurantCRUD.get_restaurants(db, skip, limit)
        return RestaurantList(
            restaurants=restaurants,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/active", response_model=RestaurantList)
async def get_active_restaurants(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get only active restaurants"""
    try:
        restaurants, total = await RestaurantCRUD.get_active_restaurants(db, skip, limit)
        return RestaurantList(
            restaurants=restaurants,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search", response_model=RestaurantList)
async def search_restaurants(
    cuisine: str = Query(..., description="Cuisine type to search for"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Search restaurants by cuisine type"""
    try:
        restaurants, total = await RestaurantCRUD.search_restaurants_by_cuisine(
            db, cuisine, skip, limit
        )
        return RestaurantList(
            restaurants=restaurants,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{restaurant_id}", response_model=Restaurant)
async def get_restaurant(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific restaurant by ID"""
    try:
        restaurant = await RestaurantCRUD.get_restaurant(db, restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return restaurant
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{restaurant_id}", response_model=Restaurant)
async def update_restaurant(
    restaurant_id: int,
    restaurant_update: RestaurantUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a restaurant"""
    try:
        restaurant = await RestaurantCRUD.update_restaurant(db, restaurant_id, restaurant_update)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return restaurant
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{restaurant_id}", status_code=204)
async def delete_restaurant(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a restaurant"""
    try:
        success = await RestaurantCRUD.delete_restaurant(db, restaurant_id)
        if not success:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

# ===== MENU-RELATED ENDPOINTS =====

@router.post("/{restaurant_id}/menu-items/", response_model=MenuItem, status_code=201)
async def create_menu_item(
    restaurant_id: int,
    menu_item: MenuItemCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a menu item to a restaurant"""
    try:
        return await MenuItemCRUD.create_menu_item(db, menu_item, restaurant_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{restaurant_id}/menu", response_model=MenuItemList)
async def get_restaurant_menu(
    restaurant_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all menu items for a restaurant"""
    try:
        menu_items, total = await RestaurantCRUD.get_restaurant_menu(db, restaurant_id, skip, limit)
        if total == 0:
            # Check if restaurant exists
            restaurant = await RestaurantCRUD.get_restaurant(db, restaurant_id)
            if not restaurant:
                raise HTTPException(status_code=404, detail="Restaurant not found")

        return MenuItemList(
            menu_items=menu_items,
            total=total,
            skip=skip,
            limit=limit
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{restaurant_id}/with-menu", response_model=RestaurantWithMenu)
async def get_restaurant_with_menu(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get restaurant with all menu items"""
    try:
        restaurant = await RestaurantCRUD.get_restaurant_with_menu(db, restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return restaurant
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
