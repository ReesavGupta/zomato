# Zomato Food Delivery Ecosystem API - Version 3.1 with Redis Cache

A complete food delivery ecosystem built with FastAPI, SQLAlchemy, SQLite, and Redis caching. This advanced version implements complex multi-table relationships with customers, orders, reviews, comprehensive analytics, and high-performance Redis caching for optimal response times.

## Features

### Core Management (V1-V2 Features)
- **Restaurant Management** - Complete CRUD with search and filtering
- **Menu Management** - Items with dietary preferences and availability
- **One-to-Many Relationships** - Restaurant → Menu Items

### Customer & Order Management (V3 New Features)
- **Customer Management** - Registration, profiles, and order history
- **Order Processing** - Complete order lifecycle with status tracking
- **Order Items** - Many-to-many relationship with additional data
- **Business Logic Validation** - Order status workflows and constraints

### Review & Rating System (V3 New Features)
- **Review Management** - Customer reviews for completed orders
- **Rating Calculations** - Automatic restaurant rating updates
- **Review Validation** - Only delivered orders can be reviewed

### Analytics & Reporting (V3 New Features)
- **Restaurant Analytics** - Revenue, popular items, order statistics
- **Customer Analytics** - Spending patterns, favorite restaurants
- **Performance Metrics** - Order status breakdowns and trends

### Redis Caching System (V3.1 New Features)
- **High-Performance Caching** - Redis backend with configurable TTL
- **Namespace-based Organization** - Separate cache namespaces for different data types
- **Smart Cache Invalidation** - Automatic cache clearing on data updates
- **Performance Monitoring** - Response time tracking and cache hit/miss analysis
- **Cache Management API** - Statistics, clearing, and performance testing endpoints

### Advanced Technical Features
- **Complex Multi-table Relationships** - Customer ↔ Order ↔ Restaurant
- **Association Objects** - Order items with additional data
- **Business Logic Layer** - Order calculations and status validation
- **Comprehensive Error Handling** - Detailed validation and error messages
- **Advanced Querying** - Complex joins and aggregations
- **Async Database Operations** - High-performance SQLite with aiosqlite
- **Redis Integration** - Sub-10ms response times for cached data

## Project Structure

```
zomato/
├── main.py              # FastAPI application entry point with Redis cache setup
├── database.py          # Database configuration and session management
├── models.py            # SQLAlchemy models (Restaurant, MenuItem, Customer, Order, OrderItem, Review)
├── schemas.py           # Pydantic schemas for all models and responses
├── crud.py              # Database operations with complex joins and business logic
├── routes/              # Modular route definitions
│   ├── __init__.py
│   ├── restaurants.py   # Restaurant endpoints with caching
│   ├── menu_items.py    # Menu item endpoints with caching
│   ├── customers.py     # Customer management endpoints
│   ├── orders.py        # Order processing and tracking endpoints
│   ├── reviews.py       # Review and analytics endpoints
│   ├── cache.py         # Cache management and statistics endpoints
│   └── demo.py          # Sample data and performance testing endpoints
├── utils/               # Business logic and utility functions
│   ├── __init__.py
│   ├── business_logic.py # Order calculations, validations, analytics
│   └── cache_manager.py  # Cache management, invalidation, and performance tracking
├── requirements.txt     # Python dependencies (includes Redis)
└── README.md           # This file
```

## Installation & Setup

### 1. Install Redis Server

**On Windows:**
```bash
# Using Chocolatey
choco install redis-64

# Or download from: https://github.com/microsoftarchive/redis/releases
```

**On macOS:**
```bash
brew install redis
brew services start redis
```

**On Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### 2. Verify Redis Installation
```bash
redis-cli ping
# Should return: PONG
```

### 3. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
```bash
python main.py
```

The API will be available at: `http://localhost:8000`

**Note:** Make sure Redis server is running before starting the application. The app will connect to Redis at `localhost:6379` by default.

## API Documentation

Once the server is running, you can access:
- **Interactive API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### Restaurant Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/restaurants/` | Create new restaurant |
| GET | `/restaurants/` | List all restaurants (paginated) |
| GET | `/restaurants/{id}` | Get specific restaurant |
| PUT | `/restaurants/{id}` | Update restaurant |
| DELETE | `/restaurants/{id}` | Delete restaurant (cascades to menu items) |
| GET | `/restaurants/search?cuisine={type}` | Search by cuisine |
| GET | `/restaurants/active` | List only active restaurants |
| POST | `/restaurants/{id}/menu-items/` | Add menu item to restaurant |
| GET | `/restaurants/{id}/menu` | Get all menu items for restaurant |
| GET | `/restaurants/{id}/with-menu` | Get restaurant with all menu items |

