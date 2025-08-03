from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import time
from datetime import datetime, timedelta
from database import get_db
from schemas import Restaurant, Order, Customer, Review
from crud import RestaurantCRUD, OrderCRUD, CustomerCRUD, ReviewCRUD, MenuItemCRUD
from utils.cache_manager import session_cache, AdvancedCachePatterns, log_cache_performance
from config import CacheNamespace, cache_config

router = APIRouter(prefix="/analytics", tags=["analytics-caching"])

@router.get("/revenue/daily")
@session_cache(
    namespace=CacheNamespace.ANALYTICS_REVENUE,
    key_builder=lambda date, *args, **kwargs: f"daily:revenue:{date}"
)
@log_cache_performance("get_daily_revenue")
async def get_daily_revenue(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db)
):
    """Get daily revenue analytics (24-hour cache)"""
    try:
        # Simulate revenue calculation
        orders, _ = await OrderCRUD.get_orders(db, per_page=1000)

        # Filter orders by date (simplified)
        daily_orders = [order for order in orders if order.status == "delivered"]

        total_revenue = sum(order.total_amount for order in daily_orders)
        order_count = len(daily_orders)
        average_order_value = total_revenue / order_count if order_count > 0 else 0

        # Calculate hourly breakdown
        hourly_breakdown = {}
        for hour in range(24):
            hourly_breakdown[f"{hour:02d}:00"] = {
                "orders": len([o for o in daily_orders if hash(o.id) % 24 == hour]),
                "revenue": total_revenue * (0.02 + (hour % 12) * 0.08)  # Simulate hourly distribution
            }

        return {
            "date": date,
            "total_revenue": round(total_revenue, 2),
            "total_orders": order_count,
            "average_order_value": round(average_order_value, 2),
            "hourly_breakdown": hourly_breakdown,
            "cache_info": {
                "ttl": cache_config.ttl_config.ANALYTICS_DAILY_TTL,
                "cached_at": time.time()
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get daily revenue")

@router.get("/customers/behavior")
@session_cache(
    namespace=CacheNamespace.ANALYTICS_CUSTOMERS,
    key_builder=lambda period, *args, **kwargs: f"behavior:{period}"
)
@log_cache_performance("get_customer_behavior")
async def get_customer_behavior_analytics(
    period: str = Query("7d", description="Period: 1d, 7d, 30d"),
    db: AsyncSession = Depends(get_db)
):
    """Get customer behavior analytics (4-hour cache)"""
    try:
        customers, _ = await CustomerCRUD.get_customers(db, per_page=1000)
        orders, _ = await OrderCRUD.get_orders(db, per_page=1000)

        # Calculate behavior metrics
        total_customers = len(customers)
        active_customers = len([c for c in customers if c.is_active])

        # Order frequency analysis
        customer_order_counts = {}
        for order in orders:
            customer_order_counts[order.customer_id] = customer_order_counts.get(order.customer_id, 0) + 1

        # Segment customers
        segments = {
            "new_customers": len([count for count in customer_order_counts.values() if count == 1]),
            "regular_customers": len([count for count in customer_order_counts.values() if 2 <= count <= 5]),
            "loyal_customers": len([count for count in customer_order_counts.values() if count > 5]),
            "inactive_customers": total_customers - len(customer_order_counts)
        }

        # Calculate average metrics
        avg_orders_per_customer = sum(customer_order_counts.values()) / len(customer_order_counts) if customer_order_counts else 0

        return {
            "period": period,
            "total_customers": total_customers,
            "active_customers": active_customers,
            "customer_segments": segments,
            "average_orders_per_customer": round(avg_orders_per_customer, 2),
            "retention_rate": round((active_customers / total_customers) * 100, 2) if total_customers > 0 else 0,
            "cache_info": {
                "ttl": cache_config.ttl_config.ANALYTICS_LONG_TTL,
                "cached_at": time.time()
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get customer behavior analytics")

@router.get("/restaurants/performance")
async def get_restaurant_performance_analytics(
    restaurant_id: Optional[int] = Query(None, description="Specific restaurant ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get restaurant performance analytics using cache-aside pattern"""
    try:
        if restaurant_id:
            # Use cache-aside pattern for specific restaurant
            cache_key = f"performance:restaurant:{restaurant_id}"

            async def fetch_restaurant_performance():
                restaurant = await RestaurantCRUD.get_restaurant(db, restaurant_id)
                if not restaurant:
                    raise HTTPException(status_code=404, detail="Restaurant not found")

                orders, _ = await OrderCRUD.get_orders(db, restaurant_id=restaurant_id, per_page=1000)
                reviews, _ = await ReviewCRUD.get_restaurant_reviews(db, restaurant_id, per_page=1000)

                # Calculate performance metrics
                total_orders = len(orders)
                completed_orders = len([o for o in orders if o.status == "delivered"])
                total_revenue = sum(o.total_amount for o in orders if o.status == "delivered")
                avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0

                return {
                    "restaurant_id": restaurant_id,
                    "restaurant_name": restaurant.name,
                    "total_orders": total_orders,
                    "completed_orders": completed_orders,
                    "completion_rate": round((completed_orders / total_orders) * 100, 2) if total_orders > 0 else 0,
                    "total_revenue": round(total_revenue, 2),
                    "average_rating": round(avg_rating, 2),
                    "total_reviews": len(reviews),
                    "cache_pattern": "cache-aside"
                }

            return await AdvancedCachePatterns.cache_aside_get(
                CacheNamespace.ANALYTICS_RESTAURANTS,
                cache_key,
                fetch_restaurant_performance
            )

        else:
            # Get all restaurants performance with multi-level caching
            cache_key = "performance:all_restaurants"

            async def fetch_all_performance():
                restaurants, _ = await RestaurantCRUD.get_restaurants(db, per_page=1000)
                performance_data = []

                for restaurant in restaurants[:10]:  # Limit to top 10 for demo
                    orders, _ = await OrderCRUD.get_orders(db, restaurant_id=restaurant.id, per_page=100)
                    completed_orders = len([o for o in orders if o.status == "delivered"])
                    total_revenue = sum(o.total_amount for o in orders if o.status == "delivered")

                    performance_data.append({
                        "restaurant_id": restaurant.id,
                        "restaurant_name": restaurant.name,
                        "total_orders": len(orders),
                        "completed_orders": completed_orders,
                        "total_revenue": round(total_revenue, 2)
                    })

                return {
                    "restaurants": performance_data,
                    "cache_pattern": "multi-level"
                }

            return await AdvancedCachePatterns.multi_level_cache(
                CacheNamespace.ANALYTICS_RESTAURANTS,  # L1: Short TTL
                CacheNamespace.ANALYTICS_REVENUE,      # L2: Long TTL
                cache_key,
                fetch_all_performance
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get restaurant performance analytics")

@router.get("/popular-items")
async def get_popular_items_analytics(
    period: str = Query("7d", description="Period: 1d, 7d, 30d"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get popular items analytics using refresh-ahead caching"""
    try:
        cache_key = f"popular_items:{period}:{limit}"

        async def fetch_popular_items():
            # Simulate popular items calculation
            menu_items, _ = await MenuItemCRUD.get_menu_items(db, per_page=1000)
            orders, _ = await OrderCRUD.get_orders(db, per_page=1000)

            # Calculate item popularity (simplified)
            item_popularity = {}
            for item in menu_items:
                # Simulate order frequency
                popularity_score = hash(item.name) % 100
                item_popularity[item.id] = {
                    "item_id": item.id,
                    "name": item.name,
                    "restaurant_id": item.restaurant_id,
                    "price": item.price,
                    "popularity_score": popularity_score,
                    "estimated_orders": popularity_score * 2
                }

            # Sort by popularity and limit
            popular_items = sorted(
                item_popularity.values(),
                key=lambda x: x["popularity_score"],
                reverse=True
            )[:limit]

            return {
                "period": period,
                "popular_items": popular_items,
                "total_items_analyzed": len(menu_items),
                "cache_pattern": "refresh-ahead"
            }

        return await AdvancedCachePatterns.refresh_ahead_cache(
            CacheNamespace.ANALYTICS_POPULAR,
            cache_key,
            fetch_popular_items,
            refresh_threshold=0.3  # Refresh when 30% of TTL remains
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get popular items analytics")

@router.post("/refresh/{analytics_type}")
async def refresh_analytics_cache(
    analytics_type: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Manually refresh analytics cache in background"""
    try:
        async def refresh_cache_background():
            if analytics_type == "revenue":
                # Refresh revenue analytics
                await get_daily_revenue("2024-01-01", db)
            elif analytics_type == "customers":
                # Refresh customer analytics
                await get_customer_behavior_analytics("7d", db)
            elif analytics_type == "restaurants":
                # Refresh restaurant analytics
                await get_restaurant_performance_analytics(None, db)
            elif analytics_type == "popular":
                # Refresh popular items
                await get_popular_items_analytics("7d", 10, db)

        background_tasks.add_task(refresh_cache_background)

        return {
            "status": "success",
            "message": f"Cache refresh for {analytics_type} analytics started in background",
            "analytics_type": analytics_type,
            "timestamp": time.time()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to start cache refresh")