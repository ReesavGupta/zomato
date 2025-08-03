from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database import get_db
from schemas import (
    Restaurant, RestaurantCreate, RestaurantUpdate, RestaurantList,
    RestaurantWithMenu, MenuItem, MenuItemCreate, MenuItemList
)
from crud import RestaurantCRUD, MenuItemCRUD
from utils.cache_manager import CacheManager, CacheInvalidator, log_cache_performance, safe_cache

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.post("/", response_model=Restaurant, status_code=201)
async def create_restaurant(
    restaurant: RestaurantCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new restaurant"""
    try:
        result = await RestaurantCRUD.create_restaurant(db, restaurant)
        # Invalidate restaurant caches after creation
        await CacheInvalidator.invalidate_restaurant_caches()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=RestaurantList)
@safe_cache(namespace=CacheManager.RESTAURANTS_NAMESPACE, expire=CacheManager.RESTAURANT_LIST_TTL)
@log_cache_performance("get_restaurants")
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
@safe_cache(namespace=CacheManager.RESTAURANTS_NAMESPACE, expire=CacheManager.RESTAURANT_ACTIVE_TTL)
@log_cache_performance("get_active_restaurants")
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
@safe_cache(namespace=CacheManager.SEARCH_RESULTS_NAMESPACE, expire=CacheManager.RESTAURANT_SEARCH_TTL)
@log_cache_performance("search_restaurants")
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
@safe_cache(namespace=CacheManager.RESTAURANTS_NAMESPACE, expire=CacheManager.RESTAURANT_DETAIL_TTL)
@log_cache_performance("get_restaurant")
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

        # Invalidate restaurant caches after update
        await CacheInvalidator.invalidate_restaurant_caches(restaurant_id)
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

        # Invalidate restaurant caches after deletion
        await CacheInvalidator.invalidate_restaurant_caches(restaurant_id)
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
        result = await MenuItemCRUD.create_menu_item(db, menu_item, restaurant_id)
        # Invalidate menu and restaurant caches after creation
        await CacheInvalidator.invalidate_menu_caches(restaurant_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{restaurant_id}/menu", response_model=MenuItemList)
@safe_cache(namespace=CacheManager.MENU_ITEMS_NAMESPACE, expire=CacheManager.MENU_ITEMS_TTL)
@log_cache_performance("get_restaurant_menu")
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
@safe_cache(namespace=CacheManager.RESTAURANT_MENUS_NAMESPACE, expire=CacheManager.RESTAURANT_WITH_MENU_TTL)
@log_cache_performance("get_restaurant_with_menu")
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

@router.get("/{restaurant_id}/analytics")
@safe_cache(namespace=CacheManager.ANALYTICS_NAMESPACE, expire=CacheManager.ANALYTICS_TTL)
@log_cache_performance("get_restaurant_analytics")
async def get_restaurant_analytics(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive restaurant analytics with caching"""
    try:
        # Verify restaurant exists
        restaurant = await RestaurantCRUD.get_restaurant(db, restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        # Get menu items for analytics
        menu_items, _ = await MenuItemCRUD.get_menu_items(db, restaurant_id=restaurant_id, per_page=1000)

        if not menu_items:
            return {
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant.name,
                "total_menu_items": 0,
                "average_price": 0,
                "price_range": {"min": 0, "max": 0},
                "categories": [],
                "dietary_options": {
                    "vegetarian_items": 0,
                    "vegan_items": 0,
                    "gluten_free_items": 0
                }
            }

        # Calculate analytics
        prices = [item.price for item in menu_items]
        categories = list(set(item.category for item in menu_items if item.category))

        analytics = {
            "restaurant_id": restaurant_id,
            "restaurant_name": restaurant.name,
            "total_menu_items": len(menu_items),
            "average_price": round(sum(prices) / len(prices), 2),
            "price_range": {
                "min": min(prices),
                "max": max(prices)
            },
            "categories": categories,
            "dietary_options": {
                "vegetarian_items": sum(1 for item in menu_items if item.is_vegetarian),
                "vegan_items": sum(1 for item in menu_items if item.is_vegan),
                "gluten_free_items": sum(1 for item in menu_items if item.is_gluten_free)
            }
        }

        return analytics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/analytics/popular-cuisines")
@safe_cache(namespace=CacheManager.ANALYTICS_NAMESPACE, expire=CacheManager.AGGREGATION_TTL)
@log_cache_performance("get_popular_cuisines")
async def get_popular_cuisines(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get popular cuisines across all restaurants"""
    try:
        restaurants, _ = await RestaurantCRUD.get_restaurants(db, per_page=1000)

        # Count cuisines
        cuisine_counts = {}
        for restaurant in restaurants:
            if restaurant.cuisine_type:
                cuisine_counts[restaurant.cuisine_type] = cuisine_counts.get(restaurant.cuisine_type, 0) + 1

        # Sort by popularity
        popular_cuisines = sorted(cuisine_counts.items(), key=lambda x: x[1], reverse=True)[:limit]

        return {
            "popular_cuisines": [
                {"cuisine": cuisine, "restaurant_count": count}
                for cuisine, count in popular_cuisines
            ],
            "total_cuisines": len(cuisine_counts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/analytics/price-ranges")
@safe_cache(namespace=CacheManager.ANALYTICS_NAMESPACE, expire=CacheManager.AGGREGATION_TTL)
@log_cache_performance("get_price_ranges")
async def get_price_ranges(db: AsyncSession = Depends(get_db)):
    """Get price range distribution across all menu items"""
    try:
        # Get all menu items
        all_items, _ = await MenuItemCRUD.get_menu_items(db, per_page=10000)

        if not all_items:
            return {"price_ranges": [], "total_items": 0}

        # Define price ranges
        ranges = [
            {"name": "Budget", "min": 0, "max": 10},
            {"name": "Moderate", "min": 10, "max": 25},
            {"name": "Premium", "min": 25, "max": 50},
            {"name": "Luxury", "min": 50, "max": float('inf')}
        ]

        # Count items in each range
        range_counts = []
        for range_info in ranges:
            count = sum(1 for item in all_items
                       if range_info["min"] <= item.price < range_info["max"])
            range_counts.append({
                "range": range_info["name"],
                "min_price": range_info["min"],
                "max_price": range_info["max"] if range_info["max"] != float('inf') else None,
                "item_count": count,
                "percentage": round((count / len(all_items)) * 100, 2)
            })

        return {
            "price_ranges": range_counts,
            "total_items": len(all_items),
            "average_price": round(sum(item.price for item in all_items) / len(all_items), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