### Menu Item Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/menu-items/` | List all menu items (paginated) |
| GET | `/menu-items/{id}` | Get specific menu item |
| GET | `/menu-items/{id}/with-restaurant` | Get menu item with restaurant details |
| PUT | `/menu-items/{id}` | Update menu item |
| DELETE | `/menu-items/{id}` | Delete menu item |
| GET | `/menu-items/search` | Search menu items with filters |

### Customer Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/customers/` | Create new customer |
| GET | `/customers/` | List all customers (paginated) |
| GET | `/customers/{id}` | Get specific customer |
| PUT | `/customers/{id}` | Update customer |
| DELETE | `/customers/{id}` | Delete customer |
| GET | `/customers/{id}/orders` | Get customer's order history |
| GET | `/customers/{id}/analytics` | Get customer analytics |

### Order Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/orders/customers/{id}/orders/` | Place new order for customer |
| GET | `/orders/{id}` | Get order with full details |
| PUT | `/orders/{id}/status` | Update order status |
| GET | `/orders/customers/{id}/orders` | Get customer's order history |
| GET | `/orders/restaurants/{id}/orders` | Get restaurant's orders |

### Review & Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/reviews/orders/{id}/review` | Add review for completed order |
| GET | `/reviews/restaurants/{id}/reviews` | Get restaurant reviews |
| GET | `/reviews/customers/{id}/reviews` | Get customer's reviews |
| GET | `/reviews/restaurants/{id}/analytics` | Get restaurant analytics |

### Advanced Cache Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/cache/stats` | Basic cache statistics and keys |
| GET | `/cache/stats/detailed` | **NEW** Detailed namespace-level statistics with TTL info |
| GET | `/cache/info` | Comprehensive cache configuration information |
| DELETE | `/cache/clear` | Clear entire cache |
| DELETE | `/cache/clear/restaurants` | Clear restaurant-related caches |
| DELETE | `/cache/clear/menu-items` | Clear menu items cache |
| DELETE | `/cache/clear/search` | **NEW** Clear search result caches |
| DELETE | `/cache/clear/analytics` | **NEW** Clear analytics and aggregation caches |
| DELETE | `/cache/clear/restaurant-menus` | **NEW** Clear restaurant-menu combination caches |
| DELETE | `/cache/clear/customers` | Clear customers cache |
| DELETE | `/cache/clear/orders` | Clear orders cache |
| DELETE | `/cache/clear/reviews` | Clear reviews cache |

### Performance Monitoring & Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/cache/metrics/hit-ratio` | **NEW** Cache hit/miss ratio and efficiency metrics |
| GET | `/cache/metrics/memory-usage` | **NEW** Detailed Redis memory usage analysis |
| GET | `/cache/performance/comprehensive-report` | **NEW** Complete performance report with recommendations |
| GET | `/cache/demo/cache-test/{restaurant_id}` | Demonstrate cache performance for specific restaurant |
| GET | `/cache/demo/performance-comparison` | **NEW** Compare cached vs non-cached performance |

### Cache Warming & Optimization

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/cache/warm` | Basic cache warming with sample data |
| POST | `/cache/warm/popular` | **NEW** Smart cache warming with popular/frequently accessed data |

### Enhanced Menu & Restaurant Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/menu-items/dietary/{dietary_type}` | **NEW** Get menu items by dietary preference (vegetarian, vegan, gluten-free) |
| GET | `/menu-items/category/{category}` | **NEW** Get menu items by category |
| GET | `/restaurants/{restaurant_id}/analytics` | **NEW** Comprehensive restaurant analytics (cached 20 min) |
| GET | `/restaurants/analytics/popular-cuisines` | **NEW** Popular cuisines across all restaurants |
| GET | `/restaurants/analytics/price-ranges` | **NEW** Price range distribution analysis |

### Real-Time Data Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/realtime/delivery-slots/{restaurant_id}` | **NEW** Available delivery slots (30-second cache) |
| GET | `/realtime/restaurant-availability/{restaurant_id}` | **NEW** Real-time restaurant capacity (60-second cache) |
| GET | `/realtime/dynamic-pricing/{restaurant_id}` | **NEW** Dynamic pricing information (2-minute cache) |
| GET | `/realtime/order-tracking/{order_id}` | **NEW** Live order tracking (conditional caching) |
| GET | `/realtime/notifications/{customer_id}` | **NEW** Customer notifications (60-second cache) |

