from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import time
from database import get_db
from schemas import Restaurant
from crud import RestaurantCRUD, MenuItemCRUD
from utils.cache_manager import CacheManager, CacheInvalidator, CacheWarmer, CacheMetrics, CacheHealthMonitor, AdvancedCachePatterns
from config import CacheNamespace, cache_config

router = APIRouter(prefix="/cache", tags=["cache-management"])

@router.get("/stats")
async def get_cache_stats():
    """Get basic cache statistics and information"""
    try:
        stats = await CacheManager.get_cache_stats()
        if "error" in stats:
            return {
                "status": "cache_unavailable",
                "message": stats.get("message", "Cache not available"),
                "cache_stats": stats,
                "timestamp": time.time()
            }
        return {
            "status": "success",
            "cache_stats": stats,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cache stats: {str(e)}")

@router.get("/stats/detailed")
async def get_detailed_cache_stats():
    """Get detailed cache statistics by namespace with TTL information"""
    try:
        detailed_stats = await CacheManager.get_detailed_cache_stats()
        if "error" in detailed_stats:
            return {
                "status": "cache_unavailable",
                "message": detailed_stats.get("message", "Cache not available"),
                "detailed_stats": detailed_stats,
                "timestamp": time.time()
            }
        return {
            "status": "success",
            "detailed_stats": detailed_stats,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get detailed cache stats: {str(e)}")

@router.delete("/clear")
async def clear_entire_cache():
    """Clear entire cache"""
    try:
        success = await CacheManager.clear_all_cache()
        if success:
            return {
                "status": "success",
                "message": "Entire cache cleared successfully",
                "timestamp": time.time()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear cache")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

@router.delete("/clear/restaurants")
async def clear_restaurant_cache():
    """Clear only restaurant-related caches"""
    try:
        success = await CacheManager.clear_namespace(CacheManager.RESTAURANTS_NAMESPACE)
        if success:
            return {
                "status": "success",
                "message": "Restaurant cache cleared successfully",
                "namespace": CacheManager.RESTAURANTS_NAMESPACE,
                "timestamp": time.time()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear restaurant cache")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear restaurant cache: {str(e)}")

@router.delete("/clear/menu-items")
async def clear_menu_items_cache():
    """Clear only menu items cache"""
    try:
        success = await CacheManager.clear_namespace(CacheManager.MENU_ITEMS_NAMESPACE)
        if success:
            return {
                "status": "success",
                "message": "Menu items cache cleared successfully",
                "namespace": CacheManager.MENU_ITEMS_NAMESPACE,
                "timestamp": time.time()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear menu items cache")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear menu items cache: {str(e)}")

@router.delete("/clear/customers")
async def clear_customers_cache():
    """Clear only customers cache"""
    try:
        success = await CacheManager.clear_namespace(CacheManager.CUSTOMERS_NAMESPACE)
        if success:
            return {
                "status": "success",
                "message": "Customers cache cleared successfully",
                "namespace": CacheManager.CUSTOMERS_NAMESPACE,
                "timestamp": time.time()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear customers cache")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear customers cache: {str(e)}")

@router.delete("/clear/orders")
async def clear_orders_cache():
    """Clear only orders cache"""
    try:
        success = await CacheManager.clear_namespace(CacheManager.ORDERS_NAMESPACE)
        if success:
            return {
                "status": "success",
                "message": "Orders cache cleared successfully",
                "namespace": CacheManager.ORDERS_NAMESPACE,
                "timestamp": time.time()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear orders cache")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear orders cache: {str(e)}")

@router.delete("/clear/reviews")
async def clear_reviews_cache():
    """Clear only reviews cache"""
    try:
        success = await CacheManager.clear_namespace(CacheManager.REVIEWS_NAMESPACE)
        if success:
            return {
                "status": "success",
                "message": "Reviews cache cleared successfully",
                "namespace": CacheManager.REVIEWS_NAMESPACE,
                "timestamp": time.time()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear reviews cache")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear reviews cache: {str(e)}")

@router.delete("/clear/search")
async def clear_search_cache():
    """Clear search result caches"""
    try:
        await CacheInvalidator.invalidate_search_caches("all")
        return {
            "status": "success",
            "message": "Search caches cleared successfully",
            "cleared_namespaces": [
                CacheManager.SEARCH_RESULTS_NAMESPACE,
                CacheManager.CATEGORIES_NAMESPACE,
                CacheManager.DIETARY_NAMESPACE
            ],
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear search cache: {str(e)}")

@router.delete("/clear/analytics")
async def clear_analytics_cache():
    """Clear analytics and aggregation caches"""
    try:
        await CacheInvalidator.invalidate_analytics_caches()
        return {
            "status": "success",
            "message": "Analytics cache cleared successfully",
            "namespace": CacheManager.ANALYTICS_NAMESPACE,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear analytics cache: {str(e)}")

@router.delete("/clear/restaurant-menus")
async def clear_restaurant_menus_cache():
    """Clear restaurant-menu combination caches"""
    try:
        success = await CacheManager.clear_namespace(CacheManager.RESTAURANT_MENUS_NAMESPACE)
        if success:
            return {
                "status": "success",
                "message": "Restaurant-menu combination cache cleared successfully",
                "namespace": CacheManager.RESTAURANT_MENUS_NAMESPACE,
                "timestamp": time.time()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear restaurant-menus cache")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear restaurant-menus cache: {str(e)}")

@router.get("/demo/cache-test/{restaurant_id}")
async def cache_performance_demo(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Demonstrate cache performance with timing"""
    try:
        # First request - should be cache miss
        start_time = time.time()
        restaurant = await RestaurantCRUD.get_restaurant(db, restaurant_id)
        first_request_time = (time.time() - start_time) * 1000
        
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        # Second request - should be cache hit (simulate by calling again)
        start_time = time.time()
        restaurant_cached = await RestaurantCRUD.get_restaurant(db, restaurant_id)
        second_request_time = (time.time() - start_time) * 1000
        
        return {
            "restaurant_id": restaurant_id,
            "restaurant_name": restaurant.name,
            "performance_test": {
                "first_request_ms": round(first_request_time, 2),
                "second_request_ms": round(second_request_time, 2),
                "performance_improvement": f"{round((first_request_time - second_request_time) / first_request_time * 100, 2)}%",
                "cache_status": "HIT" if second_request_time < 10 else "MISS"
            },
            "timestamp": time.time()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache demo failed: {str(e)}")

@router.get("/demo/performance-comparison")
async def performance_comparison(db: AsyncSession = Depends(get_db)):
    """Compare cached vs non-cached performance across multiple operations"""
    try:
        results = {
            "test_timestamp": time.time(),
            "operations": []
        }

        # Test 1: Restaurant list
        # Clear cache first
        await CacheManager.clear_namespace(CacheManager.RESTAURANTS_NAMESPACE)

        # Non-cached request
        start_time = time.time()
        restaurants, _ = await RestaurantCRUD.get_restaurants(db, per_page=20)
        non_cached_time = (time.time() - start_time) * 1000

        # Cached request (second call)
        start_time = time.time()
        restaurants_cached, _ = await RestaurantCRUD.get_restaurants(db, per_page=20)
        cached_time = (time.time() - start_time) * 1000

        results["operations"].append({
            "operation": "Restaurant List (20 items)",
            "non_cached_ms": round(non_cached_time, 2),
            "cached_ms": round(cached_time, 2),
            "improvement_percent": round((non_cached_time - cached_time) / non_cached_time * 100, 2) if non_cached_time > 0 else 0,
            "speed_multiplier": round(non_cached_time / cached_time, 2) if cached_time > 0 else 0
        })

        # Test 2: Menu items search
        await CacheManager.clear_namespace(CacheManager.SEARCH_RESULTS_NAMESPACE)

        # Non-cached search
        start_time = time.time()
        menu_items, _ = await MenuItemCRUD.get_menu_items(db, search="pizza", per_page=10)
        non_cached_search_time = (time.time() - start_time) * 1000

        # Cached search
        start_time = time.time()
        menu_items_cached, _ = await MenuItemCRUD.get_menu_items(db, search="pizza", per_page=10)
        cached_search_time = (time.time() - start_time) * 1000

        results["operations"].append({
            "operation": "Menu Items Search ('pizza')",
            "non_cached_ms": round(non_cached_search_time, 2),
            "cached_ms": round(cached_search_time, 2),
            "improvement_percent": round((non_cached_search_time - cached_search_time) / non_cached_search_time * 100, 2) if non_cached_search_time > 0 else 0,
            "speed_multiplier": round(non_cached_search_time / cached_search_time, 2) if cached_search_time > 0 else 0
        })

        # Calculate overall performance
        total_non_cached = sum(op["non_cached_ms"] for op in results["operations"])
        total_cached = sum(op["cached_ms"] for op in results["operations"])

        results["summary"] = {
            "total_operations": len(results["operations"]),
            "total_non_cached_ms": round(total_non_cached, 2),
            "total_cached_ms": round(total_cached, 2),
            "overall_improvement_percent": round((total_non_cached - total_cached) / total_non_cached * 100, 2) if total_non_cached > 0 else 0,
            "overall_speed_multiplier": round(total_non_cached / total_cached, 2) if total_cached > 0 else 0
        }

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance comparison failed: {str(e)}")

@router.post("/warm")
async def warm_cache(db: AsyncSession = Depends(get_db)):
    """Warm up cache with frequently accessed data"""
    try:
        warming_results = {
            "timestamp": time.time(),
            "warmed_data": []
        }

        # Warm restaurant list
        start_time = time.time()
        restaurants, _ = await RestaurantCRUD.get_restaurants(db, per_page=50)
        warming_results["warmed_data"].append({
            "type": "restaurant_list",
            "count": len(restaurants),
            "time_ms": round((time.time() - start_time) * 1000, 2)
        })

        # Warm active restaurants
        start_time = time.time()
        active_restaurants, _ = await RestaurantCRUD.get_restaurants(db, is_active=True, per_page=50)
        warming_results["warmed_data"].append({
            "type": "active_restaurants",
            "count": len(active_restaurants),
            "time_ms": round((time.time() - start_time) * 1000, 2)
        })

        # Warm menu items for top restaurants
        menu_warming_count = 0
        for restaurant in restaurants[:10]:  # Top 10 restaurants
            start_time = time.time()
            menu_items, _ = await MenuItemCRUD.get_menu_items(db, restaurant_id=restaurant.id, per_page=20)
            menu_warming_count += len(menu_items)

        warming_results["warmed_data"].append({
            "type": "menu_items_top_restaurants",
            "count": menu_warming_count,
            "restaurants_warmed": min(10, len(restaurants)),
            "time_ms": round((time.time() - start_time) * 1000, 2)
        })

        # Calculate totals
        total_items = sum(item["count"] for item in warming_results["warmed_data"])
        total_time = sum(item["time_ms"] for item in warming_results["warmed_data"])

        warming_results["summary"] = {
            "total_items_warmed": total_items,
            "total_time_ms": round(total_time, 2),
            "average_time_per_item_ms": round(total_time / total_items, 2) if total_items > 0 else 0
        }

        return {
            "status": "success",
            "message": "Cache warming completed successfully",
            "results": warming_results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache warming failed: {str(e)}")

@router.get("/metrics/hit-ratio")
async def get_cache_hit_ratio():
    """Get cache hit/miss ratio and efficiency metrics"""
    try:
        metrics = await CacheMetrics.calculate_hit_ratio()
        if "error" in metrics:
            return {
                "status": "cache_unavailable",
                "message": "Cache metrics not available",
                "metrics": metrics,
                "timestamp": time.time()
            }

        return {
            "status": "success",
            "metrics": metrics,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get hit ratio: {str(e)}")

@router.get("/metrics/memory-usage")
async def get_memory_usage_analysis():
    """Get detailed memory usage analysis"""
    try:
        analysis = await CacheMetrics.get_memory_usage_analysis()
        if "error" in analysis:
            return {
                "status": "cache_unavailable",
                "message": "Memory analysis not available",
                "analysis": analysis,
                "timestamp": time.time()
            }

        return {
            "status": "success",
            "memory_analysis": analysis,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze memory usage: {str(e)}")

@router.post("/warm/popular")
async def warm_popular_cache(db: AsyncSession = Depends(get_db)):
    """Warm cache with popular/frequently accessed data using smart strategies"""
    try:
        warming_stats = await CacheWarmer.warm_popular_data(db)

        if "error" in warming_stats:
            return {
                "status": "error",
                "message": "Cache warming failed",
                "error": warming_stats["error"],
                "timestamp": time.time()
            }

        return {
            "status": "success",
            "message": "Popular data cache warming completed",
            "warming_statistics": warming_stats,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Popular cache warming failed: {str(e)}")

@router.get("/performance/comprehensive-report")
async def get_comprehensive_performance_report(db: AsyncSession = Depends(get_db)):
    """Get comprehensive cache performance report with all metrics"""
    try:
        # Gather all performance metrics
        basic_stats = await CacheManager.get_cache_stats()
        detailed_stats = await CacheManager.get_detailed_cache_stats()
        hit_ratio = await CacheMetrics.calculate_hit_ratio()
        memory_analysis = await CacheMetrics.get_memory_usage_analysis()

        # Run a quick performance test
        performance_test_start = time.time()
        restaurants, _ = await RestaurantCRUD.get_restaurants(db, per_page=10)
        performance_test_time = (time.time() - performance_test_start) * 1000

        report = {
            "report_timestamp": time.time(),
            "cache_availability": "available" if "error" not in basic_stats else "unavailable",
            "basic_statistics": basic_stats,
            "detailed_statistics": detailed_stats,
            "performance_metrics": {
                "hit_ratio_analysis": hit_ratio,
                "memory_usage_analysis": memory_analysis,
                "sample_query_time_ms": round(performance_test_time, 2),
                "cache_status": "HIT" if performance_test_time < 10 else "MISS"
            },
            "recommendations": []
        }

        # Add performance recommendations
        if "hit_ratio_percent" in hit_ratio:
            if hit_ratio["hit_ratio_percent"] < 60:
                report["recommendations"].append("Consider increasing TTL values or reviewing cache invalidation strategy")
            if hit_ratio["hit_ratio_percent"] > 90:
                report["recommendations"].append("Excellent cache performance - consider expanding cached operations")

        if "memory_utilization_percent" in memory_analysis:
            if memory_analysis["memory_utilization_percent"] > 80:
                report["recommendations"].append("High memory usage - consider reducing TTL or implementing cache size limits")
            if memory_analysis["memory_utilization_percent"] < 20:
                report["recommendations"].append("Low memory usage - opportunity to cache more data")

        if not report["recommendations"]:
            report["recommendations"].append("Cache performance is optimal")

        return {
            "status": "success",
            "comprehensive_report": report
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate performance report: {str(e)}")

@router.get("/health")
async def get_cache_health():
    """Redis health check with comprehensive diagnostics"""
    try:
        health_data = await CacheHealthMonitor.check_cache_health()

        return {
            "status": "success",
            "health_check": health_data,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/stats/namespaces")
async def get_namespace_statistics():
    """Get detailed statistics by namespace"""
    try:
        detailed_stats = await CacheManager.get_detailed_cache_stats()

        if "error" in detailed_stats:
            return {
                "status": "cache_unavailable",
                "message": detailed_stats.get("message", "Cache not available"),
                "timestamp": time.time()
            }

        # Enhance with namespace-specific insights
        namespace_insights = {}
        for namespace, details in detailed_stats.get("namespace_details", {}).items():
            key_count = details.get("key_count", 0)
            memory_estimate = details.get("memory_estimate", 0)

            # Calculate insights
            avg_key_size = memory_estimate / key_count if key_count > 0 else 0

            namespace_insights[namespace] = {
                "key_count": key_count,
                "memory_estimate_bytes": memory_estimate,
                "memory_estimate_human": f"{memory_estimate / 1024:.2f} KB" if memory_estimate > 0 else "0 B",
                "average_key_size_bytes": round(avg_key_size, 2),
                "efficiency_rating": "Good" if avg_key_size < 1000 else "Review" if avg_key_size < 5000 else "Optimize"
            }

        return {
            "status": "success",
            "namespace_statistics": namespace_insights,
            "overview": detailed_stats.get("overview", {}),
            "timestamp": time.time()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get namespace statistics: {str(e)}")

@router.get("/memory-usage")
async def get_memory_usage_details():
    """Get detailed memory usage analysis"""
    try:
        memory_analysis = await CacheMetrics.get_memory_usage_analysis()

        if "error" in memory_analysis:
            return {
                "status": "cache_unavailable",
                "message": "Memory analysis not available",
                "timestamp": time.time()
            }

        # Add recommendations based on usage
        recommendations = []

        if memory_analysis.get("memory_utilization_percent", 0) > 80:
            recommendations.append("Consider increasing Redis memory limit or reducing TTL values")

        if memory_analysis.get("average_key_size_bytes", 0) > 5000:
            recommendations.append("Large average key size detected - review data structures")

        if memory_analysis.get("total_cache_keys", 0) > 100000:
            recommendations.append("High key count - consider implementing key expiration policies")

        if not recommendations:
            recommendations.append("Memory usage is optimal")

        return {
            "status": "success",
            "memory_analysis": memory_analysis,
            "recommendations": recommendations,
            "timestamp": time.time()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get memory usage: {str(e)}")

@router.delete("/clear/expired")
async def clear_expired_keys():
    """Remove expired keys from cache"""
    try:
        if not hasattr(FastAPICache, '_backend') or FastAPICache._backend is None:
            return {
                "status": "cache_unavailable",
                "message": "Cache not available",
                "timestamp": time.time()
            }

        backend = FastAPICache.get_backend()
        redis_client = backend.redis

        # Get all keys with our prefix
        keys = await redis_client.keys("zomato-*:*")
        expired_keys = []

        for key in keys:
            ttl = await redis_client.ttl(key)
            if ttl == -1:  # Key exists but has no expiration
                # Check if it's an old key that should have expired
                expired_keys.append(key)

        # Remove expired keys
        if expired_keys:
            await redis_client.delete(*expired_keys)

        return {
            "status": "success",
            "message": f"Cleared {len(expired_keys)} expired keys",
            "expired_keys_count": len(expired_keys),
            "timestamp": time.time()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear expired keys: {str(e)}")

@router.post("/warm/{namespace}")
async def warm_specific_namespace(
    namespace: str,
    db: AsyncSession = Depends(get_db)
):
    """Warm specific cache namespace"""
    try:
        warming_results = {"namespace": namespace, "items_warmed": 0, "time_taken_ms": 0}
        start_time = time.time()

        if namespace == "restaurants":
            restaurants, _ = await RestaurantCRUD.get_restaurants(db, per_page=50)
            warming_results["items_warmed"] = len(restaurants)

        elif namespace == "menu-items":
            menu_items, _ = await MenuItemCRUD.get_menu_items(db, per_page=100)
            warming_results["items_warmed"] = len(menu_items)

        elif namespace == "analytics":
            # Warm analytics data
            from routes.analytics import get_daily_revenue, get_customer_behavior_analytics
            await get_daily_revenue("2024-01-01", db)
            await get_customer_behavior_analytics("7d", db)
            warming_results["items_warmed"] = 2

        else:
            raise HTTPException(status_code=400, detail=f"Unknown namespace: {namespace}")

        warming_results["time_taken_ms"] = round((time.time() - start_time) * 1000, 2)

        return {
            "status": "success",
            "message": f"Cache warming completed for namespace: {namespace}",
            "warming_results": warming_results,
            "timestamp": time.time()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to warm namespace {namespace}: {str(e)}")

@router.get("/info")
async def get_cache_info():
    """Get comprehensive cache configuration information"""
    return {
        "cache_configuration": {
            "backend": "Redis",
            "prefix": "zomato-cache",
            "strategy": "Multi-Level Caching with Relationship Awareness",
            "namespaces": {
                "restaurants": CacheManager.RESTAURANTS_NAMESPACE,
                "menu_items": CacheManager.MENU_ITEMS_NAMESPACE,
                "restaurant_menus": CacheManager.RESTAURANT_MENUS_NAMESPACE,
                "search_results": CacheManager.SEARCH_RESULTS_NAMESPACE,
                "analytics": CacheManager.ANALYTICS_NAMESPACE,
                "categories": CacheManager.CATEGORIES_NAMESPACE,
                "dietary": CacheManager.DIETARY_NAMESPACE,
                "customers": CacheManager.CUSTOMERS_NAMESPACE,
                "orders": CacheManager.ORDERS_NAMESPACE,
                "reviews": CacheManager.REVIEWS_NAMESPACE
            },
            "multi_level_ttl_strategy": {
                "basic_restaurant_data": {
                    "ttl": "10 minutes",
                    "reason": "Stable data, infrequent changes",
                    "settings": {
                        "restaurant_detail": f"{CacheManager.RESTAURANT_DETAIL_TTL}s",
                        "restaurant_list": f"{CacheManager.RESTAURANT_LIST_TTL}s",
                        "restaurant_active": f"{CacheManager.RESTAURANT_ACTIVE_TTL}s"
                    }
                },
                "menu_items": {
                    "ttl": "8 minutes",
                    "reason": "More dynamic, frequent updates",
                    "settings": {
                        "menu_items": f"{CacheManager.MENU_ITEMS_TTL}s",
                        "menu_item_detail": f"{CacheManager.MENU_ITEM_DETAIL_TTL}s",
                        "menu_category": f"{CacheManager.MENU_CATEGORY_TTL}s"
                    }
                },
                "expensive_joins": {
                    "ttl": "15 minutes",
                    "reason": "Complex queries, expensive to compute",
                    "settings": {
                        "restaurant_with_menu": f"{CacheManager.RESTAURANT_WITH_MENU_TTL}s",
                        "restaurant_menu_list": f"{CacheManager.RESTAURANT_MENU_LIST_TTL}s"
                    }
                },
                "search_results": {
                    "ttl": "5 minutes",
                    "reason": "Frequently changing, user-specific",
                    "settings": {
                        "restaurant_search": f"{CacheManager.RESTAURANT_SEARCH_TTL}s",
                        "menu_search": f"{CacheManager.MENU_SEARCH_TTL}s",
                        "dietary_search": f"{CacheManager.DIETARY_SEARCH_TTL}s",
                        "category_search": f"{CacheManager.CATEGORY_SEARCH_TTL}s"
                    }
                },
                "analytics_and_aggregations": {
                    "ttl": "20 minutes",
                    "reason": "Expensive calculations, acceptable staleness",
                    "settings": {
                        "analytics": f"{CacheManager.ANALYTICS_TTL}s",
                        "aggregation": f"{CacheManager.AGGREGATION_TTL}s",
                        "popular_items": f"{CacheManager.POPULAR_ITEMS_TTL}s"
                    }
                },
                "business_logic": {
                    "ttl": "12 minutes",
                    "reason": "Calculated fields, moderate update frequency",
                    "settings": {
                        "calculated_fields": f"{CacheManager.CALCULATED_FIELDS_TTL}s",
                        "rating_aggregation": f"{CacheManager.RATING_AGGREGATION_TTL}s"
                    }
                }
            }
        },
        "advanced_invalidation_rules": {
            "hierarchical_invalidation": {
                "restaurant_update": [
                    "Clear specific restaurant cache",
                    "Clear restaurant-menu combinations",
                    "Clear search results",
                    "Clear analytics for restaurant",
                    "Clear restaurant list caches"
                ],
                "menu_item_update": [
                    "Clear specific menu item",
                    "Clear restaurant menu items",
                    "Clear restaurant-menu combinations",
                    "Clear search results",
                    "Clear category and dietary caches",
                    "Clear restaurant analytics",
                    "Cascade to restaurant invalidation"
                ]
            },
            "relationship_awareness": {
                "menu_changes_affect": ["restaurants", "search", "analytics", "categories", "dietary"],
                "restaurant_changes_affect": ["menus", "search", "analytics"],
                "search_optimization": "Separate namespace for fast clearing"
            }
        },
        "performance_features": {
            "cache_warming": "Proactive population of frequently accessed data",
            "hit_ratio_tracking": "Monitor cache effectiveness",
            "memory_usage_monitoring": "Track Redis memory consumption",
            "performance_comparison": "Benchmark cached vs non-cached operations",
            "detailed_statistics": "Namespace-level cache analysis"
        }
    }
