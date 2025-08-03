from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database import get_db
from schemas import (
    Customer, CustomerCreate, CustomerUpdate, CustomerList,
    OrderList, CustomerAnalytics
)
from crud import CustomerCRUD, OrderCRUD, AnalyticsCRUD

router = APIRouter(prefix="/customers", tags=["customers"])

@router.post("/", response_model=Customer, status_code=201)
async def create_customer(
    customer: CustomerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new customer"""
    try:
        return await CustomerCRUD.create_customer(db, customer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=CustomerList)
async def get_customers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    active_only: bool = Query(False, description="Filter only active customers"),
    db: AsyncSession = Depends(get_db)
):
    """Get all customers with pagination"""
    try:
        customers, total = await CustomerCRUD.get_customers(db, skip, limit, active_only)
        return CustomerList(
            customers=customers,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{customer_id}", response_model=Customer)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific customer by ID"""
    try:
        customer = await CustomerCRUD.get_customer(db, customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{customer_id}", response_model=Customer)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a customer"""
    try:
        customer = await CustomerCRUD.update_customer(db, customer_id, customer_update)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a customer"""
    try:
        success = await CustomerCRUD.delete_customer(db, customer_id)
        if not success:
            raise HTTPException(status_code=404, detail="Customer not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{customer_id}/orders", response_model=OrderList)
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

@router.get("/{customer_id}/analytics", response_model=CustomerAnalytics)
async def get_customer_analytics(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for a customer"""
    try:
        # Check if customer exists
        customer = await CustomerCRUD.get_customer(db, customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        analytics = await AnalyticsCRUD.get_customer_analytics(db, customer_id)
        return CustomerAnalytics(**analytics)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
