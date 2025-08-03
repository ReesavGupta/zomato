from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, time
from decimal import Decimal
import re
from enum import Enum

# Enums
class OrderStatusEnum(str, Enum):
    PLACED = "placed"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# Base schema for common fields
class RestaurantBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Restaurant name")
    description: Optional[str] = Field(None, description="Restaurant description")
    cuisine_type: str = Field(..., min_length=1, max_length=50, description="Type of cuisine")
    address: str = Field(..., min_length=5, description="Restaurant address")
    phone_number: str = Field(..., description="Phone number")
    rating: Optional[float] = Field(0.0, ge=0.0, le=5.0, description="Rating between 0.0 and 5.0")
    is_active: Optional[bool] = Field(True, description="Whether restaurant is active")
    opening_time: Optional[time] = Field(None, description="Opening time")
    closing_time: Optional[time] = Field(None, description="Closing time")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        # Basic phone number validation (digits, spaces, hyphens, parentheses, plus)
        pattern = r'^[\+]?[1-9][\d\s\-\(\)]{7,15}$'
        if not re.match(pattern, v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')):
            raise ValueError('Invalid phone number format')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Restaurant name cannot be empty')
        return v.strip()
    
    @validator('cuisine_type')
    def validate_cuisine_type(cls, v):
        if not v.strip():
            raise ValueError('Cuisine type cannot be empty')
        return v.strip().title()

# Schema for creating a restaurant
class RestaurantCreate(RestaurantBase):
    pass

# Schema for updating a restaurant
class RestaurantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    cuisine_type: Optional[str] = Field(None, min_length=1, max_length=50)
    address: Optional[str] = Field(None, min_length=5)
    phone_number: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    is_active: Optional[bool] = None
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None:
            pattern = r'^[\+]?[1-9][\d\s\-\(\)]{7,15}$'
            if not re.match(pattern, v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')):
                raise ValueError('Invalid phone number format')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Restaurant name cannot be empty')
        return v.strip() if v else v
    
    @validator('cuisine_type')
    def validate_cuisine_type(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Cuisine type cannot be empty')
        return v.strip().title() if v else v

# Schema for restaurant response
class Restaurant(RestaurantBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Schema for paginated restaurant list
class RestaurantList(BaseModel):
    restaurants: List[Restaurant]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True


# ===== MENU ITEM SCHEMAS =====

# Base schema for menu items
class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Menu item name")
    description: Optional[str] = Field(None, description="Menu item description")
    price: float = Field(..., gt=0, description="Price must be positive")
    category: str = Field(..., min_length=1, max_length=50, description="Menu category")
    is_vegetarian: Optional[bool] = Field(False, description="Is vegetarian")
    is_vegan: Optional[bool] = Field(False, description="Is vegan")
    is_available: Optional[bool] = Field(True, description="Is available")
    preparation_time: Optional[int] = Field(None, ge=1, description="Preparation time in minutes")

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Menu item name cannot be empty')
        return v.strip()

    @validator('category')
    def validate_category(cls, v):
        if not v.strip():
            raise ValueError('Category cannot be empty')
        return v.strip().title()

    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        # Round to 2 decimal places
        return round(v, 2)

# Schema for creating a menu item
class MenuItemCreate(MenuItemBase):
    pass

# Schema for updating a menu item
class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    is_vegetarian: Optional[bool] = None
    is_vegan: Optional[bool] = None
    is_available: Optional[bool] = None
    preparation_time: Optional[int] = Field(None, ge=1)

    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Menu item name cannot be empty')
        return v.strip() if v else v

    @validator('category')
    def validate_category(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Category cannot be empty')
        return v.strip().title() if v else v

    @validator('price')
    def validate_price(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('Price must be positive')
            return round(v, 2)
        return v

# Forward declaration for MenuItem
class MenuItem(MenuItemBase):
    id: int
    restaurant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Schema for menu item with restaurant details
class MenuItemWithRestaurant(MenuItem):
    restaurant: Restaurant

    class Config:
        from_attributes = True

# Schema for paginated menu item list
class MenuItemList(BaseModel):
    menu_items: List[MenuItem]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True

# ===== NESTED SCHEMAS FOR RESTAURANT WITH MENU =====

# Restaurant with menu items
class RestaurantWithMenu(Restaurant):
    menu_items: List[MenuItem] = []

    class Config:
        from_attributes = True

# Schema for restaurant with menu statistics
class RestaurantWithMenuStats(Restaurant):
    menu_items: List[MenuItem] = []
    total_menu_items: int = 0
    average_price: Optional[float] = None
    vegetarian_items_count: int = 0
    vegan_items_count: int = 0

    class Config:
        from_attributes = True


# ===== CUSTOMER SCHEMAS =====

# Base schema for customers
class CustomerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Customer name")
    email: str = Field(..., description="Customer email")
    phone_number: str = Field(..., description="Phone number")
    address: str = Field(..., min_length=10, description="Customer address")
    is_active: Optional[bool] = Field(True, description="Is customer active")

    @validator('email')
    def validate_email(cls, v):
        # Basic email validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()

    @validator('phone_number')
    def validate_phone_number(cls, v):
        # Basic phone number validation
        pattern = r'^[\+]?[1-9][\d\s\-\(\)]{7,15}$'
        if not re.match(pattern, v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')):
            raise ValueError('Invalid phone number format')
        return v

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Customer name cannot be empty')
        return v.strip()

# Schema for creating a customer
class CustomerCreate(CustomerBase):
    pass

# Schema for updating a customer
class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = Field(None, min_length=10)
    is_active: Optional[bool] = None

    @validator('email')
    def validate_email(cls, v):
        if v is not None:
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, v):
                raise ValueError('Invalid email format')
            return v.lower()
        return v

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None:
            pattern = r'^[\+]?[1-9][\d\s\-\(\)]{7,15}$'
            if not re.match(pattern, v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')):
                raise ValueError('Invalid phone number format')
        return v

    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Customer name cannot be empty')
        return v.strip() if v else v

# Schema for customer response
class Customer(CustomerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== ORDER ITEM SCHEMAS =====

# Base schema for order items
class OrderItemBase(BaseModel):
    menu_item_id: int = Field(..., description="Menu item ID")
    quantity: int = Field(..., gt=0, description="Quantity must be positive")
    special_requests: Optional[str] = Field(None, description="Special requests for this item")

# Schema for creating order items (used in order creation)
class OrderItemCreate(OrderItemBase):
    pass

# Schema for order item response
class OrderItem(OrderItemBase):
    id: int
    order_id: int
    item_price: Decimal = Field(..., description="Price at time of order")
    menu_item: Optional[MenuItem] = None

    class Config:
        from_attributes = True


# ===== ORDER SCHEMAS =====

# Base schema for orders
class OrderBase(BaseModel):
    restaurant_id: int = Field(..., description="Restaurant ID")
    delivery_address: str = Field(..., min_length=10, description="Delivery address")
    special_instructions: Optional[str] = Field(None, description="Special instructions for the order")

# Schema for creating an order
class OrderCreate(OrderBase):
    order_items: List[OrderItemCreate] = Field(..., min_items=1, description="Order items")

    @validator('order_items')
    def validate_order_items(cls, v):
        if not v:
            raise ValueError('Order must contain at least one item')
        return v

# Schema for updating order status
class OrderStatusUpdate(BaseModel):
    order_status: OrderStatusEnum = Field(..., description="New order status")
    delivery_time: Optional[datetime] = Field(None, description="Delivery time (for delivered status)")

# Schema for order response
class Order(OrderBase):
    id: int
    customer_id: int
    order_status: OrderStatusEnum
    total_amount: Decimal
    order_date: datetime
    delivery_time: Optional[datetime] = None

    class Config:
        from_attributes = True

# Schema for order with full details
class OrderWithDetails(Order):
    customer: Optional[Customer] = None
    restaurant: Optional[Restaurant] = None
    order_items: List[OrderItem] = []

    class Config:
        from_attributes = True


# ===== REVIEW SCHEMAS =====

# Base schema for reviews
class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    comment: Optional[str] = Field(None, max_length=1000, description="Review comment")

# Schema for creating a review
class ReviewCreate(ReviewBase):
    pass

# Schema for review response
class Review(ReviewBase):
    id: int
    customer_id: int
    restaurant_id: int
    order_id: int
    created_at: datetime
    customer: Optional[Customer] = None

    class Config:
        from_attributes = True


# ===== ANALYTICS SCHEMAS =====

# Restaurant analytics
class RestaurantAnalytics(BaseModel):
    restaurant_id: int
    total_orders: int
    total_revenue: Decimal
    average_rating: Optional[float] = None
    total_reviews: int
    popular_items: List[dict] = []  # [{menu_item_id, name, order_count}]
    order_status_breakdown: dict = {}  # {status: count}

    class Config:
        from_attributes = True

# Customer analytics
class CustomerAnalytics(BaseModel):
    customer_id: int
    total_orders: int
    total_spent: Decimal
    average_order_value: Decimal
    favorite_restaurants: List[dict] = []  # [{restaurant_id, name, order_count}]
    order_status_breakdown: dict = {}

    class Config:
        from_attributes = True

# Paginated lists
class CustomerList(BaseModel):
    customers: List[Customer]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True

class OrderList(BaseModel):
    orders: List[Order]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True

class ReviewList(BaseModel):
    reviews: List[Review]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True
