import time
import logging
from typing import Any, Optional, Callable, Dict
from fastapi_cache import FastAPICache
from functools import wraps
from config import cache_config, CacheNamespace, Environment

def safe_cache(namespace: str, expire: int):
    """Safe cache decorator that handles missing Redis gracefully"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Check if cache is available
                if hasattr(FastAPICache, '_backend') and FastAPICache._backend is not None:
                    # Try to use the original cache decorator
                    from fastapi_cache.decorator import cache
                    cached_func = cache(namespace=namespace, expire=expire)(func)
                    return await cached_func(*args, **kwargs)
                else:
                    # Cache not available, call function directly
                    return await func(*args, **kwargs)
            except Exception as e:
                # If cache fails, fall back to direct function call
                cache_logger.warning(f"Cache operation failed, falling back to direct call: {str(e)}")
                return await func(*args, **kwargs)
        return wrapper
    return decorator


def session_cache(namespace: CacheNamespace, key_builder: Optional[Callable] = None, condition: Optional[Callable] = None):
    """Advanced session-based cache decorator with conditional caching"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Check if cache is available
                if not hasattr(FastAPICache, '_backend') or FastAPICache._backend is None:
                    return await func(*args, **kwargs)

                # Check condition if provided
                if condition and not condition(*args, **kwargs):
                    return await func(*args, **kwargs)

                # Build cache key
                if key_builder:
                    cache_key = key_builder(*args, **kwargs)
                else:
                    # Default key builder
                    cache_key = f"{func.__name__}:" + ":".join(str(arg) for arg in args if not hasattr(arg, '__dict__'))

                # Get TTL from configuration
                ttl = cache_config.get_ttl(namespace)

                # Build full cache key
                full_key = cache_config.get_cache_key(namespace, cache_key)

                # Try to get from cache
                backend = FastAPICache.get_backend()
                cached_result = await backend.get(full_key)

                if cached_result is not None:
                    cache_logger.debug(f"Cache HIT for key: {full_key}")
                    return cached_result

                # Cache miss - execute function
                cache_logger.debug(f"Cache MISS for key: {full_key}")
                result = await func(*args, **kwargs)

                # Store in cache
                await backend.set(full_key, result, expire=ttl)

                return result

            except Exception as e:
                cache_logger.warning(f"Session cache operation failed, falling back to direct call: {str(e)}")
                return await func(*args, **kwargs)
        return wrapper
    return decorator


