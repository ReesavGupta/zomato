from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import time
import random
from database import get_db
from schemas import Order, Restaurant
from crud import OrderCRUD, RestaurantCRUD
from utils.cache_manager import session_cache, conditional_cache, log_cache_performance
from config import CacheNamespace, cache_config

router = APIRouter(prefix="/realtime", tags=["real-time-data"])

@router.get("/delivery-slots/{restaurant_id}")
@session_cache(
    namespace=CacheNamespace.REALTIME_DELIVERY,
    key_builder=lambda restaurant_id, *args, **kwargs: f"slots:restaurant:{restaurant_id}"
)
@log_cache_performance("get_delivery_slots")
async def get_available_delivery_slots(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get available delivery slots for a restaurant (30-second cache)"""
    try:
        # Verify restaurant exists
        restaurant = await RestaurantCRUD.get_restaurant(db, restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        # Simulate real-time delivery slot calculation
        current_time = time.time()
        base_slots = [
            {"time": "12:00-12:30", "available": True, "estimated_prep_time": 25},
            {"time": "12:30-13:00", "available": True, "estimated_prep_time": 30},
            {"time": "13:00-13:30", "available": False, "estimated_prep_time": 35},
            {"time": "13:30-14:00", "available": True, "estimated_prep_time": 28},
            {"time": "14:00-14:30", "available": True, "estimated_prep_time": 22},
        ]

        # Add dynamic availability based on current load
        for slot in base_slots:
            # Simulate dynamic availability
            if random.random() > 0.3:  # 70% chance of being available
                slot["available"] = True
                slot["estimated_prep_time"] = random.randint(20, 40)
            else:
                slot["available"] = False

        return {
            "restaurant_id": restaurant_id,
            "restaurant_name": restaurant.name,
            "delivery_slots": base_slots,
            "last_updated": current_time,
            "cache_ttl": cache_config.ttl_config.DELIVERY_SLOTS_TTL
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get delivery slots")

@router.get("/restaurant-availability/{restaurant_id}")
@session_cache(
    namespace=CacheNamespace.REALTIME_AVAILABILITY,
    key_builder=lambda restaurant_id, *args, **kwargs: f"availability:restaurant:{restaurant_id}"
)
@log_cache_performance("get_restaurant_availability")
async def get_restaurant_availability(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get real-time restaurant availability and capacity (60-second cache)"""
    try:
        restaurant = await RestaurantCRUD.get_restaurant(db, restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        # Simulate real-time capacity calculation
        current_orders = random.randint(5, 25)  # Simulate current order load
        max_capacity = 30
        capacity_percentage = (current_orders / max_capacity) * 100

        # Determine availability status
        if capacity_percentage < 60:
            status = "available"
            estimated_wait = random.randint(15, 25)
        elif capacity_percentage < 85:
            status = "busy"
            estimated_wait = random.randint(30, 45)
        else:
            status = "very_busy"
            estimated_wait = random.randint(50, 70)

        return {
            "restaurant_id": restaurant_id,
            "restaurant_name": restaurant.name,
            "availability_status": status,
            "current_capacity_percentage": round(capacity_percentage, 1),
            "estimated_wait_minutes": estimated_wait,
            "accepting_orders": capacity_percentage < 95,
            "last_updated": time.time(),
            "cache_ttl": cache_config.ttl_config.RESTAURANT_CAPACITY_TTL
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get restaurant availability")

@router.get("/dynamic-pricing/{restaurant_id}")
@session_cache(
    namespace=CacheNamespace.REALTIME_PRICING,
    key_builder=lambda restaurant_id, *args, **kwargs: f"pricing:restaurant:{restaurant_id}"
)
@log_cache_performance("get_dynamic_pricing")
async def get_dynamic_pricing(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get dynamic pricing information (2-minute cache)"""
    try:
        restaurant = await RestaurantCRUD.get_restaurant(db, restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        # Simulate dynamic pricing calculation
        base_delivery_fee = 2.99
        surge_multiplier = 1.0

        # Simulate surge pricing based on demand
        current_hour = int(time.strftime("%H"))
        if 11 <= current_hour <= 13 or 18 <= current_hour <= 20:  # Peak hours
            surge_multiplier = random.uniform(1.2, 1.8)
        elif 13 <= current_hour <= 17:  # Moderate hours
            surge_multiplier = random.uniform(1.0, 1.3)
        else:  # Off-peak hours
            surge_multiplier = random.uniform(0.8, 1.1)

        dynamic_delivery_fee = round(base_delivery_fee * surge_multiplier, 2)

        # Service fee calculation
        service_fee_percentage = 0.15 if surge_multiplier > 1.5 else 0.12

        return {
            "restaurant_id": restaurant_id,
            "restaurant_name": restaurant.name,
            "pricing": {
                "base_delivery_fee": base_delivery_fee,
                "current_delivery_fee": dynamic_delivery_fee,
                "surge_multiplier": round(surge_multiplier, 2),
                "service_fee_percentage": service_fee_percentage,
                "is_surge_pricing": surge_multiplier > 1.1
            },
            "demand_level": "high" if surge_multiplier > 1.5 else "medium" if surge_multiplier > 1.1 else "low",
            "last_updated": time.time(),
            "cache_ttl": cache_config.ttl_config.DYNAMIC_PRICING_TTL
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get dynamic pricing")

@router.get("/order-tracking/{order_id}")
@conditional_cache(
    namespace=CacheNamespace.ORDER_TRACKING,
    condition=lambda result: result.get("status") in ["confirmed", "preparing", "out_for_delivery"],
    expire=cache_config.ttl_config.DELIVERY_TRACKING_TTL
)
@log_cache_performance("get_order_tracking")
async def get_order_tracking(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get real-time order tracking information (conditional caching based on status)"""
    try:
        # Get order details
        order = await OrderCRUD.get_order(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Simulate real-time tracking data
        tracking_stages = [
            {"stage": "placed", "completed": True, "timestamp": time.time() - 1800},
            {"stage": "confirmed", "completed": True, "timestamp": time.time() - 1500},
            {"stage": "preparing", "completed": order.status != "pending", "timestamp": time.time() - 900 if order.status != "pending" else None},
            {"stage": "ready", "completed": order.status in ["ready", "out_for_delivery", "delivered"], "timestamp": time.time() - 300 if order.status in ["ready", "out_for_delivery", "delivered"] else None},
            {"stage": "out_for_delivery", "completed": order.status in ["out_for_delivery", "delivered"], "timestamp": time.time() - 180 if order.status in ["out_for_delivery", "delivered"] else None},
            {"stage": "delivered", "completed": order.status == "delivered", "timestamp": time.time() if order.status == "delivered" else None}
        ]

        # Estimate delivery time
        if order.status == "delivered":
            estimated_delivery = "Delivered"
        elif order.status == "out_for_delivery":
            estimated_delivery = f"{random.randint(5, 15)} minutes"
        elif order.status in ["preparing", "ready"]:
            estimated_delivery = f"{random.randint(15, 35)} minutes"
        else:
            estimated_delivery = f"{random.randint(25, 45)} minutes"

        return {
            "order_id": order_id,
            "status": order.status,
            "tracking_stages": tracking_stages,
            "estimated_delivery": estimated_delivery,
            "last_updated": time.time(),
            "cache_info": {
                "cached": order.status in ["confirmed", "preparing", "out_for_delivery"],
                "ttl": cache_config.ttl_config.DELIVERY_TRACKING_TTL if order.status in ["confirmed", "preparing", "out_for_delivery"] else 0
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get order tracking")

@router.get("/notifications/{customer_id}")
@session_cache(
    namespace=CacheNamespace.REALTIME_NOTIFICATIONS,
    key_builder=lambda customer_id, *args, **kwargs: f"notifications:customer:{customer_id}"
)
@log_cache_performance("get_customer_notifications")
async def get_customer_notifications(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get real-time notifications for a customer (60-second cache)"""
    try:
        # Simulate real-time notifications
        notifications = [
            {
                "id": 1,
                "type": "order_update",
                "title": "Order Confirmed",
                "message": "Your order from Pizza Palace has been confirmed",
                "timestamp": time.time() - 300,
                "read": False
            },
            {
                "id": 2,
                "type": "promotion",
                "title": "Special Offer",
                "message": "20% off on your next order from Burger King",
                "timestamp": time.time() - 1800,
                "read": True
            },
            {
                "id": 3,
                "type": "delivery_update",
                "title": "Out for Delivery",
                "message": "Your order is on the way! Estimated delivery: 15 minutes",
                "timestamp": time.time() - 600,
                "read": False
            }
        ]

        # Add random new notifications
        if random.random() > 0.7:  # 30% chance of new notification
            notifications.insert(0, {
                "id": random.randint(100, 999),
                "type": "system",
                "title": "System Update",
                "message": "New restaurants added in your area",
                "timestamp": time.time(),
                "read": False
            })

        unread_count = sum(1 for n in notifications if not n["read"])

        return {
            "customer_id": customer_id,
            "notifications": notifications,
            "unread_count": unread_count,
            "last_updated": time.time(),
            "cache_ttl": cache_config.ttl_config.REALTIME_DATA_TTL
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get notifications")