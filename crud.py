from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from models import Restaurant, MenuItem, Customer, Order, OrderItem, Review, OrderStatus
from schemas import (
    RestaurantCreate, RestaurantUpdate, MenuItemCreate, MenuItemUpdate,
    CustomerCreate, CustomerUpdate, OrderCreate, OrderStatusUpdate, ReviewCreate
)
from utils.business_logic import OrderCalculator, OrderStatusValidator, ReviewValidator, AnalyticsCalculator

class RestaurantCRUD:
    
    @staticmethod
    async def create_restaurant(db: AsyncSession, restaurant: RestaurantCreate) -> Restaurant:
        """Create a new restaurant"""
        db_restaurant = Restaurant(**restaurant.dict())
        db.add(db_restaurant)
        try:
            await db.commit()
            await db.refresh(db_restaurant)
            return db_restaurant
        except IntegrityError:
            await db.rollback()
            raise ValueError("Restaurant with this name already exists")
    
    @staticmethod
    async def get_restaurant(db: AsyncSession, restaurant_id: int) -> Optional[Restaurant]:
        """Get a restaurant by ID"""
        result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_restaurants(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = False
    ) -> tuple[List[Restaurant], int]:
        """Get restaurants with pagination"""
        query = select(Restaurant)
        count_query = select(func.count(Restaurant.id))
        
        if active_only:
            query = query.where(Restaurant.is_active == True)
            count_query = count_query.where(Restaurant.is_active == True)
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(Restaurant.created_at.desc())
        result = await db.execute(query)
        restaurants = result.scalars().all()
        
        return restaurants, total
    
    @staticmethod
    async def search_restaurants_by_cuisine(
        db: AsyncSession, 
        cuisine_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Restaurant], int]:
        """Search restaurants by cuisine type"""
        query = select(Restaurant).where(
            Restaurant.cuisine_type.ilike(f"%{cuisine_type}%")
        )
        count_query = select(func.count(Restaurant.id)).where(
            Restaurant.cuisine_type.ilike(f"%{cuisine_type}%")
        )
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(Restaurant.created_at.desc())
        result = await db.execute(query)
        restaurants = result.scalars().all()
        
        return restaurants, total
    
    @staticmethod
    async def update_restaurant(
        db: AsyncSession, 
        restaurant_id: int, 
        restaurant_update: RestaurantUpdate
    ) -> Optional[Restaurant]:
        """Update a restaurant"""
        result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
        db_restaurant = result.scalar_one_or_none()
        
        if not db_restaurant:
            return None
        
        # Update only provided fields
        update_data = restaurant_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_restaurant, field, value)
        
        try:
            await db.commit()
            await db.refresh(db_restaurant)
            return db_restaurant
        except IntegrityError:
            await db.rollback()
            raise ValueError("Restaurant with this name already exists")
    
    @staticmethod
    async def delete_restaurant(db: AsyncSession, restaurant_id: int) -> bool:
        """Delete a restaurant"""
        result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
        db_restaurant = result.scalar_one_or_none()
        
        if not db_restaurant:
            return False
        
        await db.delete(db_restaurant)
        await db.commit()
        return True
    
    @staticmethod
    async def get_active_restaurants(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Restaurant], int]:
        """Get only active restaurants"""
        return await RestaurantCRUD.get_restaurants(db, skip, limit, active_only=True)

    @staticmethod
    async def get_restaurant_with_menu(db: AsyncSession, restaurant_id: int) -> Optional[Restaurant]:
        """Get a restaurant with all its menu items"""
        result = await db.execute(
            select(Restaurant)
            .options(selectinload(Restaurant.menu_items))
            .where(Restaurant.id == restaurant_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_restaurant_menu(
        db: AsyncSession,
        restaurant_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[MenuItem], int]:
        """Get all menu items for a specific restaurant"""
        # Check if restaurant exists
        restaurant_result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
        if not restaurant_result.scalar_one_or_none():
            return [], 0

        # Get menu items
        query = select(MenuItem).where(MenuItem.restaurant_id == restaurant_id)
        count_query = select(func.count(MenuItem.id)).where(MenuItem.restaurant_id == restaurant_id)

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(MenuItem.created_at.desc())
        result = await db.execute(query)
        menu_items = result.scalars().all()

        return menu_items, total


class MenuItemCRUD:

    @staticmethod
    async def create_menu_item(
        db: AsyncSession,
        menu_item: MenuItemCreate,
        restaurant_id: int
    ) -> MenuItem:
        """Create a new menu item for a restaurant"""
        # Check if restaurant exists
        restaurant_result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
        if not restaurant_result.scalar_one_or_none():
            raise ValueError("Restaurant not found")

        db_menu_item = MenuItem(**menu_item.dict(), restaurant_id=restaurant_id)
        db.add(db_menu_item)
        try:
            await db.commit()
            await db.refresh(db_menu_item)
            return db_menu_item
        except IntegrityError:
            await db.rollback()
            raise ValueError("Error creating menu item")

    @staticmethod
    async def get_menu_item(db: AsyncSession, item_id: int) -> Optional[MenuItem]:
        """Get a menu item by ID"""
        result = await db.execute(select(MenuItem).where(MenuItem.id == item_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_menu_item_with_restaurant(db: AsyncSession, item_id: int) -> Optional[MenuItem]:
        """Get a menu item with restaurant details"""
        result = await db.execute(
            select(MenuItem)
            .options(selectinload(MenuItem.restaurant))
            .where(MenuItem.id == item_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_menu_items(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[MenuItem], int]:
        """Get all menu items with pagination"""
        query = select(MenuItem)
        count_query = select(func.count(MenuItem.id))

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(MenuItem.created_at.desc())
        result = await db.execute(query)
        menu_items = result.scalars().all()

        return menu_items, total

    @staticmethod
    async def search_menu_items(
        db: AsyncSession,
        category: Optional[str] = None,
        vegetarian: Optional[bool] = None,
        vegan: Optional[bool] = None,
        available: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[MenuItem], int]:
        """Search menu items with filters"""
        query = select(MenuItem)
        count_query = select(func.count(MenuItem.id))

        # Build filters
        filters = []
        if category:
            filters.append(MenuItem.category.ilike(f"%{category}%"))
        if vegetarian is not None:
            filters.append(MenuItem.is_vegetarian == vegetarian)
        if vegan is not None:
            filters.append(MenuItem.is_vegan == vegan)
        if available is not None:
            filters.append(MenuItem.is_available == available)

        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(MenuItem.created_at.desc())
        result = await db.execute(query)
        menu_items = result.scalars().all()

        return menu_items, total

    @staticmethod
    async def update_menu_item(
        db: AsyncSession,
        item_id: int,
        menu_item_update: MenuItemUpdate
    ) -> Optional[MenuItem]:
        """Update a menu item"""
        result = await db.execute(select(MenuItem).where(MenuItem.id == item_id))
        db_menu_item = result.scalar_one_or_none()

        if not db_menu_item:
            return None

        # Update only provided fields
        update_data = menu_item_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_menu_item, field, value)

        try:
            await db.commit()
            await db.refresh(db_menu_item)
            return db_menu_item
        except IntegrityError:
            await db.rollback()
            raise ValueError("Error updating menu item")

    @staticmethod
    async def delete_menu_item(db: AsyncSession, item_id: int) -> bool:
        """Delete a menu item"""
        result = await db.execute(select(MenuItem).where(MenuItem.id == item_id))
        db_menu_item = result.scalar_one_or_none()

        if not db_menu_item:
            return False

        await db.delete(db_menu_item)
        await db.commit()
        return True


class CustomerCRUD:

    @staticmethod
    async def create_customer(db: AsyncSession, customer: CustomerCreate) -> Customer:
        """Create a new customer"""
        db_customer = Customer(**customer.dict())
        db.add(db_customer)
        try:
            await db.commit()
            await db.refresh(db_customer)
            return db_customer
        except IntegrityError:
            await db.rollback()
            raise ValueError("Customer with this email already exists")

    @staticmethod
    async def get_customer(db: AsyncSession, customer_id: int) -> Optional[Customer]:
        """Get a customer by ID"""
        result = await db.execute(select(Customer).where(Customer.id == customer_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_customer_by_email(db: AsyncSession, email: str) -> Optional[Customer]:
        """Get a customer by email"""
        result = await db.execute(select(Customer).where(Customer.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_customers(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> tuple[List[Customer], int]:
        """Get customers with pagination"""
        query = select(Customer)
        count_query = select(func.count(Customer.id))

        if active_only:
            query = query.where(Customer.is_active == True)
            count_query = count_query.where(Customer.is_active == True)

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(Customer.created_at.desc())
        result = await db.execute(query)
        customers = result.scalars().all()

        return customers, total

    @staticmethod
    async def update_customer(
        db: AsyncSession,
        customer_id: int,
        customer_update: CustomerUpdate
    ) -> Optional[Customer]:
        """Update a customer"""
        result = await db.execute(select(Customer).where(Customer.id == customer_id))
        db_customer = result.scalar_one_or_none()

        if not db_customer:
            return None

        # Update only provided fields
        update_data = customer_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_customer, field, value)

        try:
            await db.commit()
            await db.refresh(db_customer)
            return db_customer
        except IntegrityError:
            await db.rollback()
            raise ValueError("Customer with this email already exists")

    @staticmethod
    async def delete_customer(db: AsyncSession, customer_id: int) -> bool:
        """Delete a customer"""
        result = await db.execute(select(Customer).where(Customer.id == customer_id))
        db_customer = result.scalar_one_or_none()

        if not db_customer:
            return False

        await db.delete(db_customer)
        await db.commit()
        return True


class OrderCRUD:

    @staticmethod
    async def create_order(db: AsyncSession, order: OrderCreate, customer_id: int) -> Order:
        """Create a new order with order items"""
        # Validate customer exists
        customer_result = await db.execute(select(Customer).where(Customer.id == customer_id))
        if not customer_result.scalar_one_or_none():
            raise ValueError("Customer not found")

        # Validate restaurant exists
        restaurant_result = await db.execute(select(Restaurant).where(Restaurant.id == order.restaurant_id))
        restaurant = restaurant_result.scalar_one_or_none()
        if not restaurant:
            raise ValueError("Restaurant not found")

        # Get menu items for validation
        menu_item_ids = [item.menu_item_id for item in order.order_items]
        menu_items_result = await db.execute(
            select(MenuItem).where(
                and_(
                    MenuItem.id.in_(menu_item_ids),
                    MenuItem.restaurant_id == order.restaurant_id
                )
            )
        )
        menu_items = menu_items_result.scalars().all()
        menu_items_dict = {item.id: item for item in menu_items}

        # Validate order items
        validated_items = []
        for order_item in order.order_items:
            if order_item.menu_item_id not in menu_items_dict:
                raise ValueError(f"Menu item {order_item.menu_item_id} not found or doesn't belong to this restaurant")

            menu_item = menu_items_dict[order_item.menu_item_id]
            if not menu_item.is_available:
                raise ValueError(f"Menu item '{menu_item.name}' is not available")

            validated_items.append({
                'menu_item_id': order_item.menu_item_id,
                'quantity': order_item.quantity,
                'item_price': menu_item.price,
                'special_requests': order_item.special_requests
            })

        # Calculate total amount
        total_amount = sum(Decimal(str(item['item_price'])) * item['quantity'] for item in validated_items)

        # Create order
        db_order = Order(
            customer_id=customer_id,
            restaurant_id=order.restaurant_id,
            total_amount=total_amount,
            delivery_address=order.delivery_address,
            special_instructions=order.special_instructions,
            order_status=OrderStatus.PLACED
        )

        db.add(db_order)
        await db.flush()  # Get the order ID

        # Create order items
        for item_data in validated_items:
            db_order_item = OrderItem(
                order_id=db_order.id,
                **item_data
            )
            db.add(db_order_item)

        try:
            await db.commit()
            await db.refresh(db_order)
            return db_order
        except Exception:
            await db.rollback()
            raise ValueError("Error creating order")

    @staticmethod
    async def get_order(db: AsyncSession, order_id: int) -> Optional[Order]:
        """Get an order by ID"""
        result = await db.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_order_with_details(db: AsyncSession, order_id: int) -> Optional[Order]:
        """Get an order with full details"""
        result = await db.execute(
            select(Order)
            .options(
                selectinload(Order.customer),
                selectinload(Order.restaurant),
                selectinload(Order.order_items).selectinload(OrderItem.menu_item)
            )
            .where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_order_status(
        db: AsyncSession,
        order_id: int,
        status_update: OrderStatusUpdate
    ) -> Optional[Order]:
        """Update order status"""
        result = await db.execute(select(Order).where(Order.id == order_id))
        db_order = result.scalar_one_or_none()

        if not db_order:
            return None

        # Validate status transition
        OrderStatusValidator.validate_status_transition(db_order.order_status, status_update.order_status)

        # Update status
        db_order.order_status = status_update.order_status

        # Set delivery time if delivered
        if status_update.order_status == OrderStatus.DELIVERED and status_update.delivery_time:
            db_order.delivery_time = status_update.delivery_time
        elif status_update.order_status == OrderStatus.DELIVERED:
            db_order.delivery_time = datetime.utcnow()

        try:
            await db.commit()
            await db.refresh(db_order)
            return db_order
        except Exception:
            await db.rollback()
            raise ValueError("Error updating order status")

    @staticmethod
    async def get_customer_orders(
        db: AsyncSession,
        customer_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Order], int]:
        """Get orders for a customer"""
        query = select(Order).where(Order.customer_id == customer_id)
        count_query = select(func.count(Order.id)).where(Order.customer_id == customer_id)

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(Order.order_date.desc())
        result = await db.execute(query)
        orders = result.scalars().all()

        return orders, total

    @staticmethod
    async def get_restaurant_orders(
        db: AsyncSession,
        restaurant_id: int,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[OrderStatus] = None
    ) -> tuple[List[Order], int]:
        """Get orders for a restaurant"""
        query = select(Order).where(Order.restaurant_id == restaurant_id)
        count_query = select(func.count(Order.id)).where(Order.restaurant_id == restaurant_id)

        if status_filter:
            query = query.where(Order.order_status == status_filter)
            count_query = count_query.where(Order.order_status == status_filter)

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(Order.order_date.desc())
        result = await db.execute(query)
        orders = result.scalars().all()

        return orders, total


class ReviewCRUD:

    @staticmethod
    async def create_review(
        db: AsyncSession,
        review: ReviewCreate,
        customer_id: int,
        order_id: int
    ) -> Review:
        """Create a review for an order"""
        # Get order with details
        order_result = await db.execute(
            select(Order)
            .options(selectinload(Order.review))
            .where(Order.id == order_id)
        )
        order = order_result.scalar_one_or_none()

        if not order:
            raise ValueError("Order not found")

        # Validate review eligibility
        ReviewValidator.validate_review_eligibility(customer_id, order.customer_id, order.order_status)

        # Check if review already exists
        if order.review:
            raise ValueError("Order has already been reviewed")

        # Create review
        db_review = Review(
            customer_id=customer_id,
            restaurant_id=order.restaurant_id,
            order_id=order_id,
            rating=review.rating,
            comment=review.comment
        )

        db.add(db_review)

        try:
            await db.commit()
            await db.refresh(db_review)
            return db_review
        except Exception:
            await db.rollback()
            raise ValueError("Error creating review")

    @staticmethod
    async def get_restaurant_reviews(
        db: AsyncSession,
        restaurant_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Review], int]:
        """Get reviews for a restaurant"""
        query = select(Review).where(Review.restaurant_id == restaurant_id)
        count_query = select(func.count(Review.id)).where(Review.restaurant_id == restaurant_id)

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results with customer details
        query = query.options(selectinload(Review.customer)).offset(skip).limit(limit).order_by(Review.created_at.desc())
        result = await db.execute(query)
        reviews = result.scalars().all()

        return reviews, total

    @staticmethod
    async def get_customer_reviews(
        db: AsyncSession,
        customer_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Review], int]:
        """Get reviews by a customer"""
        query = select(Review).where(Review.customer_id == customer_id)
        count_query = select(func.count(Review.id)).where(Review.customer_id == customer_id)

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(Review.created_at.desc())
        result = await db.execute(query)
        reviews = result.scalars().all()

        return reviews, total


class AnalyticsCRUD:

    @staticmethod
    async def get_restaurant_analytics(db: AsyncSession, restaurant_id: int) -> Dict[str, Any]:
        """Get analytics for a restaurant"""
        # Get total orders and revenue
        orders_result = await db.execute(
            select(func.count(Order.id), func.sum(Order.total_amount))
            .where(Order.restaurant_id == restaurant_id)
        )
        total_orders, total_revenue = orders_result.first()
        total_orders = total_orders or 0
        total_revenue = total_revenue or Decimal('0.00')

        # Get reviews and average rating
        reviews_result = await db.execute(
            select(Review.rating)
            .where(Review.restaurant_id == restaurant_id)
        )
        reviews = reviews_result.scalars().all()
        average_rating = AnalyticsCalculator.calculate_average_rating([{'rating': r} for r in reviews])

        # Get popular items
        popular_items_result = await db.execute(
            select(OrderItem.menu_item_id, MenuItem.name, func.sum(OrderItem.quantity).label('total_quantity'))
            .join(MenuItem, OrderItem.menu_item_id == MenuItem.id)
            .join(Order, OrderItem.order_id == Order.id)
            .where(Order.restaurant_id == restaurant_id)
            .group_by(OrderItem.menu_item_id, MenuItem.name)
            .order_by(desc('total_quantity'))
            .limit(10)
        )
        popular_items = [
            {
                'menu_item_id': item[0],
                'name': item[1],
                'order_count': item[2]
            }
            for item in popular_items_result.fetchall()
        ]

        # Get order status breakdown
        status_result = await db.execute(
            select(Order.order_status, func.count(Order.id))
            .where(Order.restaurant_id == restaurant_id)
            .group_by(Order.order_status)
        )
        order_status_breakdown = {status.value: count for status, count in status_result.fetchall()}

        return {
            'restaurant_id': restaurant_id,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'average_rating': average_rating,
            'total_reviews': len(reviews),
            'popular_items': popular_items,
            'order_status_breakdown': order_status_breakdown
        }

    @staticmethod
    async def get_customer_analytics(db: AsyncSession, customer_id: int) -> Dict[str, Any]:
        """Get analytics for a customer"""
        # Get total orders and spending
        orders_result = await db.execute(
            select(func.count(Order.id), func.sum(Order.total_amount))
            .where(Order.customer_id == customer_id)
        )
        total_orders, total_spent = orders_result.first()
        total_orders = total_orders or 0
        total_spent = total_spent or Decimal('0.00')

        average_order_value = total_spent / total_orders if total_orders > 0 else Decimal('0.00')

        # Get favorite restaurants
        favorite_restaurants_result = await db.execute(
            select(Order.restaurant_id, Restaurant.name, func.count(Order.id).label('order_count'))
            .join(Restaurant, Order.restaurant_id == Restaurant.id)
            .where(Order.customer_id == customer_id)
            .group_by(Order.restaurant_id, Restaurant.name)
            .order_by(desc('order_count'))
            .limit(5)
        )
        favorite_restaurants = [
            {
                'restaurant_id': item[0],
                'name': item[1],
                'order_count': item[2]
            }
            for item in favorite_restaurants_result.fetchall()
        ]

        # Get order status breakdown
        status_result = await db.execute(
            select(Order.order_status, func.count(Order.id))
            .where(Order.customer_id == customer_id)
            .group_by(Order.order_status)
        )
        order_status_breakdown = {status.value: count for status, count in status_result.fetchall()}

        return {
            'customer_id': customer_id,
            'total_orders': total_orders,
            'total_spent': total_spent,
            'average_order_value': average_order_value,
            'favorite_restaurants': favorite_restaurants,
            'order_status_breakdown': order_status_breakdown
        }
