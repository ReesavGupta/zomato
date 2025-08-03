from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import RestaurantCreate, MenuItemCreate
from crud import RestaurantCRUD, MenuItemCRUD
from utils.cache_manager import CacheInvalidator

router = APIRouter(prefix="/demo", tags=["demo"])

@router.post("/sample-data")
async def create_sample_data(db: AsyncSession = Depends(get_db)):
    """Create sample restaurants and menu items for testing cache performance"""
    try:
        sample_restaurants = [
            {
                "name": "Pizza Palace",
                "description": "Authentic Italian pizza with fresh ingredients",
                "cuisine_type": "Italian",
                "address": "123 Main St, Downtown",
                "phone_number": "+1-555-0123",
                "rating": 4.5,
                "opening_time": "10:00:00",
                "closing_time": "22:00:00"
            },
            {
                "name": "Burger Barn",
                "description": "Gourmet burgers and craft beer",
                "cuisine_type": "American",
                "address": "456 Oak Ave, Midtown",
                "phone_number": "+1-555-0456",
                "rating": 4.2,
                "opening_time": "11:00:00",
                "closing_time": "23:00:00"
            },
            {
                "name": "Sushi Zen",
                "description": "Fresh sushi and Japanese cuisine",
                "cuisine_type": "Japanese",
                "address": "789 Pine Rd, Uptown",
                "phone_number": "+1-555-0789",
                "rating": 4.8,
                "opening_time": "17:00:00",
                "closing_time": "22:30:00"
            },
            {
                "name": "Taco Fiesta",
                "description": "Authentic Mexican street food",
                "cuisine_type": "Mexican",
                "address": "321 Elm St, Southside",
                "phone_number": "+1-555-0321",
                "rating": 4.3,
                "opening_time": "09:00:00",
                "closing_time": "21:00:00"
            },
            {
                "name": "Curry House",
                "description": "Traditional Indian curries and tandoor",
                "cuisine_type": "Indian",
                "address": "654 Maple Dr, Eastside",
                "phone_number": "+1-555-0654",
                "rating": 4.6,
                "opening_time": "12:00:00",
                "closing_time": "22:00:00"
            }
        ]
        
        created_restaurants = []
        
        # Create restaurants
        for restaurant_data in sample_restaurants:
            restaurant_create = RestaurantCreate(**restaurant_data)
            restaurant = await RestaurantCRUD.create_restaurant(db, restaurant_create)
            created_restaurants.append(restaurant)
        
        # Create sample menu items for each restaurant
        sample_menu_items = {
            "Pizza Palace": [
                {"name": "Margherita Pizza", "description": "Classic tomato, mozzarella, basil", "price": 12.99, "category": "Main Course", "is_vegetarian": True, "preparation_time": 15},
                {"name": "Pepperoni Pizza", "description": "Pepperoni with mozzarella cheese", "price": 14.99, "category": "Main Course", "preparation_time": 15},
                {"name": "Caesar Salad", "description": "Fresh romaine with caesar dressing", "price": 8.99, "category": "Appetizer", "is_vegetarian": True, "preparation_time": 5}
            ],
            "Burger Barn": [
                {"name": "Classic Burger", "description": "Beef patty with lettuce, tomato, onion", "price": 11.99, "category": "Main Course", "preparation_time": 12},
                {"name": "Veggie Burger", "description": "Plant-based patty with avocado", "price": 12.99, "category": "Main Course", "is_vegetarian": True, "is_vegan": True, "preparation_time": 12},
                {"name": "Sweet Potato Fries", "description": "Crispy sweet potato fries", "price": 6.99, "category": "Side", "is_vegetarian": True, "preparation_time": 8}
            ],
            "Sushi Zen": [
                {"name": "Salmon Roll", "description": "Fresh salmon with avocado", "price": 8.99, "category": "Main Course", "preparation_time": 10},
                {"name": "Vegetable Roll", "description": "Cucumber, avocado, carrot", "price": 6.99, "category": "Main Course", "is_vegetarian": True, "preparation_time": 8},
                {"name": "Miso Soup", "description": "Traditional soybean soup", "price": 3.99, "category": "Appetizer", "is_vegetarian": True, "preparation_time": 3}
            ],
            "Taco Fiesta": [
                {"name": "Beef Tacos", "description": "Seasoned ground beef with salsa", "price": 9.99, "category": "Main Course", "preparation_time": 8},
                {"name": "Chicken Quesadilla", "description": "Grilled chicken with cheese", "price": 10.99, "category": "Main Course", "preparation_time": 10},
                {"name": "Guacamole", "description": "Fresh avocado dip with chips", "price": 5.99, "category": "Appetizer", "is_vegetarian": True, "preparation_time": 5}
            ],
            "Curry House": [
                {"name": "Chicken Tikka Masala", "description": "Creamy tomato curry with chicken", "price": 13.99, "category": "Main Course", "preparation_time": 20},
                {"name": "Vegetable Biryani", "description": "Fragrant rice with mixed vegetables", "price": 11.99, "category": "Main Course", "is_vegetarian": True, "preparation_time": 25},
                {"name": "Naan Bread", "description": "Traditional Indian flatbread", "price": 3.99, "category": "Side", "is_vegetarian": True, "preparation_time": 5}
            ]
        }
        
        created_menu_items = []
        
        # Create menu items for each restaurant
        for restaurant in created_restaurants:
            if restaurant.name in sample_menu_items:
                for menu_item_data in sample_menu_items[restaurant.name]:
                    menu_item_create = MenuItemCreate(**menu_item_data)
                    menu_item = await MenuItemCRUD.create_menu_item(db, menu_item_create, restaurant.id)
                    created_menu_items.append(menu_item)
        
        # Clear cache after creating sample data
        await CacheInvalidator.invalidate_restaurant_caches()
        
        return {
            "status": "success",
            "message": "Sample data created successfully",
            "created": {
                "restaurants": len(created_restaurants),
                "menu_items": len(created_menu_items)
            },
            "restaurants": [
                {
                    "id": r.id,
                    "name": r.name,
                    "cuisine_type": r.cuisine_type,
                    "rating": float(r.rating)
                } for r in created_restaurants
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create sample data: {str(e)}")

@router.delete("/sample-data")
async def clear_sample_data(db: AsyncSession = Depends(get_db)):
    """Clear all sample data (restaurants and menu items)"""
    try:
        # Get all restaurants
        restaurants, _ = await RestaurantCRUD.get_restaurants(db, skip=0, limit=1000)
        
        deleted_count = 0
        for restaurant in restaurants:
            success = await RestaurantCRUD.delete_restaurant(db, restaurant.id)
            if success:
                deleted_count += 1
        
        # Clear all caches
        await CacheInvalidator.invalidate_restaurant_caches()
        
        return {
            "status": "success",
            "message": f"Deleted {deleted_count} restaurants and their menu items",
            "deleted_restaurants": deleted_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear sample data: {str(e)}")

@router.get("/cache-performance-test")
async def cache_performance_test(db: AsyncSession = Depends(get_db)):
    """Run a comprehensive cache performance test"""
    try:
        import time
        
        # Test 1: Restaurant list performance
        start_time = time.time()
        restaurants_first, _ = await RestaurantCRUD.get_restaurants(db, skip=0, limit=10)
        first_request_time = (time.time() - start_time) * 1000
        
        start_time = time.time()
        restaurants_second, _ = await RestaurantCRUD.get_restaurants(db, skip=0, limit=10)
        second_request_time = (time.time() - start_time) * 1000
        
        # Test 2: Individual restaurant performance (if restaurants exist)
        individual_test = None
        if restaurants_first:
            restaurant_id = restaurants_first[0].id
            
            start_time = time.time()
            restaurant_first = await RestaurantCRUD.get_restaurant(db, restaurant_id)
            individual_first_time = (time.time() - start_time) * 1000
            
            start_time = time.time()
            restaurant_second = await RestaurantCRUD.get_restaurant(db, restaurant_id)
            individual_second_time = (time.time() - start_time) * 1000
            
            individual_test = {
                "restaurant_id": restaurant_id,
                "first_request_ms": round(individual_first_time, 2),
                "second_request_ms": round(individual_second_time, 2),
                "improvement": f"{round((individual_first_time - individual_second_time) / individual_first_time * 100, 2)}%" if individual_first_time > 0 else "0%"
            }
        
        return {
            "status": "success",
            "performance_tests": {
                "restaurant_list": {
                    "first_request_ms": round(first_request_time, 2),
                    "second_request_ms": round(second_request_time, 2),
                    "improvement": f"{round((first_request_time - second_request_time) / first_request_time * 100, 2)}%" if first_request_time > 0 else "0%",
                    "restaurants_found": len(restaurants_first)
                },
                "individual_restaurant": individual_test
            },
            "cache_recommendations": {
                "cache_hit_threshold": "< 10ms response time",
                "cache_miss_expected": "> 50ms response time",
                "optimal_performance": "90%+ improvement on cache hits"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance test failed: {str(e)}")
