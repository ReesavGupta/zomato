from sqlalchemy import Column, Integer, String, Text, Float, Boolean, Time, DateTime, UniqueConstraint, ForeignKey, DECIMAL, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

# Enums for order status
class OrderStatus(enum.Enum):
    PLACED = "placed"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Restaurant(Base):
    __tablename__ = "restaurants"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Required fields
    name = Column(String(100), nullable=False, index=True)
    cuisine_type = Column(String(50), nullable=False, index=True)
    address = Column(Text, nullable=False)
    phone_number = Column(String(20), nullable=False)

    # Optional fields
    description = Column(Text, nullable=True)

    # Rating and status
    rating = Column(Float, default=0.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Operating hours
    opening_time = Column(Time, nullable=True)
    closing_time = Column(Time, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    menu_items = relationship("MenuItem", back_populates="restaurant", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="restaurant", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="restaurant", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        UniqueConstraint('name', name='uq_restaurant_name'),
    )

    def __repr__(self):
        return f"<Restaurant(id={self.id}, name='{self.name}', cuisine='{self.cuisine_type}')>"


class MenuItem(Base):
    __tablename__ = "menu_items"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Required fields
    name = Column(String(100), nullable=False, index=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    category = Column(String(50), nullable=False, index=True)

    # Optional fields
    description = Column(Text, nullable=True)

    # Dietary preferences
    is_vegetarian = Column(Boolean, default=False, nullable=False, index=True)
    is_vegan = Column(Boolean, default=False, nullable=False, index=True)

    # Availability and timing
    is_available = Column(Boolean, default=True, nullable=False, index=True)
    preparation_time = Column(Integer, nullable=True)  # in minutes

    # Foreign key
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    restaurant = relationship("Restaurant", back_populates="menu_items")
    order_items = relationship("OrderItem", back_populates="menu_item")

    def __repr__(self):
        return f"<MenuItem(id={self.id}, name='{self.name}', price={self.price}, restaurant_id={self.restaurant_id})>"


class Customer(Base):
    __tablename__ = "customers"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Required fields
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone_number = Column(String(20), nullable=False)
    address = Column(Text, nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="customer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.name}', email='{self.email}')>"


class Order(Base):
    __tablename__ = "orders"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False, index=True)

    # Order details
    order_status = Column(Enum(OrderStatus), default=OrderStatus.PLACED, nullable=False, index=True)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    delivery_address = Column(Text, nullable=False)
    special_instructions = Column(Text, nullable=True)

    # Timestamps
    order_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    delivery_time = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    restaurant = relationship("Restaurant", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    review = relationship("Review", back_populates="order", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order(id={self.id}, customer_id={self.customer_id}, restaurant_id={self.restaurant_id}, status={self.order_status})>"


class OrderItem(Base):
    __tablename__ = "order_items"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False, index=True)

    # Order item details
    quantity = Column(Integer, nullable=False)
    item_price = Column(DECIMAL(10, 2), nullable=False)  # Price at time of order
    special_requests = Column(Text, nullable=True)

    # Relationships
    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")

    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, menu_item_id={self.menu_item_id}, quantity={self.quantity})>"


class Review(Base):
    __tablename__ = "reviews"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True, index=True)

    # Review details
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    customer = relationship("Customer", back_populates="reviews")
    restaurant = relationship("Restaurant", back_populates="reviews")
    order = relationship("Order", back_populates="review")

    def __repr__(self):
        return f"<Review(id={self.id}, customer_id={self.customer_id}, restaurant_id={self.restaurant_id}, rating={self.rating})>"