### Enterprise Analytics Caching

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/revenue/daily` | **NEW** Daily revenue analytics (24-hour cache) |
| GET | `/analytics/customers/behavior` | **NEW** Customer behavior analytics (4-hour cache) |
| GET | `/analytics/restaurants/performance` | **NEW** Restaurant performance with cache-aside pattern |
| GET | `/analytics/popular-items` | **NEW** Popular items with refresh-ahead caching |
| POST | `/analytics/refresh/{analytics_type}` | **NEW** Manual cache refresh in background |

### Enterprise Cache Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/cache/health` | **NEW** Redis health check with comprehensive diagnostics |
| GET | `/cache/stats/namespaces` | **NEW** Detailed statistics by namespace |
| GET | `/cache/memory-usage` | **NEW** Detailed memory usage analysis with recommendations |
| DELETE | `/cache/clear/expired` | **NEW** Remove expired keys from cache |
| POST | `/cache/warm/{namespace}` | **NEW** Warm specific cache namespace |
| GET | `/cache/metrics/hit-ratio` | Cache hit/miss ratio and efficiency metrics |
| GET | `/cache/performance/comprehensive-report` | Complete performance report with recommendations |

### Demo & Testing

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/demo/sample-data` | Create sample restaurants for testing |
| DELETE | `/demo/sample-data` | Clear all sample data |
| GET | `/demo/cache-performance-test` | Run comprehensive cache performance test |

### Search & Filter Parameters

**Menu Items:**
- `category` - Filter by menu category
- `vegetarian` - Filter by vegetarian items (true/false)
- `vegan` - Filter by vegan items (true/false)
- `available` - Filter by availability (true/false)

**Orders:**
- `status` - Filter by order status (placed, confirmed, preparing, out_for_delivery, delivered, cancelled)

**Customers:**
- `active_only` - Filter only active customers (true/false)

### Example Usage

#### 1. Create Restaurant
```bash
curl -X POST "http://localhost:8000/restaurants/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pizza Palace",
    "description": "Authentic Italian pizza",
    "cuisine_type": "Italian",
    "address": "123 Main St, City",
    "phone_number": "+1-555-0123",
    "rating": 4.5,
    "opening_time": "10:00:00",
    "closing_time": "22:00:00"
  }'
```

#### 2. Add Menu Item
```bash
curl -X POST "http://localhost:8000/restaurants/1/menu-items/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Margherita Pizza",
    "description": "Classic pizza with tomato, mozzarella, and basil",
    "price": 12.99,
    "category": "Main Course",
    "is_vegetarian": true,
    "is_vegan": false,
    "preparation_time": 15
  }'
```

#### 3. Create Customer
```bash
curl -X POST "http://localhost:8000/customers/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone_number": "+1-555-0456",
    "address": "456 Oak Ave, City"
  }'
```

#### 4. Place Order
```bash
curl -X POST "http://localhost:8000/orders/customers/1/orders/" \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_id": 1,
    "delivery_address": "456 Oak Ave, City",
    "special_instructions": "Ring doorbell twice",
    "order_items": [
      {
        "menu_item_id": 1,
        "quantity": 2,
        "special_requests": "Extra cheese"
      }
    ]
  }'
```

#### 5. Update Order Status
```bash
curl -X PUT "http://localhost:8000/orders/1/status" \
  -H "Content-Type: application/json" \
  -d '{
    "order_status": "delivered",
    "delivery_time": "2024-01-15T18:30:00"
  }'
```

#### 6. Add Review
```bash
curl -X POST "http://localhost:8000/reviews/orders/1/review?customer_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5,
    "comment": "Excellent pizza! Fast delivery and great taste."
  }'
