from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from database import get_db
from schemas import (
    Order, OrderCreate, OrderWithDetails, OrderStatusUpdate,
    OrderList, OrderStatusEnum
)
from crud import OrderCRUD, CustomerCRUD, RestaurantCRUD
from models import OrderStatus

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/customers/{customer_id}/orders/", response_model=Order, status_code=201)
async def place_order(
    customer_id: int,
    order: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Place a new order for a customer"""
    try:
        return await OrderCRUD.create_order(db, order, customer_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{order_id}", response_model=OrderWithDetails)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get order with full details"""
    try:
        order = await OrderCRUD.get_order_with_details(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{order_id}/status", response_model=Order)
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update order status"""
    try:
        order = await OrderCRUD.update_order_status(db, order_id, status_update)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/customers/{customer_id}/orders", response_model=OrderList)
async def get_customer_orders(
    customer_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get order history for a customer"""
    try:
        # Check if customer exists
        customer = await CustomerCRUD.get_customer(db, customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        orders, total = await OrderCRUD.get_customer_orders(db, customer_id, skip, limit)
        return OrderList(
            orders=orders,
            total=total,
            skip=skip,
            limit=limit
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/restaurants/{restaurant_id}/orders", response_model=OrderList)
async def get_restaurant_orders(
    restaurant_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    status: Optional[OrderStatusEnum] = Query(None, description="Filter by order status"),
    db: AsyncSession = Depends(get_db)
):
    """Get orders for a restaurant"""
    try:
        # Check if restaurant exists
        restaurant = await RestaurantCRUD.get_restaurant(db, restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        # Convert enum to model enum if provided
        status_filter = None
        if status:
            status_filter = OrderStatus(status.value)
        
        orders, total = await OrderCRUD.get_restaurant_orders(db, restaurant_id, skip, limit, status_filter)
        return OrderList(
            orders=orders,
            total=total,
            skip=skip,
            limit=limit
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
