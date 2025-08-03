# Zomato Food Delivery Ecosystem API - Version 3

A complete food delivery ecosystem built with FastAPI, SQLAlchemy, and SQLite. This advanced version implements complex multi-table relationships with customers, orders, reviews, and comprehensive analytics, creating a production-ready food delivery platform.

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

### Advanced Technical Features
- **Complex Multi-table Relationships** - Customer ↔ Order ↔ Restaurant
- **Association Objects** - Order items with additional data
- **Business Logic Layer** - Order calculations and status validation
- **Comprehensive Error Handling** - Detailed validation and error messages
- **Advanced Querying** - Complex joins and aggregations
- **Async Database Operations** - High-performance SQLite with aiosqlite

## Project Structure

```
zomato/
├── main.py              # FastAPI application entry point
├── database.py          # Database configuration and session management
├── models.py            # SQLAlchemy models (Restaurant, MenuItem, Customer, Order, OrderItem, Review)
├── schemas.py           # Pydantic schemas for all models and responses
├── crud.py              # Database operations with complex joins and business logic
├── routes/              # Modular route definitions
│   ├── __init__.py
│   ├── restaurants.py   # Restaurant and restaurant-menu endpoints
│   ├── menu_items.py    # Menu item endpoints
│   ├── customers.py     # Customer management endpoints
│   ├── orders.py        # Order processing and tracking endpoints
│   └── reviews.py       # Review and analytics endpoints
├── utils/               # Business logic and utility functions
│   ├── __init__.py
│   └── business_logic.py # Order calculations, validations, analytics
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation & Setup

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python main.py
```

The API will be available at: `http://localhost:8000`

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
