import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.models.gemini_cache import GeminiCache
import logging

logger = logging.getLogger(__name__)

class GeminiCacheService:
    """
    Service for caching Gemini AI API responses to reduce costs and improve performance.

    This service implements a TTL-based cache for AI responses, with a default
    expiration time of 7 days. It's expected to reduce API costs by ~70%.
    """

    def __init__(self, db: Session):
        self.db = db
        self.cache_ttl = timedelta(days=7)  # Cache for 7 days
        self.enabled = True  # Flag to easily disable caching if needed

    def _generate_cache_key(self, deviation_id: str, context: Dict, suggestion_type: str) -> str:
        """Generate unique cache key from deviation + context + type"""
        cache_data = {
            'deviation_id': str(deviation_id),
            'context': context or {},
            'type': suggestion_type
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()

    def get_cached_response(self, deviation_id: str, context: Dict, suggestion_type: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached response if exists and not expired"""
        if not self.enabled:
            return None

        try:
            cache_key = self._generate_cache_key(deviation_id, context, suggestion_type)

            cached = self.db.query(GeminiCache).filter(
                GeminiCache.cache_key == cache_key,
                GeminiCache.expires_at > datetime.utcnow()
            ).first()

            if cached:
                # Update cache stats
                cached.update_access_stats()
                self.db.commit()

                logger.info(f"✅ Cache hit for {suggestion_type} (deviation: {deviation_id})")
                return json.loads(cached.response_data)

            logger.info(f"❌ Cache miss for {suggestion_type} (deviation: {deviation_id})")
            return None
        except Exception as e:
            logger.error(f"Error retrieving from cache: {e}")
            return None

    def cache_response(self, deviation_id: str, context: Dict, suggestion_type: str, response: List[Dict[str, Any]]) -> bool:
        """Cache API response"""
        if not self.enabled:
            return False

        try:
            cache_key = self._generate_cache_key(deviation_id, context, suggestion_type)
            expires_at = datetime.utcnow() + self.cache_ttl

            # Check for existing cache entry and update if exists
            existing = self.db.query(GeminiCache).filter(
                GeminiCache.cache_key == cache_key
            ).first()

            if existing:
                existing.response_data = json.dumps(response)
                existing.expires_at = expires_at
                existing.access_count += 1
                existing.last_accessed = datetime.utcnow()
                self.db.commit()
                logger.info(f"Updated existing cache entry for {suggestion_type} (deviation: {deviation_id})")
                return True

            # Create new cache entry
            context_dict = context or {}
            cached = GeminiCache(
                cache_key=cache_key,
                deviation_id=deviation_id,
                suggestion_type=suggestion_type,
                context_hash=self._hash_context(context_dict),
                response_data=json.dumps(response),
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                access_count=1,
                last_accessed=datetime.utcnow()
            )

            self.db.add(cached)
            self.db.commit()
            logger.info(f"Created new cache entry for {suggestion_type} (deviation: {deviation_id})")
            return True
        except Exception as e:
            logger.error(f"Error caching response: {e}")
            return False

    def _hash_context(self, context: Dict) -> str:
        """Generate hash of context for quick lookup"""
        context_str = json.dumps(context or {}, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()

    def cleanup_expired(self) -> int:
        """Remove expired cache entries"""
        try:
            expired = self.db.query(GeminiCache).filter(
                GeminiCache.expires_at < datetime.utcnow()
            ).delete()
            self.db.commit()
            logger.info(f"Cleaned up {expired} expired cache entries")
            return expired
        except Exception as e:
            logger.error(f"Error cleaning up expired entries: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            total_entries = self.db.query(GeminiCache).count()
            total_access_count = self.db.query(
                GeminiCache
            ).with_entities(
                GeminiCache.access_count
            ).all()

            total_hits = sum(count[0] for count in total_access_count)
            avg_hits = total_hits / total_entries if total_entries > 0 else 0

            # Get entries by suggestion type
            entries_by_type = self.db.query(
                GeminiCache.suggestion_type,
                func.count(GeminiCache.id)
            ).group_by(
                GeminiCache.suggestion_type
            ).all()

            type_distribution = {type_: count for type_, count in entries_by_type}

            # Get count by age
            day_ago = datetime.utcnow() - timedelta(days=1)
            week_ago = datetime.utcnow() - timedelta(weeks=1)

            last_day_entries = self.db.query(GeminiCache).filter(
                GeminiCache.created_at > day_ago
            ).count()

            last_week_entries = self.db.query(GeminiCache).filter(
                GeminiCache.created_at > week_ago
            ).count()

            return {
                "total_entries": total_entries,
                "total_hits": total_hits,
                "avg_hits_per_entry": round(avg_hits, 2),
                "type_distribution": type_distribution,
                "last_24h_entries": last_day_entries,
                "last_7d_entries": last_week_entries,
                "ttl_days": self.cache_ttl.days,
                "enabled": self.enabled,
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {
                "error": str(e)
            }