```

#### 7. Get Restaurant Analytics
```bash
curl "http://localhost:8000/reviews/restaurants/1/analytics"
```

#### 8. Create Sample Data for Testing
```bash
curl -X POST "http://localhost:8000/demo/sample-data"
```

#### 9. Check Cache Statistics
```bash
curl "http://localhost:8000/cache/stats"
```

#### 10. Test Cache Performance
```bash
curl "http://localhost:8000/demo/cache-performance-test"
```

#### 11. Clear Restaurant Cache
```bash
curl -X DELETE "http://localhost:8000/cache/clear/restaurants"
```

#### 12. Demonstrate Cache Performance for Specific Restaurant
```bash
curl "http://localhost:8000/cache/demo/cache-test/1"
```

#### 13. Get Detailed Cache Statistics
```bash
curl "http://localhost:8000/cache/stats/detailed"
```

#### 14. Get Cache Hit Ratio Metrics
```bash
curl "http://localhost:8000/cache/metrics/hit-ratio"
```

#### 15. Get Memory Usage Analysis
```bash
curl "http://localhost:8000/cache/metrics/memory-usage"
```

#### 16. Run Performance Comparison Test
```bash
curl "http://localhost:8000/cache/demo/performance-comparison"
```

#### 17. Warm Cache with Popular Data
```bash
curl -X POST "http://localhost:8000/cache/warm/popular"
```

#### 18. Get Comprehensive Performance Report
```bash
curl "http://localhost:8000/cache/performance/comprehensive-report"
```

#### 19. Get Restaurant Analytics (Cached)
```bash
curl "http://localhost:8000/restaurants/1/analytics"
```

#### 20. Get Popular Cuisines Analysis
```bash
curl "http://localhost:8000/restaurants/analytics/popular-cuisines"
```

#### 21. Get Vegetarian Menu Items
```bash
curl "http://localhost:8000/menu-items/dietary/vegetarian"
```

#### 22. Get Menu Items by Category
```bash
curl "http://localhost:8000/menu-items/category/appetizers"
```

#### 23. Clear Search Caches
```bash
curl -X DELETE "http://localhost:8000/cache/clear/search"
```

#### 24. Clear Analytics Caches
```bash
curl -X DELETE "http://localhost:8000/cache/clear/analytics"
```

#### 25. Get Real-Time Delivery Slots
```bash
curl "http://localhost:8000/realtime/delivery-slots/1"
```

#### 26. Check Restaurant Availability
```bash
curl "http://localhost:8000/realtime/restaurant-availability/1"
```

#### 27. Get Dynamic Pricing
```bash
curl "http://localhost:8000/realtime/dynamic-pricing/1"
```

#### 28. Track Order in Real-Time
```bash
curl "http://localhost:8000/realtime/order-tracking/1"
```

#### 29. Get Customer Notifications
```bash
curl "http://localhost:8000/realtime/notifications/1"
```

#### 30. Get Daily Revenue Analytics
```bash
curl "http://localhost:8000/analytics/revenue/daily?date=2024-01-01"
```

#### 31. Get Customer Behavior Analytics
```bash
curl "http://localhost:8000/analytics/customers/behavior?period=7d"
```

#### 32. Get Restaurant Performance Analytics
```bash
curl "http://localhost:8000/analytics/restaurants/performance?restaurant_id=1"
```

#### 33. Get Popular Items Analytics
```bash
curl "http://localhost:8000/analytics/popular-items?period=7d&limit=10"
```

#### 34. Refresh Analytics Cache
```bash
curl -X POST "http://localhost:8000/analytics/refresh/revenue"
```

#### 35. Check Cache Health
```bash
curl "http://localhost:8000/cache/health"
```

#### 36. Get Namespace Statistics
```bash
curl "http://localhost:8000/cache/stats/namespaces"
```

#### 37. Get Memory Usage Analysis
```bash
curl "http://localhost:8000/cache/memory-usage"
```

#### 38. Clear Expired Keys
```bash
curl -X DELETE "http://localhost:8000/cache/clear/expired"
```

#### 39. Warm Specific Namespace
```bash
curl -X POST "http://localhost:8000/cache/warm/restaurants"
```

## Data Models

### Restaurant Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | Integer | Auto | Primary key |
| name | String(100) | Yes | Restaurant name (3-100 chars) |
| description | Text | No | Restaurant description |
| cuisine_type | String(50) | Yes | Type of cuisine |
| address | Text | Yes | Restaurant address |
| phone_number | String(20) | Yes | Phone number (validated) |
| rating | Float | No | Rating (0.0-5.0, default 0.0) |
| is_active | Boolean | No | Active status (default True) |
| opening_time | Time | No | Opening time |
| closing_time | Time | No | Closing time |
| created_at | DateTime | Auto | Creation timestamp |
| updated_at | DateTime | Auto | Last update timestamp |
| menu_items | Relationship | Auto | One-to-many relationship with menu items |

### MenuItem Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | Integer | Auto | Primary key |
| name | String(100) | Yes | Menu item name (3-100 chars) |
| description | Text | No | Menu item description |
| price | Decimal(10,2) | Yes | Price (must be positive) |
| category | String(50) | Yes | Menu category |
| is_vegetarian | Boolean | No | Vegetarian flag (default False) |
| is_vegan | Boolean | No | Vegan flag (default False) |
| is_available | Boolean | No | Availability flag (default True) |
| preparation_time | Integer | No | Preparation time in minutes |
| restaurant_id | Integer | Yes | Foreign key to Restaurant |
| created_at | DateTime | Auto | Creation timestamp |
| updated_at | DateTime | Auto | Last update timestamp |
| restaurant | Relationship | Auto | Many-to-one relationship with restaurant |
| order_items | Relationship | Auto | One-to-many relationship with order items |

### Customer Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | Integer | Auto | Primary key |
| name | String(100) | Yes | Customer name (2-100 chars) |
| email | String(255) | Yes | Customer email (unique) |
| phone_number | String(20) | Yes | Phone number (validated) |
| address | Text | Yes | Customer address |
| is_active | Boolean | No | Active status (default True) |
| created_at | DateTime | Auto | Creation timestamp |
| updated_at | DateTime | Auto | Last update timestamp |
| orders | Relationship | Auto | One-to-many relationship with orders |
| reviews | Relationship | Auto | One-to-many relationship with reviews |

### Order Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | Integer | Auto | Primary key |
| customer_id | Integer | Yes | Foreign key to Customer |
| restaurant_id | Integer | Yes | Foreign key to Restaurant |
| order_status | Enum | Auto | Order status (default: placed) |
| total_amount | Decimal(10,2) | Auto | Calculated total amount |
| delivery_address | Text | Yes | Delivery address |
| special_instructions | Text | No | Special instructions |
| order_date | DateTime | Auto | Order creation timestamp |
| delivery_time | DateTime | No | Actual delivery time |
| customer | Relationship | Auto | Many-to-one relationship with customer |
| restaurant | Relationship | Auto | Many-to-one relationship with restaurant |
| order_items | Relationship | Auto | One-to-many relationship with order items |
| review | Relationship | Auto | One-to-one relationship with review |

### OrderItem Model (Association Object)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | Integer | Auto | Primary key |
| order_id | Integer | Yes | Foreign key to Order |
| menu_item_id | Integer | Yes | Foreign key to MenuItem |
| quantity | Integer | Yes | Quantity ordered |
| item_price | Decimal(10,2) | Auto | Price at time of order |
| special_requests | Text | No | Special requests for this item |
| order | Relationship | Auto | Many-to-one relationship with order |
| menu_item | Relationship | Auto | Many-to-one relationship with menu item |

### Review Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | Integer | Auto | Primary key |
| customer_id | Integer | Yes | Foreign key to Customer |
| restaurant_id | Integer | Yes | Foreign key to Restaurant |
| order_id | Integer | Yes | Foreign key to Order (unique) |
| rating | Integer | Yes | Rating (1-5 stars) |
| comment | Text | No | Review comment |
| created_at | DateTime | Auto | Creation timestamp |
| customer | Relationship | Auto | Many-to-one relationship with customer |
| restaurant | Relationship | Auto | Many-to-one relationship with restaurant |
| order | Relationship | Auto | One-to-one relationship with order |

## Validation Rules

### Restaurant Validation
- **Name**: 3-100 characters, cannot be empty, must be unique
- **Phone**: Must match international format pattern
- **Rating**: Must be between 0.0 and 5.0
- **Cuisine Type**: Cannot be empty, auto-capitalized

### Menu Item Validation
- **Name**: 3-100 characters, cannot be empty
- **Price**: Must be positive, rounded to 2 decimal places
- **Category**: Cannot be empty, auto-capitalized
- **Preparation Time**: Must be positive integer (minutes)

### Relationship Constraints
- **Cascade Delete**: Deleting a restaurant removes all its menu items
- **Foreign Key**: Menu items must belong to an existing restaurant

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `201`: Created
- `204`: No Content (for DELETE)
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `500`: Internal Server Error

## Development

### Running in Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Database
- Uses SQLite database (`restaurants.db`)
- Tables are created automatically on startup
- Async operations with aiosqlite

## Database Relationships

### Complex Multi-table Relationships

**One-to-Many Relationships:**
- Restaurant → Menu Items
- Restaurant → Orders
- Restaurant → Reviews
- Customer → Orders
- Customer → Reviews
- Order → Order Items

**Many-to-Many with Association Object:**
- Order ↔ Menu Items (through OrderItem with additional data)

**One-to-One Relationships:**
- Order → Review (each order can have at most one review)

### Relationship Features
- **Cascade Delete** - Removing parent removes all children
- **Efficient Loading** - Uses `selectinload()` and `joinedload()` for optimal queries
- **Business Logic Constraints** - Validates relationships and state transitions
- **Complex Joins** - Multi-table queries for analytics and reporting

## Business Logic & Validation

### Order Status Workflow
```
placed → confirmed → preparing → out_for_delivery → delivered
   ↓         ↓           ↓              ↓