def conditional_cache(namespace: CacheNamespace, condition: Callable, expire: Optional[int] = None):
    """Conditional cache decorator - only cache when condition is met"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Check if cache is available
                if not hasattr(FastAPICache, '_backend') or FastAPICache._backend is None:
                    return await func(*args, **kwargs)

                # Execute function first to get result for condition check
                result = await func(*args, **kwargs)

                # Check if we should cache this result
                if condition(result):
                    # Get TTL
                    ttl = expire or cache_config.get_ttl(namespace)

                    # Build cache key
                    cache_key = f"{func.__name__}:" + ":".join(str(arg) for arg in args if not hasattr(arg, '__dict__'))
                    full_key = cache_config.get_cache_key(namespace, cache_key)

                    # Store in cache
                    backend = FastAPICache.get_backend()
                    await backend.set(full_key, result, expire=ttl)
                    cache_logger.debug(f"Conditionally cached result for key: {full_key}")

                return result

            except Exception as e:
                cache_logger.warning(f"Conditional cache operation failed: {str(e)}")
                return await func(*args, **kwargs)
        return wrapper
    return decorator

# Configure logging for cache operations
logging.basicConfig(level=logging.INFO)
cache_logger = logging.getLogger("cache_manager")

class CacheManager:
    """Utility class for advanced cache management and performance tracking"""

    # Cache namespaces - Multi-level organization
    RESTAURANTS_NAMESPACE = "restaurants"
    MENU_ITEMS_NAMESPACE = "menu-items"
    RESTAURANT_MENUS_NAMESPACE = "restaurant-menus"
    SEARCH_RESULTS_NAMESPACE = "search-results"
    CUSTOMERS_NAMESPACE = "customers"
    ORDERS_NAMESPACE = "orders"
    REVIEWS_NAMESPACE = "reviews"
    ANALYTICS_NAMESPACE = "analytics"
    CATEGORIES_NAMESPACE = "categories"
    DIETARY_NAMESPACE = "dietary"

    # Multi-Level Cache TTL settings (in seconds)
    # Basic restaurant data - 10 minutes (stable data)
    RESTAURANT_DETAIL_TTL = 600
    RESTAURANT_LIST_TTL = 600
    RESTAURANT_ACTIVE_TTL = 600

    # Menu items - 8 minutes (more dynamic)
    MENU_ITEMS_TTL = 480
    MENU_ITEM_DETAIL_TTL = 480
    MENU_CATEGORY_TTL = 480

    # Restaurant-with-menu - 15 minutes (expensive joins)
    RESTAURANT_WITH_MENU_TTL = 900
    RESTAURANT_MENU_LIST_TTL = 900

    # Search results - 5 minutes (frequently changing)
    RESTAURANT_SEARCH_TTL = 300
    MENU_SEARCH_TTL = 300
    DIETARY_SEARCH_TTL = 300
    CATEGORY_SEARCH_TTL = 300

    # Analytics and aggregations - 20 minutes (expensive calculations)
    ANALYTICS_TTL = 1200
    AGGREGATION_TTL = 1200
    POPULAR_ITEMS_TTL = 1200

    # Business logic caching - 12 minutes
    CALCULATED_FIELDS_TTL = 720
    RATING_AGGREGATION_TTL = 720
    
    @staticmethod
    async def clear_namespace(namespace: str) -> bool:
        """Clear all cache entries for a specific namespace"""
        try:
            # Check if FastAPICache is initialized
            if not hasattr(FastAPICache, '_backend') or FastAPICache._backend is None:
                cache_logger.warning("Cache not initialized, skipping clear operation")
                return False
            await FastAPICache.clear(namespace=namespace)
            cache_logger.info(f"Cleared cache namespace: {namespace}")
            return True
        except Exception as e:
            cache_logger.error(f"Failed to clear namespace {namespace}: {str(e)}")
            return False
    
    @staticmethod
    async def clear_all_cache() -> bool:
        """Clear entire cache"""
        try:
            # Check if FastAPICache is initialized
            if not hasattr(FastAPICache, '_backend') or FastAPICache._backend is None:
                cache_logger.warning("Cache not initialized, skipping clear operation")
                return False
            await FastAPICache.clear()
            cache_logger.info("Cleared entire cache")
            return True
        except Exception as e:
            cache_logger.error(f"Failed to clear entire cache: {str(e)}")
            return False
    
    @staticmethod
    async def get_cache_stats() -> dict:
        """Get basic cache statistics"""
        try:
            # Check if FastAPICache is initialized
            if not hasattr(FastAPICache, '_backend') or FastAPICache._backend is None:
                return {
                    "error": "Cache not initialized",
                    "message": "Redis cache is not available. Please ensure Redis server is running."
                }

            # Get Redis client from FastAPICache
            backend = FastAPICache.get_backend()
            redis_client = backend.redis

            # Get Redis info
            info = await redis_client.info()

            # Get all keys with our prefix
            keys = await redis_client.keys("zomato-cache:*")

            stats = {
                "total_keys": len(keys),
                "memory_usage": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "cache_hits": info.get("keyspace_hits", 0),
                "cache_misses": info.get("keyspace_misses", 0),
                "keys_by_namespace": {}
            }

            # Group keys by namespace
            for key in keys:
                # Extract namespace from key (format: zomato-cache:namespace:...)
                parts = key.split(":")
                if len(parts) >= 3:
                    namespace = parts[2]
                    if namespace not in stats["keys_by_namespace"]:
                        stats["keys_by_namespace"][namespace] = 0
                    stats["keys_by_namespace"][namespace] += 1

            return stats
        except Exception as e:
            cache_logger.error(f"Failed to get cache stats: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    async def get_detailed_cache_stats() -> dict:
        """Get detailed cache statistics by namespace with TTL information"""
        try:
            # Check if FastAPICache is initialized
            if not hasattr(FastAPICache, '_backend') or FastAPICache._backend is None:
                return {
                    "error": "Cache not initialized",
                    "message": "Redis cache is not available. Please ensure Redis server is running."
                }

            # Get Redis client from FastAPICache
            backend = FastAPICache.get_backend()
            redis_client = backend.redis

            # Get Redis info
            info = await redis_client.info()

            # Get all keys with our prefix
            keys = await redis_client.keys("zomato-cache:*")

            # Detailed namespace analysis
            namespace_details = {}
            total_memory_estimate = 0

            for key in keys:
                parts = key.split(":")
                if len(parts) >= 3:
                    namespace = parts[2]

                    if namespace not in namespace_details:
                        namespace_details[namespace] = {
                            "key_count": 0,
                            "keys": [],
                            "ttl_info": {},
                            "memory_estimate": 0
                        }

                    namespace_details[namespace]["key_count"] += 1
                    namespace_details[namespace]["keys"].append(key)

                    # Get TTL for this key
                    try:
                        ttl = await redis_client.ttl(key)
                        if ttl > 0:
                            namespace_details[namespace]["ttl_info"][key] = ttl

                        # Estimate memory usage (rough approximation)
                        key_size = len(key.encode('utf-8'))
                        value_size = await redis_client.memory_usage(key) or 100  # fallback estimate
                        total_size = key_size + value_size
                        namespace_details[namespace]["memory_estimate"] += total_size
                        total_memory_estimate += total_size
                    except Exception:
                        # Skip if memory_usage command not available
                        pass

            # Calculate hit ratios
            total_hits = info.get("keyspace_hits", 0)
            total_misses = info.get("keyspace_misses", 0)
            total_requests = total_hits + total_misses
            hit_ratio = (total_hits / total_requests * 100) if total_requests > 0 else 0

            detailed_stats = {
                "overview": {
                    "total_keys": len(keys),
                    "total_namespaces": len(namespace_details),
                    "memory_usage": info.get("used_memory_human", "N/A"),
                    "memory_estimate_bytes": total_memory_estimate,
                    "connected_clients": info.get("connected_clients", 0),
                    "cache_hits": total_hits,
                    "cache_misses": total_misses,
                    "hit_ratio_percent": round(hit_ratio, 2),
                    "redis_version": info.get("redis_version", "Unknown")
                },
                "namespace_details": namespace_details,
                "ttl_configuration": {
                    "restaurants": f"{CacheManager.RESTAURANT_DETAIL_TTL}s",
                    "menu-items": f"{CacheManager.MENU_ITEMS_TTL}s",
                    "restaurant-menus": f"{CacheManager.RESTAURANT_WITH_MENU_TTL}s",
                    "search-results": f"{CacheManager.RESTAURANT_SEARCH_TTL}s",
                    "analytics": f"{CacheManager.ANALYTICS_TTL}s"
                }
            }

            return detailed_stats
        except Exception as e:
            cache_logger.error(f"Failed to get detailed cache stats: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    async def clear_specific_key(namespace: str, key_pattern: str) -> bool:
        """Clear specific cache keys matching a pattern within a namespace"""
        try:
            if not hasattr(FastAPICache, '_backend') or FastAPICache._backend is None:
                cache_logger.warning("Cache not initialized, skipping clear operation")
                return False

            backend = FastAPICache.get_backend()
            redis_client = backend.redis

            # Build the full pattern
            full_pattern = f"zomato-cache:{namespace}:{key_pattern}"
            keys = await redis_client.keys(full_pattern)

            if keys:
                await redis_client.delete(*keys)
                cache_logger.info(f"Cleared {len(keys)} keys matching pattern: {full_pattern}")
                return True
            else:
                cache_logger.info(f"No keys found matching pattern: {full_pattern}")
                return True

        except Exception as e:
            cache_logger.error(f"Failed to clear specific keys {namespace}:{key_pattern}: {str(e)}")
            return False
    
    @staticmethod
    def cache_key_generator(*args, **kwargs) -> str:
        """Generate cache key from function arguments"""
        key_parts = []
        for arg in args:
            if hasattr(arg, '__dict__'):  # Skip complex objects like DB sessions
                continue
            key_parts.append(str(arg))
        
        for k, v in kwargs.items():
            if k in ['db']:  # Skip database session
                continue
            key_parts.append(f"{k}:{v}")
        
        return ":".join(key_parts)

def log_cache_performance(func_name: str):
    """Decorator to log cache performance"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Try to determine if this was a cache hit or miss
            # This is a simplified approach - in a real implementation,
            # you might want to modify the cache backend to track this
            cache_status = "HIT" if response_time < 10 else "MISS"
            
            cache_logger.info(
                f"Function: {func_name} | "
                f"Response Time: {response_time:.2f}ms | "
                f"Cache Status: {cache_status}"
            )
            
            return result
        return wrapper
    return decorator

