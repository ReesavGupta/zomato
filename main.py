from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
import redis.asyncio as redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import time
from database import create_tables
from routes.restaurants import router as restaurant_router
from routes.menu_items import router as menu_item_router
from routes.customers import router as customer_router
from routes.orders import router as order_router
from routes.reviews import router as review_router
from routes.cache import router as cache_router
from routes.demo import router as demo_router
from routes.realtime import router as realtime_router
from routes.analytics import router as analytics_router

# Performance monitoring middleware
class PerformanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Add performance headers
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        response.headers["X-Cache-Status"] = "HIT" if process_time < 10 else "MISS"

        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables and initialize Redis cache
    await create_tables()

    # Initialize Redis connection with error handling
    try:
        redis_client = redis.from_url("redis://localhost:6379", encoding="utf8", decode_responses=True)
        # Test Redis connection
        await redis_client.ping()
        FastAPICache.init(RedisBackend(redis_client), prefix="zomato-cache")
        print("✅ Redis cache initialized successfully")
        print("🚀 Application ready with Redis caching enabled")
    except Exception as e:
        print(f"⚠️  Redis connection failed: {e}")
        print("⚠️  Application will run without caching. Please ensure Redis server is running.")
        print("💡 To install Redis:")
        print("   - Windows: choco install redis-64")
        print("   - macOS: brew install redis && brew services start redis")
        print("   - Linux: sudo apt install redis-server && sudo systemctl start redis-server")
        print("🚀 Application ready without caching")
        # Initialize with a dummy backend or skip cache initialization
        redis_client = None

    # Background cache warming
    try:
        from utils.cache_manager import CacheWarmer
        from database import get_db

        # Get database session for cache warming
        async for db in get_db():
            warming_stats = await CacheWarmer.warm_popular_data(db)
            if "error" not in warming_stats:
                print(f"🔥 Cache warming completed: {warming_stats}")
            break
    except Exception as e:
        print(f"⚠️  Cache warming failed: {e}")

    # Start background cache maintenance tasks
    try:
        from utils.background_tasks import background_cache_manager
        await background_cache_manager.start_background_tasks()
        print("🔄 Background cache maintenance tasks started")
    except Exception as e:
        print(f"⚠️  Background tasks failed to start: {e}")

    yield

    # Shutdown: Clean up resources
    try:
        from utils.background_tasks import background_cache_manager
        await background_cache_manager.stop_background_tasks()
        print("🛑 Background cache tasks stopped")
    except Exception as e:
        print(f"⚠️  Background tasks cleanup failed: {e}")

    if redis_client:
        await redis_client.close()

# Create FastAPI application
app = FastAPI(
    title="Zomato Food Delivery Ecosystem API with Redis Cache",
    description="A complete food delivery platform with restaurants, menus, customers, orders, reviews, and Redis caching for improved performance",
    version="3.1.0",
    lifespan=lifespan
)

# Add performance monitoring middleware
app.add_middleware(PerformanceMiddleware)

# Include routers
app.include_router(restaurant_router)
app.include_router(menu_item_router)
app.include_router(customer_router)
app.include_router(order_router)
app.include_router(review_router)
app.include_router(cache_router)
app.include_router(demo_router)
app.include_router(realtime_router)
app.include_router(analytics_router)

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to Zomato Food Delivery Ecosystem API with Redis Cache",
        "version": "3.1.0",
        "features": [
            "Restaurant Management",
            "Menu Management",
            "Customer Management",
            "Order Processing",
            "Review System",
            "Analytics & Reporting",
            "Complex Multi-table Relationships",
            "Redis Caching for Performance",
            "Cache Management & Statistics",
            "Performance Testing Tools"
        ],
        "cache_info": {
            "backend": "Redis",
            "cache_stats": "/cache/stats",
            "cache_management": "/cache/clear",
            "performance_demo": "/demo/cache-performance-test"
        },
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