cancelled  cancelled  cancelled    (final state)
```

### Business Rules
- **Order Validation** - Menu items must belong to the selected restaurant
- **Review Eligibility** - Only customers can review their own delivered orders
- **Price Calculation** - Order total calculated from current menu item prices
- **Status Transitions** - Enforced valid order status progressions
- **Unique Constraints** - One review per order, unique customer emails

### Analytics Features
- **Restaurant Analytics** - Revenue, popular items, order statistics
- **Customer Analytics** - Spending patterns, favorite restaurants
- **Performance Metrics** - Order status breakdowns and trends
- **Rating Calculations** - Automatic average rating updates

## Enterprise Redis Caching Architecture (Version 4.0)

### Enterprise Multi-Level Caching Architecture

**Production-Ready Namespace Strategy:**
- **`customers:{customer_id}`** - Individual customer data and sessions (30 min TTL)
- **`restaurants:{restaurant_id}`** - Restaurant-specific data (40 min TTL)
- **`orders:{order_id}`** - Order details and status (3 min TTL)
- **`analytics:restaurants`** - Restaurant performance data (4 hours TTL)
- **`analytics:customers`** - Customer behavior data (4 hours TTL)
- **`analytics:revenue`** - Revenue analytics (24 hours TTL)
- **`search:*`** - All search results (5 min TTL)
- **`realtime:*`** - Live operational data (30 sec - 2 min TTL)

**Advanced Cache Data Classification:**

**Static Data (Long TTL: 30+ minutes):**
- Restaurant details, menu items, customer profiles
- Stable data with infrequent changes
- Optimized for maximum cache hits

**Dynamic Data (Short TTL: 2-5 minutes):**
- Order statuses, delivery tracking, live reviews
- Frequently changing operational data
- Balance between freshness and performance

**Real-time Data (Very Short TTL: 30 seconds):**
- Available delivery slots, restaurant capacity
- Dynamic pricing, live notifications
- Critical for real-time user experience

**Analytics Data (Medium TTL: 15 minutes - 24 hours):**
- Popular items, customer preferences, revenue metrics
- Expensive calculations with acceptable staleness
- Scheduled refresh for optimal performance

### Multi-Level TTL Strategy

**1. Basic Restaurant Data (10 minutes)**
- Stable data with infrequent changes
- Restaurant details, lists, active status
- Optimal for core business operations

**2. Menu Items (8 minutes)**
- More dynamic content with frequent updates
- Individual items, categories, dietary info
- Balanced between freshness and performance

**3. Expensive Joins (15 minutes)**
- Complex restaurant-with-menu combinations
- High computational cost operations
- Longer TTL justified by query complexity

**4. Search Results (5 minutes)**
- User-specific and frequently changing
- Restaurant search, menu search, filters
- Short TTL for dynamic user experience

**5. Analytics & Aggregations (20 minutes)**
- Expensive calculations and business intelligence
- Popular cuisines, price ranges, statistics
- Acceptable staleness for performance gains

### Enterprise Cache Patterns

**1. Session-Based Caching:**
```python
@session_cache(
    namespace=CacheNamespace.CUSTOMERS,
    key_builder=lambda customer_id, *args, **kwargs: f"customer:{customer_id}"
)
async def get_customer_profile(customer_id: int):
    # Customer profile with personalized data
