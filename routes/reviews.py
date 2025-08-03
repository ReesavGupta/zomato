from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database import get_db
from schemas import Review, ReviewCreate, ReviewList, RestaurantAnalytics
from crud import ReviewCRUD, OrderCRUD, CustomerCRUD, RestaurantCRUD, AnalyticsCRUD

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/orders/{order_id}/review", response_model=Review, status_code=201)
async def create_review(
    order_id: int,
    review: ReviewCreate,
    customer_id: int = Query(..., description="Customer ID creating the review"),
    db: AsyncSession = Depends(get_db)
):
    """Add a review for a completed order"""
    try:
        return await ReviewCRUD.create_review(db, review, customer_id, order_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/restaurants/{restaurant_id}/reviews", response_model=ReviewList)
async def get_restaurant_reviews(
    restaurant_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all reviews for a restaurant"""
    try:
        # Check if restaurant exists
        restaurant = await RestaurantCRUD.get_restaurant(db, restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        reviews, total = await ReviewCRUD.get_restaurant_reviews(db, restaurant_id, skip, limit)
        return ReviewList(
            reviews=reviews,
            total=total,
            skip=skip,
            limit=limit
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/customers/{customer_id}/reviews", response_model=ReviewList)
async def get_customer_reviews(
    customer_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all reviews by a customer"""
    try:
        # Check if customer exists
        customer = await CustomerCRUD.get_customer(db, customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        reviews, total = await ReviewCRUD.get_customer_reviews(db, customer_id, skip, limit)
        return ReviewList(
            reviews=reviews,
            total=total,
            skip=skip,
            limit=limit
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/restaurants/{restaurant_id}/analytics", response_model=RestaurantAnalytics)
async def get_restaurant_analytics(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive analytics for a restaurant"""
    try:
        # Check if restaurant exists
        restaurant = await RestaurantCRUD.get_restaurant(db, restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        analytics = await AnalyticsCRUD.get_restaurant_analytics(db, restaurant_id)
        return RestaurantAnalytics(**analytics)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
