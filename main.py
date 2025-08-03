from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import create_tables
from routes.restaurants import router as restaurant_router
from routes.menu_items import router as menu_item_router
from routes.customers import router as customer_router
from routes.orders import router as order_router
from routes.reviews import router as review_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    await create_tables()
    yield
    # Shutdown: Clean up resources if needed
    pass

# Create FastAPI application
app = FastAPI(
    title="Zomato Food Delivery Ecosystem API",
    description="A complete food delivery platform with restaurants, menus, customers, orders, and reviews",
    version="3.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(restaurant_router)
app.include_router(menu_item_router)
app.include_router(customer_router)
app.include_router(order_router)
app.include_router(review_router)

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to Zomato Food Delivery Ecosystem API",
        "version": "3.0.0",
        "features": [
            "Restaurant Management",
            "Menu Management",
            "Customer Management",
            "Order Processing",
            "Review System",
            "Analytics & Reporting",
            "Complex Multi-table Relationships"
        ],
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "zomato-food-delivery-ecosystem"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