class CacheInvalidator:
    """Handles advanced cache invalidation logic for maintaining data consistency"""

    @staticmethod
    async def invalidate_restaurant_caches(restaurant_id: Optional[int] = None):
        """Hierarchical invalidation for restaurant data changes"""
        try:
            if restaurant_id:
                # Clear specific restaurant cache
                await CacheManager.clear_specific_key(
                    CacheManager.RESTAURANTS_NAMESPACE,
                    f"*restaurant:{restaurant_id}*"
                )

                # Clear restaurant-menu combinations
                await CacheManager.clear_specific_key(
                    CacheManager.RESTAURANT_MENUS_NAMESPACE,
                    f"*restaurant:{restaurant_id}*"
                )

                # Clear analytics that might include this restaurant
                await CacheManager.clear_specific_key(
                    CacheManager.ANALYTICS_NAMESPACE,
                    f"*restaurant:{restaurant_id}*"
                )

                cache_logger.info(f"Hierarchically invalidated caches for restaurant {restaurant_id}")
            else:
                # Clear all restaurant-related namespaces
                await CacheManager.clear_namespace(CacheManager.RESTAURANTS_NAMESPACE)
                await CacheManager.clear_namespace(CacheManager.RESTAURANT_MENUS_NAMESPACE)
                cache_logger.info("Invalidated all restaurant caches")

            # Always clear search results (restaurant might appear in searches)
            await CacheManager.clear_namespace(CacheManager.SEARCH_RESULTS_NAMESPACE)

            # Clear restaurant list caches
            await CacheManager.clear_specific_key(
                CacheManager.RESTAURANTS_NAMESPACE,
                "*list*"
            )

        except Exception as e:
            cache_logger.error(f"Failed to invalidate restaurant caches: {str(e)}")

    @staticmethod
    async def invalidate_menu_caches(restaurant_id: Optional[int] = None, item_id: Optional[int] = None):
        """Advanced menu item cache invalidation with relationship awareness"""
        try:
            if item_id and restaurant_id:
                # Clear specific menu item
                await CacheManager.clear_specific_key(
                    CacheManager.MENU_ITEMS_NAMESPACE,
                    f"*item:{item_id}*"
                )

                # Clear all menu items for the restaurant
                await CacheManager.clear_specific_key(
                    CacheManager.MENU_ITEMS_NAMESPACE,
                    f"*restaurant:{restaurant_id}*"
                )

                cache_logger.info(f"Advanced invalidation for menu item {item_id} in restaurant {restaurant_id}")
            elif restaurant_id:
                # Clear all menu items for the restaurant
                await CacheManager.clear_specific_key(
                    CacheManager.MENU_ITEMS_NAMESPACE,
                    f"*restaurant:{restaurant_id}*"
                )
                cache_logger.info(f"Invalidated menu caches for restaurant {restaurant_id}")
            else:
                # Clear all menu items
                await CacheManager.clear_namespace(CacheManager.MENU_ITEMS_NAMESPACE)
                cache_logger.info("Invalidated all menu caches")

            # Clear restaurant-menu combinations (expensive joins affected)
            if restaurant_id:
                await CacheManager.clear_specific_key(
                    CacheManager.RESTAURANT_MENUS_NAMESPACE,
                    f"*restaurant:{restaurant_id}*"
                )
            else:
                await CacheManager.clear_namespace(CacheManager.RESTAURANT_MENUS_NAMESPACE)

            # Clear search results (menu items appear in searches)
            await CacheManager.clear_namespace(CacheManager.SEARCH_RESULTS_NAMESPACE)

            # Clear category and dietary caches (menu item might affect these)
            await CacheManager.clear_namespace(CacheManager.CATEGORIES_NAMESPACE)
            await CacheManager.clear_namespace(CacheManager.DIETARY_NAMESPACE)

            # Clear analytics (menu changes affect restaurant analytics)
            if restaurant_id:
                await CacheManager.clear_specific_key(
                    CacheManager.ANALYTICS_NAMESPACE,
                    f"*restaurant:{restaurant_id}*"
                )

            # Also invalidate restaurant caches since menu affects restaurant data
            await CacheInvalidator.invalidate_restaurant_caches(restaurant_id)

        except Exception as e:
            cache_logger.error(f"Failed to invalidate menu caches: {str(e)}")
    
    @staticmethod
    async def invalidate_search_caches(search_type: str = "all"):
        """Invalidate search-related caches"""
        try:
            if search_type == "all":
                await CacheManager.clear_namespace(CacheManager.SEARCH_RESULTS_NAMESPACE)
                await CacheManager.clear_namespace(CacheManager.CATEGORIES_NAMESPACE)
                await CacheManager.clear_namespace(CacheManager.DIETARY_NAMESPACE)
            elif search_type == "dietary":
                await CacheManager.clear_namespace(CacheManager.DIETARY_NAMESPACE)
            elif search_type == "category":
                await CacheManager.clear_namespace(CacheManager.CATEGORIES_NAMESPACE)
            elif search_type == "results":
                await CacheManager.clear_namespace(CacheManager.SEARCH_RESULTS_NAMESPACE)

            cache_logger.info(f"Invalidated search caches: {search_type}")
        except Exception as e:
            cache_logger.error(f"Failed to invalidate search caches: {str(e)}")

    @staticmethod
    async def invalidate_analytics_caches(restaurant_id: Optional[int] = None):
        """Invalidate analytics and aggregation caches"""
        try:
            if restaurant_id:
                await CacheManager.clear_specific_key(
                    CacheManager.ANALYTICS_NAMESPACE,
                    f"*restaurant:{restaurant_id}*"
                )
                cache_logger.info(f"Invalidated analytics caches for restaurant {restaurant_id}")
            else:
                await CacheManager.clear_namespace(CacheManager.ANALYTICS_NAMESPACE)
                cache_logger.info("Invalidated all analytics caches")

        except Exception as e:
            cache_logger.error(f"Failed to invalidate analytics caches: {str(e)}")

    @staticmethod
    async def invalidate_customer_caches(customer_id: Optional[int] = None):
        """Invalidate customer-related caches"""
        try:
            if customer_id:
                await CacheManager.clear_specific_key(
                    CacheManager.CUSTOMERS_NAMESPACE,
                    f"*customer:{customer_id}*"
                )
                cache_logger.info(f"Invalidated caches for customer {customer_id}")
            else:
                await CacheManager.clear_namespace(CacheManager.CUSTOMERS_NAMESPACE)
                cache_logger.info("Invalidated all customer caches")

        except Exception as e:
            cache_logger.error(f"Failed to invalidate customer caches: {str(e)}")

    @staticmethod
    async def invalidate_order_caches(customer_id: Optional[int] = None, restaurant_id: Optional[int] = None):
        """Invalidate order-related caches with cascading effects"""
        try:
            await CacheManager.clear_namespace(CacheManager.ORDERS_NAMESPACE)

            # Orders affect customer and restaurant analytics
            if customer_id:
                await CacheInvalidator.invalidate_customer_caches(customer_id)
            if restaurant_id:
                await CacheInvalidator.invalidate_restaurant_caches(restaurant_id)
                await CacheInvalidator.invalidate_analytics_caches(restaurant_id)

            cache_logger.info("Invalidated order-related caches with cascading effects")

        except Exception as e:
            cache_logger.error(f"Failed to invalidate order caches: {str(e)}")

    @staticmethod
    async def invalidate_review_caches(customer_id: Optional[int] = None, restaurant_id: Optional[int] = None):
        """Invalidate review-related caches with cascading effects"""
        try:
            await CacheManager.clear_namespace(CacheManager.REVIEWS_NAMESPACE)

            # Reviews affect customer and restaurant data and analytics
            if customer_id:
                await CacheInvalidator.invalidate_customer_caches(customer_id)
            if restaurant_id:
                await CacheInvalidator.invalidate_restaurant_caches(restaurant_id)
                await CacheInvalidator.invalidate_analytics_caches(restaurant_id)

            cache_logger.info("Invalidated review-related caches with cascading effects")

        except Exception as e:
            cache_logger.error(f"Failed to invalidate review caches: {str(e)}")


