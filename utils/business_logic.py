from decimal import Decimal
from typing import List, Dict, Any
from datetime import datetime
from models import OrderStatus
from schemas import OrderItemCreate

class OrderCalculator:
    """Utility class for order calculations"""
    
    @staticmethod
    def calculate_order_total(order_items: List[Dict[str, Any]]) -> Decimal:
        """Calculate total amount for an order"""
        total = Decimal('0.00')
        for item in order_items:
            item_price = Decimal(str(item['price']))
            quantity = item['quantity']
            total += item_price * quantity
        return total
    
    @staticmethod
    def validate_order_items(order_items: List[OrderItemCreate], menu_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate order items and return with prices"""
        menu_item_map = {item['id']: item for item in menu_items}
        validated_items = []
        
        for order_item in order_items:
            if order_item.menu_item_id not in menu_item_map:
                raise ValueError(f"Menu item {order_item.menu_item_id} not found")
            
            menu_item = menu_item_map[order_item.menu_item_id]
            if not menu_item['is_available']:
                raise ValueError(f"Menu item '{menu_item['name']}' is not available")
            
            validated_items.append({
                'menu_item_id': order_item.menu_item_id,
                'quantity': order_item.quantity,
                'price': menu_item['price'],
                'special_requests': order_item.special_requests,
                'menu_item': menu_item
            })
        
        return validated_items

class OrderStatusValidator:
    """Utility class for order status validation"""
    
    VALID_STATUS_TRANSITIONS = {
        OrderStatus.PLACED: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
        OrderStatus.CONFIRMED: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
        OrderStatus.PREPARING: [OrderStatus.OUT_FOR_DELIVERY, OrderStatus.CANCELLED],
        OrderStatus.OUT_FOR_DELIVERY: [OrderStatus.DELIVERED],
        OrderStatus.DELIVERED: [],  # Final state
        OrderStatus.CANCELLED: []   # Final state
    }
    
    @staticmethod
    def can_transition(current_status: OrderStatus, new_status: OrderStatus) -> bool:
        """Check if status transition is valid"""
        return new_status in OrderStatusValidator.VALID_STATUS_TRANSITIONS.get(current_status, [])
    
    @staticmethod
    def validate_status_transition(current_status: OrderStatus, new_status: OrderStatus) -> None:
        """Validate status transition and raise error if invalid"""
        if not OrderStatusValidator.can_transition(current_status, new_status):
            raise ValueError(f"Cannot transition from {current_status.value} to {new_status.value}")
    
    @staticmethod
    def can_be_reviewed(order_status: OrderStatus) -> bool:
        """Check if order can be reviewed"""
        return order_status == OrderStatus.DELIVERED

class ReviewValidator:
    """Utility class for review validation"""
    
    @staticmethod
    def can_customer_review_order(customer_id: int, order_customer_id: int, order_status: OrderStatus) -> bool:
        """Check if customer can review the order"""
        if customer_id != order_customer_id:
            return False
        return OrderStatusValidator.can_be_reviewed(order_status)
    
    @staticmethod
    def validate_review_eligibility(customer_id: int, order_customer_id: int, order_status: OrderStatus) -> None:
        """Validate review eligibility and raise error if invalid"""
        if customer_id != order_customer_id:
            raise ValueError("Customer can only review their own orders")
        
        if not OrderStatusValidator.can_be_reviewed(order_status):
            raise ValueError("Can only review delivered orders")

class AnalyticsCalculator:
    """Utility class for analytics calculations"""
    
    @staticmethod
    def calculate_average_rating(reviews: List[Dict[str, Any]]) -> float:
        """Calculate average rating from reviews"""
        if not reviews:
            return 0.0
        
        total_rating = sum(review['rating'] for review in reviews)
        return round(total_rating / len(reviews), 2)
    
    @staticmethod
    def calculate_popular_items(order_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate popular menu items from order items"""
        item_counts = {}
        
        for item in order_items:
            menu_item_id = item['menu_item_id']
            if menu_item_id not in item_counts:
                item_counts[menu_item_id] = {
                    'menu_item_id': menu_item_id,
                    'name': item.get('menu_item_name', 'Unknown'),
                    'order_count': 0
                }
            item_counts[menu_item_id]['order_count'] += item['quantity']
        
        # Sort by order count descending
        popular_items = sorted(item_counts.values(), key=lambda x: x['order_count'], reverse=True)
        return popular_items[:10]  # Top 10 popular items
    
    @staticmethod
    def calculate_order_status_breakdown(orders: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate order status breakdown"""
        status_counts = {}
        
        for order in orders:
            status = order['order_status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return status_counts
    
    @staticmethod
    def calculate_favorite_restaurants(orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate customer's favorite restaurants"""
        restaurant_counts = {}
        
        for order in orders:
            restaurant_id = order['restaurant_id']
            if restaurant_id not in restaurant_counts:
                restaurant_counts[restaurant_id] = {
                    'restaurant_id': restaurant_id,
                    'name': order.get('restaurant_name', 'Unknown'),
                    'order_count': 0
                }
            restaurant_counts[restaurant_id]['order_count'] += 1
        
        # Sort by order count descending
        favorite_restaurants = sorted(restaurant_counts.values(), key=lambda x: x['order_count'], reverse=True)
        return favorite_restaurants[:5]  # Top 5 favorite restaurants
