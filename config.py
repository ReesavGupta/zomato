"""
Enterprise Cache Configuration for Zomato Food Delivery Platform
Comprehensive caching settings with environment-specific configurations
"""

import os
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass


class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class CacheNamespace(Enum):
    # Customer-specific data
    CUSTOMERS = "customers"
    CUSTOMER_SESSIONS = "customer_sessions"
    CUSTOMER_PREFERENCES = "customer_preferences"

    # Restaurant-specific data
    RESTAURANTS = "restaurants"
    RESTAURANT_MENUS = "restaurant_menus"
    RESTAURANT_ANALYTICS = "restaurant_analytics"
    RESTAURANT_CAPACITY = "restaurant_capacity"

    # Order-specific data
    ORDERS = "orders"
    ORDER_TRACKING = "order_tracking"
    ORDER_HISTORY = "order_history"

    # Analytics namespaces
    ANALYTICS_RESTAURANTS = "analytics:restaurants"
    ANALYTICS_CUSTOMERS = "analytics:customers"
    ANALYTICS_REVENUE = "analytics:revenue"
    ANALYTICS_POPULAR = "analytics:popular"

    # Search and filtering
    SEARCH_RESULTS = "search:results"
    SEARCH_FILTERS = "search:filters"
    SEARCH_SUGGESTIONS = "search:suggestions"

    # Real-time operational data
    REALTIME_DELIVERY = "realtime:delivery"
    REALTIME_AVAILABILITY = "realtime:availability"
    REALTIME_PRICING = "realtime:pricing"
    REALTIME_NOTIFICATIONS = "realtime:notifications"

    # System and performance
    SYSTEM_HEALTH = "system:health"
    PERFORMANCE_METRICS = "performance:metrics"


@dataclass
class CacheTTLConfig:
    """TTL configuration for different data types"""

    # Static Data - Long TTL (30+ minutes)
    STATIC_DATA_TTL = 1800  # 30 minutes
    RESTAURANT_DETAILS_TTL = 2400  # 40 minutes
    MENU_ITEMS_TTL = 1800  # 30 minutes
    CUSTOMER_PROFILES_TTL = 3600  # 60 minutes

    # Dynamic Data - Short TTL (2-5 minutes)
    DYNAMIC_DATA_TTL = 300  # 5 minutes
    ORDER_STATUS_TTL = 180  # 3 minutes
    DELIVERY_TRACKING_TTL = 120  # 2 minutes
    LIVE_REVIEWS_TTL = 240  # 4 minutes

    # Real-time Data - Very short TTL (30 seconds - 2 minutes)
    REALTIME_DATA_TTL = 60  # 1 minute
    DELIVERY_SLOTS_TTL = 30  # 30 seconds
    RESTAURANT_CAPACITY_TTL = 60  # 1 minute
    DYNAMIC_PRICING_TTL = 120  # 2 minutes

    # Analytics Data - Medium TTL (15 minutes - 24 hours)
    ANALYTICS_SHORT_TTL = 900  # 15 minutes
    ANALYTICS_MEDIUM_TTL = 3600  # 1 hour
    ANALYTICS_LONG_TTL = 14400  # 4 hours
    ANALYTICS_DAILY_TTL = 86400  # 24 hours

    # Session Data
    SESSION_TTL = 1800  # 30 minutes
    SESSION_EXTENDED_TTL = 7200  # 2 hours

    # Search and filtering
    SEARCH_RESULTS_TTL = 300  # 5 minutes
    SEARCH_SUGGESTIONS_TTL = 600  # 10 minutes