class CacheWarmer:
    """Handles proactive cache warming and smart refresh strategies"""

    @staticmethod
    async def warm_popular_data(db_session):
        """Warm cache with frequently accessed data"""
        try:
            from crud import RestaurantCRUD, MenuItemCRUD

            warming_stats = {
                "restaurants_warmed": 0,
                "menu_items_warmed": 0,
                "analytics_warmed": 0,
                "start_time": time.time()
            }

            # Warm restaurant list (most accessed)
            restaurants, _ = await RestaurantCRUD.get_restaurants(db_session, per_page=50)
            warming_stats["restaurants_warmed"] = len(restaurants)

            # Warm active restaurants
            active_restaurants, _ = await RestaurantCRUD.get_restaurants(db_session, is_active=True, per_page=30)

            # Warm menu items for top restaurants
            menu_count = 0
            for restaurant in restaurants[:15]:  # Top 15 restaurants
                menu_items, _ = await MenuItemCRUD.get_menu_items(db_session, restaurant_id=restaurant.id, per_page=20)
                menu_count += len(menu_items)

            warming_stats["menu_items_warmed"] = menu_count
            warming_stats["total_time"] = time.time() - warming_stats["start_time"]

            cache_logger.info(f"Cache warming completed: {warming_stats}")
            return warming_stats

        except Exception as e:
            cache_logger.error(f"Cache warming failed: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    async def smart_refresh_strategy(db_session, namespace: str):
        """Implement smart refresh for frequently accessed but stale data"""
        try:
            if not hasattr(FastAPICache, '_backend') or FastAPICache._backend is None:
                cache_logger.warning("Cache not available for smart refresh")
                return False

            backend = FastAPICache.get_backend()
            redis_client = backend.redis

            # Get keys in namespace that are close to expiring
            pattern = f"zomato-cache:{namespace}:*"
            keys = await redis_client.keys(pattern)

            refresh_candidates = []
            for key in keys:
                ttl = await redis_client.ttl(key)
                # Refresh if TTL is less than 25% of original
                if 0 < ttl < (CacheManager.RESTAURANT_DETAIL_TTL * 0.25):
                    refresh_candidates.append(key)

            if refresh_candidates:
                cache_logger.info(f"Smart refresh identified {len(refresh_candidates)} candidates in {namespace}")
                # Here you would implement the refresh logic based on the key patterns
                return True

            return False

        except Exception as e:
            cache_logger.error(f"Smart refresh failed for {namespace}: {str(e)}")
            return False


class CacheMetrics:
    """Advanced cache performance monitoring and metrics collection"""

    @staticmethod
    async def calculate_hit_ratio() -> dict:
        """Calculate cache hit ratio from Redis stats"""
        try:
            if not hasattr(FastAPICache, '_backend') or FastAPICache._backend is None:
                return {"error": "Cache not available"}

            backend = FastAPICache.get_backend()
            redis_client = backend.redis
            info = await redis_client.info()

            hits = info.get("keyspace_hits", 0)
            misses = info.get("keyspace_misses", 0)
            total_requests = hits + misses

            if total_requests == 0:
                return {"hit_ratio": 0, "total_requests": 0}

            hit_ratio = (hits / total_requests) * 100

            return {
                "hit_ratio_percent": round(hit_ratio, 2),
                "cache_hits": hits,
                "cache_misses": misses,
                "total_requests": total_requests,
                "efficiency_rating": "Excellent" if hit_ratio > 80 else "Good" if hit_ratio > 60 else "Needs Improvement"
            }

        except Exception as e:
            cache_logger.error(f"Failed to calculate hit ratio: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    async def get_memory_usage_analysis() -> dict:
        """Analyze Redis memory usage patterns"""
        try:
            if not hasattr(FastAPICache, '_backend') or FastAPICache._backend is None:
                return {"error": "Cache not available"}

            backend = FastAPICache.get_backend()
            redis_client = backend.redis
            info = await redis_client.info()

            # Get memory info
            used_memory = info.get("used_memory", 0)
            used_memory_human = info.get("used_memory_human", "0B")
            max_memory = info.get("maxmemory", 0)

            # Calculate memory efficiency
            keys = await redis_client.keys("zomato-cache:*")
            avg_key_size = used_memory / len(keys) if keys else 0

            analysis = {
                "total_memory_used": used_memory,
                "memory_used_human": used_memory_human,
                "max_memory_configured": max_memory,
                "memory_utilization_percent": round((used_memory / max_memory) * 100, 2) if max_memory > 0 else 0,
                "total_cache_keys": len(keys),
                "average_key_size_bytes": round(avg_key_size, 2),
                "memory_efficiency": "Good" if avg_key_size < 1000 else "Review Large Keys"
            }

            return analysis

        except Exception as e:
            cache_logger.error(f"Failed to analyze memory usage: {str(e)}")
            return {"error": str(e)}


class AdvancedCachePatterns:
    """Implementation of enterprise cache patterns"""

    @staticmethod
    async def write_through_cache(namespace: CacheNamespace, key: str, data: Any, update_func: Callable):
        """Write-through caching pattern - update database and cache simultaneously"""
        try:
            # Update database first
            result = await update_func(data)

            # Update cache immediately
            if hasattr(FastAPICache, '_backend') and FastAPICache._backend is not None:
                backend = FastAPICache.get_backend()
                ttl = cache_config.get_ttl(namespace)
                cache_key = cache_config.get_cache_key(namespace, key)

                await backend.set(cache_key, result, expire=ttl)
                cache_logger.info(f"Write-through cache updated for key: {cache_key}")

            return result

        except Exception as e:
            cache_logger.error(f"Write-through cache failed: {str(e)}")
            raise

    @staticmethod
    async def cache_aside_get(namespace: CacheNamespace, key: str, fetch_func: Callable, *args, **kwargs):
        """Cache-aside pattern - check cache first, then database"""
        try:
            if not hasattr(FastAPICache, '_backend') or FastAPICache._backend is None:
                return await fetch_func(*args, **kwargs)

            backend = FastAPICache.get_backend()
            cache_key = cache_config.get_cache_key(namespace, key)

            # Try cache first
            cached_result = await backend.get(cache_key)
            if cached_result is not None:
                cache_logger.debug(f"Cache-aside HIT for key: {cache_key}")
                return cached_result

            # Cache miss - fetch from database
            cache_logger.debug(f"Cache-aside MISS for key: {cache_key}")
            result = await fetch_func(*args, **kwargs)

            # Store in cache
            ttl = cache_config.get_ttl(namespace)
            await backend.set(cache_key, result, expire=ttl)

            return result

        except Exception as e:
            cache_logger.error(f"Cache-aside pattern failed: {str(e)}")
            return await fetch_func(*args, **kwargs)

    @staticmethod
    async def refresh_ahead_cache(namespace: CacheNamespace, key: str, fetch_func: Callable, refresh_threshold: float = 0.25):
        """Refresh-ahead caching - refresh cache before expiration"""
        try:
            if not hasattr(FastAPICache, '_backend') or FastAPICache._backend is None:
                return await fetch_func()

            backend = FastAPICache.get_backend()
            redis_client = backend.redis
            cache_key = cache_config.get_cache_key(namespace, key)

            # Check TTL
            ttl = await redis_client.ttl(cache_key)
            original_ttl = cache_config.get_ttl(namespace)

            # If TTL is less than threshold, refresh in background
            if 0 < ttl < (original_ttl * refresh_threshold):
                cache_logger.info(f"Refresh-ahead triggered for key: {cache_key}")

                # Fetch new data
                fresh_data = await fetch_func()

                # Update cache with fresh data
                await backend.set(cache_key, fresh_data, expire=original_ttl)

                return fresh_data

            # Normal cache retrieval
            cached_result = await backend.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Cache miss - fetch and store
            result = await fetch_func()
            await backend.set(cache_key, result, expire=original_ttl)

            return result

        except Exception as e:
            cache_logger.error(f"Refresh-ahead cache failed: {str(e)}")
            return await fetch_func()

    @staticmethod
    async def multi_level_cache(l1_namespace: CacheNamespace, l2_namespace: CacheNamespace, key: str, fetch_func: Callable):
        """Multi-level caching with L1 (fast, short TTL) and L2 (slower, long TTL)"""
        try:
            if not hasattr(FastAPICache, '_backend') or FastAPICache._backend is None:
                return await fetch_func()

            backend = FastAPICache.get_backend()

            # L1 Cache (fast, short TTL)
            l1_key = cache_config.get_cache_key(l1_namespace, f"l1:{key}")
            l1_result = await backend.get(l1_key)

            if l1_result is not None:
                cache_logger.debug(f"L1 cache HIT for key: {l1_key}")
                return l1_result

            # L2 Cache (slower, long TTL)
            l2_key = cache_config.get_cache_key(l2_namespace, f"l2:{key}")
            l2_result = await backend.get(l2_key)

            if l2_result is not None:
                cache_logger.debug(f"L2 cache HIT for key: {l2_key}")

                # Populate L1 cache
                l1_ttl = cache_config.get_ttl(l1_namespace)
                await backend.set(l1_key, l2_result, expire=l1_ttl)

                return l2_result

            # Cache miss - fetch from source
            cache_logger.debug(f"Multi-level cache MISS for key: {key}")
            result = await fetch_func()

            # Populate both caches
            l1_ttl = cache_config.get_ttl(l1_namespace)
            l2_ttl = cache_config.get_ttl(l2_namespace)

            await backend.set(l1_key, result, expire=l1_ttl)
            await backend.set(l2_key, result, expire=l2_ttl)

            return result

        except Exception as e:
            cache_logger.error(f"Multi-level cache failed: {str(e)}")
            return await fetch_func()


class CacheHealthMonitor:
    """Advanced cache health monitoring and alerting"""

    @staticmethod
    async def check_cache_health() -> Dict[str, Any]:
        """Comprehensive cache health check"""
        try:
            if not hasattr(FastAPICache, '_backend') or FastAPICache._backend is None:
                return {
                    "status": "unhealthy",
                    "error": "Cache backend not available",
                    "timestamp": time.time()
                }

            backend = FastAPICache.get_backend()
            redis_client = backend.redis

            # Test Redis connectivity
            start_time = time.time()
            await redis_client.ping()
            ping_time = (time.time() - start_time) * 1000

            # Get Redis info
            info = await redis_client.info()

            # Calculate health metrics
            hit_ratio_data = await CacheMetrics.calculate_hit_ratio()
            memory_data = await CacheMetrics.get_memory_usage_analysis()

            # Determine health status
            health_issues = []

            if ping_time > cache_config.performance_thresholds["response_time_warning"]:
                health_issues.append(f"High ping time: {ping_time:.2f}ms")

            if "hit_ratio_percent" in hit_ratio_data:
                hit_ratio = hit_ratio_data["hit_ratio_percent"]
                if hit_ratio < cache_config.performance_thresholds["hit_ratio_critical"] * 100:
                    health_issues.append(f"Critical hit ratio: {hit_ratio}%")
                elif hit_ratio < cache_config.performance_thresholds["hit_ratio_warning"] * 100:
                    health_issues.append(f"Low hit ratio: {hit_ratio}%")

            if "memory_utilization_percent" in memory_data:
                memory_usage = memory_data["memory_utilization_percent"]
                if memory_usage > cache_config.performance_thresholds["memory_usage_critical"] * 100:
                    health_issues.append(f"Critical memory usage: {memory_usage}%")
                elif memory_usage > cache_config.performance_thresholds["memory_usage_warning"] * 100:
                    health_issues.append(f"High memory usage: {memory_usage}%")

            # Determine overall status
            if not health_issues:
                status = "healthy"
            elif any("Critical" in issue for issue in health_issues):
                status = "critical"
            else:
                status = "warning"

            return {
                "status": status,
                "ping_time_ms": round(ping_time, 2),
                "redis_version": info.get("redis_version", "Unknown"),
                "uptime_seconds": info.get("uptime_in_seconds", 0),
                "connected_clients": info.get("connected_clients", 0),
                "health_issues": health_issues,
                "performance_metrics": {
                    "hit_ratio": hit_ratio_data,
                    "memory_usage": memory_data
                },
                "timestamp": time.time()
            }

        except Exception as e:
            cache_logger.error(f"Cache health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
