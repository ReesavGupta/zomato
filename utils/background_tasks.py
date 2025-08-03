"""
Background tasks for cache management and maintenance
"""

import asyncio
import time
import logging
from typing import Dict, Any
from utils.cache_manager import CacheWarmer, CacheHealthMonitor, AdvancedCachePatterns
from config import CacheNamespace, cache_config

# Setup logging
background_logger = logging.getLogger("background_tasks")
background_logger.setLevel(logging.INFO)

class BackgroundCacheManager:
    """Manages background cache operations and maintenance"""

    def __init__(self):
        self.is_running = False
        self.tasks = {}

    async def start_background_tasks(self):
        """Start all background cache maintenance tasks"""
        if self.is_running:
            return

        self.is_running = True
        background_logger.info("Starting background cache maintenance tasks")

        # Start cache refresh task
        self.tasks["cache_refresh"] = asyncio.create_task(self._cache_refresh_loop())

        # Start health monitoring task
        self.tasks["health_monitor"] = asyncio.create_task(self._health_monitor_loop())

        # Start cache cleanup task
        self.tasks["cache_cleanup"] = asyncio.create_task(self._cache_cleanup_loop())

    async def stop_background_tasks(self):
        """Stop all background tasks"""
        self.is_running = False

        for task_name, task in self.tasks.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    background_logger.info(f"Cancelled background task: {task_name}")

        self.tasks.clear()
        background_logger.info("Stopped all background cache tasks")

    async def _cache_refresh_loop(self):
        """Background loop for cache refresh operations"""
        while self.is_running:
            try:
                # Refresh analytics cache every 30 minutes
                await asyncio.sleep(1800)  # 30 minutes

                if not self.is_running:
                    break

                background_logger.info("Starting scheduled cache refresh")

                # Refresh popular items cache
                await self._refresh_popular_items()

                # Refresh restaurant analytics
                await self._refresh_restaurant_analytics()

                background_logger.info("Completed scheduled cache refresh")

            except asyncio.CancelledError:
                break
            except Exception as e:
                background_logger.error(f"Cache refresh loop error: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry

    async def _health_monitor_loop(self):
        """Background loop for cache health monitoring"""
        while self.is_running:
            try:
                # Check health every 5 minutes
                await asyncio.sleep(300)  # 5 minutes

                if not self.is_running:
                    break

                health_data = await CacheHealthMonitor.check_cache_health()

                # Log health status
                status = health_data.get("status", "unknown")
                if status == "critical":
                    background_logger.error(f"CRITICAL cache health issues: {health_data.get('health_issues', [])}")
                elif status == "warning":
                    background_logger.warning(f"Cache health warnings: {health_data.get('health_issues', [])}")
                else:
                    background_logger.info("Cache health check passed")

                # Store health metrics for monitoring
                await self._store_health_metrics(health_data)

            except asyncio.CancelledError:
                break
            except Exception as e:
                background_logger.error(f"Health monitor loop error: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retry

    async def _cache_cleanup_loop(self):
        """Background loop for cache cleanup operations"""
        while self.is_running:
            try:
                # Cleanup every 2 hours
                await asyncio.sleep(7200)  # 2 hours

                if not self.is_running:
                    break

                background_logger.info("Starting cache cleanup")

                # Remove expired keys
                await self._cleanup_expired_keys()

                # Optimize memory usage
                await self._optimize_cache_memory()

                background_logger.info("Completed cache cleanup")

            except asyncio.CancelledError:
                break
            except Exception as e:
                background_logger.error(f"Cache cleanup loop error: {str(e)}")
                await asyncio.sleep(600)  # Wait 10 minutes before retry

    async def _refresh_popular_items(self):
        """Refresh popular items cache"""
        try:
            background_logger.info("Refreshing popular items cache")
            await asyncio.sleep(1)  # Simulate refresh

        except Exception as e:
            background_logger.error(f"Failed to refresh popular items cache: {str(e)}")

    async def _refresh_restaurant_analytics(self):
        """Refresh restaurant analytics cache"""
        try:
            background_logger.info("Refreshing restaurant analytics cache")
            await asyncio.sleep(1)  # Simulate refresh

        except Exception as e:
            background_logger.error(f"Failed to refresh restaurant analytics cache: {str(e)}")

    async def _store_health_metrics(self, health_data: Dict[str, Any]):
        """Store health metrics for monitoring"""
        try:
            if "performance_metrics" in health_data:
                hit_ratio = health_data["performance_metrics"].get("hit_ratio", {})
                if "hit_ratio_percent" in hit_ratio:
                    background_logger.info(f"Cache hit ratio: {hit_ratio['hit_ratio_percent']}%")

        except Exception as e:
            background_logger.error(f"Failed to store health metrics: {str(e)}")

    async def _cleanup_expired_keys(self):
        """Clean up expired cache keys"""
        try:
            from fastapi_cache import FastAPICache

            if not hasattr(FastAPICache, '_backend') or FastAPICache._backend is None:
                return

            backend = FastAPICache.get_backend()
            redis_client = backend.redis

            # Get all keys with our prefix
            keys = await redis_client.keys(f"{cache_config.cache_prefix}:*")
            expired_count = 0

            for key in keys:
                ttl = await redis_client.ttl(key)
                if ttl == -1:  # Key exists but has no expiration
                    await redis_client.delete(key)
                    expired_count += 1

            if expired_count > 0:
                background_logger.info(f"Cleaned up {expired_count} expired keys")

        except Exception as e:
            background_logger.error(f"Failed to cleanup expired keys: {str(e)}")

    async def _optimize_cache_memory(self):
        """Optimize cache memory usage"""
        try:
            from utils.cache_manager import CacheMetrics

            memory_data = await CacheMetrics.get_memory_usage_analysis()

            if "error" not in memory_data:
                memory_usage = memory_data.get("memory_utilization_percent", 0)

                if memory_usage > 85:
                    background_logger.warning(f"High memory usage detected: {memory_usage}%")

        except Exception as e:
            background_logger.error(f"Failed to optimize cache memory: {str(e)}")


# Global background cache manager instance
background_cache_manager = BackgroundCacheManager()