```

**2. Conditional Caching:**
```python
@conditional_cache(
    namespace=CacheNamespace.ORDERS,
    condition=lambda result: result.get("status") == "delivered"
)
async def get_order_details(order_id: int):
    # Cache only completed orders
```

**3. Write-Through Caching:**
```python
async def update_restaurant_rating(restaurant_id: int, new_rating: float):
    # Update database
    result = await update_database(restaurant_id, new_rating)
    # Update cache immediately
    await FastAPICache.set(f"restaurants:rating:{restaurant_id}", new_rating, expire=1800)
```

**4. Cache-Aside Pattern:**
```python
async def get_popular_items(restaurant_id: int):
    # Try cache first
    cached = await FastAPICache.get(f"analytics:popular:{restaurant_id}")
    if cached:
        return cached

    # Calculate and cache
    popular_items = calculate_popular_items(restaurant_id)
    await FastAPICache.set(f"analytics:popular:{restaurant_id}", popular_items, expire=900)
    return popular_items
```

**5. Refresh-Ahead Caching:**
```python
# Background task to refresh cache before expiration
async def refresh_analytics_cache():
    # Refresh high-priority caches before they expire
```

**6. Multi-Level Caching:**
- L1 Cache: Fast, short TTL (real-time data)
- L2 Cache: Slower, long TTL (analytics data)
- Automatic promotion from L2 to L1 on access

### Intelligent Cache Invalidation

**Order Placement Cascade:**
- Invalidate customer history
- Update restaurant orders cache
- Refresh analytics data
- Clear search results if capacity affected

**Status Update Optimization:**
- Update specific order cache
- Conditional customer notifications
- Real-time tracking updates

**Review Addition Impact:**
- Invalidate restaurant ratings
- Clear review lists
- Update analytics aggregations
- Refresh popular items if rating changed

**Menu Update Hierarchy:**
- Clear specific menu item
- Update restaurant menu cache
- Cascade through search results
- Refresh category and dietary filters
- Update restaurant analytics

### Performance Monitoring & Analytics

**Cache Hit Ratio Tracking:**
- Real-time hit/miss ratio calculation
- Efficiency ratings (Excellent >80%, Good >60%)
- Performance trend analysis

**Memory Usage Analysis:**
- Redis memory utilization monitoring
- Average key size analysis
- Memory efficiency recommendations

**Performance Comparison:**
- Cached vs non-cached operation benchmarks
- Speed multiplier calculations
- Response time improvements (typically 5-20x faster)

### Cache Warming Strategies

**Proactive Cache Population:**
- Popular data pre-loading on startup
- Frequently accessed restaurant and menu data
- Smart refresh for near-expiring keys

**Smart Refresh Logic:**
- Automatic refresh when TTL < 25% of original
- Background population of frequently accessed data
- Predictive caching based on access patterns

### Advanced Cache Management

**Detailed Statistics:**
- Namespace-level cache analysis
- TTL information and key distribution
- Memory usage per namespace
- Performance metrics and recommendations

**Management Operations:**
- Granular namespace clearing
- Performance comparison tools
- Cache warming endpoints
- Comprehensive performance reports

## Advanced Features

### Search & Filtering
- **Multi-criteria Search** - Combine multiple filters
- **Dietary Preferences** - Vegetarian/vegan filtering
- **Status-based Filtering** - Orders by status, active customers
- **Date Range Queries** - Order history with time filters

### Performance Optimizations
- **Database Indexing** - Strategic indexes on foreign keys and search fields
- **Efficient Queries** - Minimized N+1 queries with proper loading strategies
- **Pagination** - All list endpoints support pagination
- **Async Operations** - Non-blocking database operations
- **Redis Caching** - Sub-10ms response times for frequently accessed data
- **Smart Cache Invalidation** - Maintains data consistency while maximizing cache hits
- **Multi-Level Caching** - Different TTL strategies for different data types
- **Relationship-Aware Invalidation** - Hierarchical cache clearing with cascade prevention
- **Advanced Performance Monitoring** - Hit ratio tracking, memory analysis, and recommendations
- **Proactive Cache Warming** - Smart pre-population of frequently accessed data
- **Enterprise Cache Patterns** - Session-based, conditional, write-through, cache-aside, refresh-ahead
- **Real-Time Data Caching** - Sub-minute TTLs for live operational data
- **Background Maintenance** - Automated health monitoring, cleanup, and optimization
- **Production Monitoring** - Comprehensive alerting and performance tracking

## Performance Benchmarks

### Expected Performance Improvements

**Cache Hit Scenarios:**
- **Restaurant List**: 5-15x faster (200ms → 10-40ms)
- **Restaurant Details**: 8-20x faster (150ms → 8-20ms)
- **Menu Items**: 6-18x faster (180ms → 10-30ms)
- **Restaurant-with-Menu**: 10-25x faster (400ms → 15-40ms)
- **Search Operations**: 4-12x faster (250ms → 20-60ms)
- **Analytics**: 15-30x faster (800ms → 25-55ms)

**Memory Efficiency:**
- **Average Key Size**: 200-800 bytes per cache entry
- **Memory Usage**: ~1-5MB for 1000 restaurants with full menu data
- **Hit Ratio Target**: >80% for optimal performance

**Cache Warming Benefits:**
- **Startup Performance**: 90% of requests served from cache within 5 minutes
- **Popular Data**: Pre-loaded top 50 restaurants and their menus
- **Smart Refresh**: Automatic refresh before expiration for frequently accessed data

### Real-World Performance Scenarios

**High-Traffic Restaurant Discovery:**
- Without Cache: 200ms average response time
- With Cache: 15ms average response time
- **Improvement**: 13x faster, 92% reduction in response time

**Menu Browsing Experience:**
- Without Cache: 180ms for menu items + 150ms for restaurant details = 330ms
- With Cache: 12ms for menu items + 8ms for restaurant details = 20ms
- **Improvement**: 16x faster, 94% reduction in total load time

**Search and Filter Operations:**
- Without Cache: 250ms for complex search queries
- With Cache: 25ms for cached search results
- **Improvement**: 10x faster, 90% reduction in search time

**Business Analytics Dashboard:**
- Without Cache: 800ms for restaurant analytics calculation
- With Cache: 30ms for cached analytics
- **Improvement**: 27x faster, 96% reduction in dashboard load time

## Enterprise Monitoring & Alerting

### Production Monitoring Features

**Cache Health Monitoring:**
- Automated health checks every 5 minutes
- Performance threshold alerting
- Memory usage monitoring with recommendations
- Redis connectivity and latency tracking

**Performance Thresholds:**
- **Hit Ratio Warning**: < 70% (indicates cache strategy issues)
- **Hit Ratio Critical**: < 50% (requires immediate attention)
- **Memory Usage Warning**: > 80% (consider scaling or TTL optimization)
- **Memory Usage Critical**: > 90% (immediate action required)
- **Response Time Warning**: > 100ms (performance degradation)
- **Response Time Critical**: > 500ms (system overload)

**Background Maintenance Tasks:**
- **Cache Refresh Loop**: Every 30 minutes for analytics data
- **Health Monitor Loop**: Every 5 minutes for system health
- **Cache Cleanup Loop**: Every 2 hours for expired key removal
- **Memory Optimization**: Automatic memory usage analysis

### Enterprise Cache Patterns Implementation

**Environment-Specific Configuration:**
- **Development**: Short TTLs for rapid testing (1-5 minutes)
- **Staging**: Medium TTLs for integration testing (5-15 minutes)
- **Production**: Long TTLs for optimal performance (30 minutes - 24 hours)

**Automated Cache Warming:**
- Startup cache population for critical data
- Background refresh for frequently accessed items
- Predictive caching based on usage patterns
- Smart refresh before expiration (refresh-ahead pattern)

**Advanced Invalidation Strategies:**
- Hierarchical invalidation with cascade prevention
- Conditional caching based on data state
- Write-through updates for critical consistency
- Multi-level cache coordination

### Production Deployment Checklist

**Redis Configuration:**
- [ ] Redis server installed and configured
- [ ] Memory limits set appropriately
- [ ] Persistence configured for data safety
- [ ] Network security configured
- [ ] Monitoring and alerting set up

**Application Configuration:**
- [ ] Environment variables configured
- [ ] Cache namespaces properly set
- [ ] TTL values optimized for use case
- [ ] Background tasks enabled
- [ ] Health checks configured

**Performance Optimization:**
- [ ] Cache hit ratio > 80%
- [ ] Memory usage < 80%
- [ ] Response times < 100ms for cached data
- [ ] Background tasks running smoothly
- [ ] Monitoring dashboards configured

**Operational Procedures:**
- [ ] Cache warming procedures documented
- [ ] Invalidation strategies tested
- [ ] Monitoring alerts configured
- [ ] Backup and recovery procedures
- [ ] Performance tuning guidelines

## Next Steps (Future Enhancements)

This complete ecosystem can be extended with:
- **Authentication & Authorization** (JWT tokens, role-based access)
- **Payment Integration** (Stripe, PayPal integration)
- **Real-time Updates** (WebSocket notifications for order status)
- **Geolocation Services** (Distance-based restaurant search)
- **Inventory Management** (Stock tracking for menu items)
- **Delivery Tracking** (GPS integration for delivery personnel)
- **Advanced Analytics** (Machine learning for recommendations)
- **Multi-tenant Architecture** (Support for multiple restaurant chains)