class EnterpriseCache:
    """Enterprise cache configuration manager"""

    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        self.environment = environment
        self.ttl_config = CacheTTLConfig()
        self._setup_environment_config()

    def _setup_environment_config(self):
        """Setup environment-specific configurations"""
        if self.environment == Environment.DEVELOPMENT:
            # Shorter TTLs for development
            self.ttl_config.STATIC_DATA_TTL = 300  # 5 minutes
            self.ttl_config.DYNAMIC_DATA_TTL = 60   # 1 minute
            self.ttl_config.REALTIME_DATA_TTL = 30  # 30 seconds
            self.ttl_config.ANALYTICS_SHORT_TTL = 180  # 3 minutes

        elif self.environment == Environment.STAGING:
            # Medium TTLs for staging
            self.ttl_config.STATIC_DATA_TTL = 900   # 15 minutes
            self.ttl_config.DYNAMIC_DATA_TTL = 180  # 3 minutes
            self.ttl_config.REALTIME_DATA_TTL = 45  # 45 seconds
            self.ttl_config.ANALYTICS_SHORT_TTL = 600  # 10 minutes

        # Production uses default values (longest TTLs)

    @property
    def redis_config(self) -> Dict[str, Any]:
        """Redis connection configuration"""
        return {
            "url": os.getenv("REDIS_URL", "redis://localhost:6379"),
            "encoding": "utf8",
            "decode_responses": True,
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
            "retry_on_timeout": True,
            "health_check_interval": 30
        }

    @property
    def cache_prefix(self) -> str:
        """Cache key prefix"""
        return os.getenv("CACHE_PREFIX", f"zomato-{self.environment.value}")

    def get_ttl(self, namespace: CacheNamespace) -> int:
        """Get TTL for specific namespace"""
        ttl_mapping = {
            # Customer data
            CacheNamespace.CUSTOMERS: self.ttl_config.STATIC_DATA_TTL,
            CacheNamespace.CUSTOMER_SESSIONS: self.ttl_config.SESSION_TTL,
            CacheNamespace.CUSTOMER_PREFERENCES: self.ttl_config.STATIC_DATA_TTL,

            # Restaurant data
            CacheNamespace.RESTAURANTS: self.ttl_config.RESTAURANT_DETAILS_TTL,
            CacheNamespace.RESTAURANT_MENUS: self.ttl_config.MENU_ITEMS_TTL,
            CacheNamespace.RESTAURANT_ANALYTICS: self.ttl_config.ANALYTICS_MEDIUM_TTL,
            CacheNamespace.RESTAURANT_CAPACITY: self.ttl_config.REALTIME_DATA_TTL,

            # Order data
            CacheNamespace.ORDERS: self.ttl_config.DYNAMIC_DATA_TTL,
            CacheNamespace.ORDER_TRACKING: self.ttl_config.DELIVERY_TRACKING_TTL,
            CacheNamespace.ORDER_HISTORY: self.ttl_config.STATIC_DATA_TTL,

            # Analytics
            CacheNamespace.ANALYTICS_RESTAURANTS: self.ttl_config.ANALYTICS_LONG_TTL,
            CacheNamespace.ANALYTICS_CUSTOMERS: self.ttl_config.ANALYTICS_LONG_TTL,
            CacheNamespace.ANALYTICS_REVENUE: self.ttl_config.ANALYTICS_DAILY_TTL,
            CacheNamespace.ANALYTICS_POPULAR: self.ttl_config.ANALYTICS_SHORT_TTL,

            # Search
            CacheNamespace.SEARCH_RESULTS: self.ttl_config.SEARCH_RESULTS_TTL,
            CacheNamespace.SEARCH_FILTERS: self.ttl_config.SEARCH_RESULTS_TTL,
            CacheNamespace.SEARCH_SUGGESTIONS: self.ttl_config.SEARCH_SUGGESTIONS_TTL,

            # Real-time
            CacheNamespace.REALTIME_DELIVERY: self.ttl_config.DELIVERY_SLOTS_TTL,
            CacheNamespace.REALTIME_AVAILABILITY: self.ttl_config.RESTAURANT_CAPACITY_TTL,
            CacheNamespace.REALTIME_PRICING: self.ttl_config.DYNAMIC_PRICING_TTL,
            CacheNamespace.REALTIME_NOTIFICATIONS: self.ttl_config.REALTIME_DATA_TTL,

            # System
            CacheNamespace.SYSTEM_HEALTH: self.ttl_config.REALTIME_DATA_TTL,
            CacheNamespace.PERFORMANCE_METRICS: self.ttl_config.ANALYTICS_SHORT_TTL,
        }

        return ttl_mapping.get(namespace, self.ttl_config.DYNAMIC_DATA_TTL)

    def get_cache_key(self, namespace: CacheNamespace, identifier: str, **kwargs) -> str:
        """Generate cache key with namespace and identifier"""
        base_key = f"{self.cache_prefix}:{namespace.value}:{identifier}"

        if kwargs:
            # Add additional parameters to key
            params = ":".join(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            base_key = f"{base_key}:{params}"

        return base_key

    @property
    def performance_thresholds(self) -> Dict[str, float]:
        """Performance monitoring thresholds"""
        return {
            "hit_ratio_warning": 0.7,    # Warn if hit ratio < 70%
            "hit_ratio_critical": 0.5,   # Critical if hit ratio < 50%
            "memory_usage_warning": 0.8, # Warn if memory usage > 80%
            "memory_usage_critical": 0.9, # Critical if memory usage > 90%
            "response_time_warning": 100,  # Warn if response time > 100ms
            "response_time_critical": 500, # Critical if response time > 500ms
        }


# Global cache configuration instance
def get_cache_config() -> EnterpriseCache:
    """Get cache configuration based on environment"""
    env_name = os.getenv("ENVIRONMENT", "development").lower()
    try:
        environment = Environment(env_name)
    except ValueError:
        environment = Environment.DEVELOPMENT

    return EnterpriseCache(environment)


# Cache configuration instance
cache_config = get_cache_config()