"""
SQLite cache management for search results and templates
Improves performance by caching experiences and patterns
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheManager:
    """
    SQLite-based cache for:
    - Search results (by query, domain, platform)
    - Task templates (by domain, project type)
    - Learned patterns (best practices)
    - User preferences
    """

    def __init__(self, cache_path: str):
        self.cache_path = Path(cache_path)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = self.cache_path.parent / "coach_cache.db"
        self._init_database()

    def _init_database(self) -> None:
        """Initialize SQLite database with tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Search results cache
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                domain TEXT,
                platform TEXT,
                results JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        """)

        # Task templates cache
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                project_type TEXT,
                template JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usage_count INTEGER DEFAULT 0
            )
        """)

        # Micro-task patterns (learned patterns)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS micro_task_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT NOT NULL,
                pattern JSON NOT NULL,
                success_rate FLOAT DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Verification criteria templates
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verification_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_category TEXT NOT NULL,
                criteria JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indices for faster queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_query ON search_cache(query)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_domain ON search_cache(domain)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_type ON task_templates(domain)")

        conn.commit()
        conn.close()

    def cache_search_results(
        self,
        query: str,
        results: List[Dict[str, Any]],
        domain: Optional[str] = None,
        platform: Optional[str] = None,
        ttl_hours: int = 24,
    ) -> None:
        """Cache search results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        expires_at = (datetime.now() + timedelta(hours=ttl_hours)).isoformat()

        try:
            cursor.execute("""
                INSERT INTO search_cache (query, domain, platform, results, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """, (query, domain, platform, json.dumps(results), expires_at))
            conn.commit()
            logger.info(f"Cached search results for query: {query}")
        except Exception as e:
            logger.error(f"Error caching search results: {str(e)}")
        finally:
            conn.close()

    def get_cached_results(
        self,
        query: str,
        domain: Optional[str] = None,
    ) -> Optional[List[Dict[str, Any]]]:
        """Retrieve cached search results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT results FROM search_cache
                WHERE query = ? AND domain = ?
                AND expires_at > datetime('now')
                ORDER BY created_at DESC
                LIMIT 1
            """, (query, domain))

            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
        except Exception as e:
            logger.error(f"Error retrieving cached results: {str(e)}")
        finally:
            conn.close()

        return None

    def cache_task_template(
        self,
        domain: str,
        template: Dict[str, Any],
        project_type: Optional[str] = None,
    ) -> None:
        """Cache a task template"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO task_templates (domain, project_type, template)
                VALUES (?, ?, ?)
            """, (domain, project_type, json.dumps(template)))
            conn.commit()
            logger.info(f"Cached template for domain: {domain}")
        except Exception as e:
            logger.error(f"Error caching template: {str(e)}")
        finally:
            conn.close()

    def get_task_templates(
        self,
        domain: str,
        project_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get cached task templates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        templates = []

        try:
            if project_type:
                cursor.execute("""
                    SELECT template FROM task_templates
                    WHERE domain = ? AND project_type = ?
                    ORDER BY usage_count DESC
                """, (domain, project_type))
            else:
                cursor.execute("""
                    SELECT template FROM task_templates
                    WHERE domain = ?
                    ORDER BY usage_count DESC
                """, (domain,))

            for row in cursor.fetchall():
                templates.append(json.loads(row[0]))

        except Exception as e:
            logger.error(f"Error retrieving templates: {str(e)}")
        finally:
            conn.close()

        return templates

    def cache_micro_task_pattern(
        self,
        task_type: str,
        pattern: Dict[str, Any],
        success_rate: float = 0.0,
    ) -> None:
        """Cache a learned micro-task pattern"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO micro_task_patterns (task_type, pattern, success_rate)
                VALUES (?, ?, ?)
            """, (task_type, json.dumps(pattern), success_rate))
            conn.commit()
        except Exception as e:
            logger.error(f"Error caching pattern: {str(e)}")
        finally:
            conn.close()

    def get_successful_patterns(
        self,
        task_type: str,
        min_success_rate: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """Get high-success micro-task patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        patterns = []

        try:
            cursor.execute("""
                SELECT pattern FROM micro_task_patterns
                WHERE task_type = ? AND success_rate >= ?
                ORDER BY success_rate DESC
            """, (task_type, min_success_rate))

            for row in cursor.fetchall():
                patterns.append(json.loads(row[0]))

        except Exception as e:
            logger.error(f"Error retrieving patterns: {str(e)}")
        finally:
            conn.close()

        return patterns

    def cache_verification_criteria(
        self,
        task_category: str,
        criteria: Dict[str, Any],
    ) -> None:
        """Cache verification criteria template"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO verification_templates (task_category, criteria)
                VALUES (?, ?)
            """, (task_category, json.dumps(criteria)))
            conn.commit()
        except Exception as e:
            logger.error(f"Error caching verification criteria: {str(e)}")
        finally:
            conn.close()

    def get_verification_criteria(
        self,
        task_category: str,
    ) -> Optional[Dict[str, Any]]:
        """Get verification criteria template"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT criteria FROM verification_templates
                WHERE task_category = ?
                LIMIT 1
            """, (task_category,))

            row = cursor.fetchone()
            if row:
                return json.loads(row[0])

        except Exception as e:
            logger.error(f"Error retrieving verification criteria: {str(e)}")
        finally:
            conn.close()

        return None

    def clear_expired_cache(self) -> int:
        """Clear expired cache entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                DELETE FROM search_cache
                WHERE expires_at < datetime('now')
            """)
            deleted = cursor.rowcount
            conn.commit()
            logger.info(f"Cleared {deleted} expired cache entries")
            return deleted

        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return 0
        finally:
            conn.close()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        stats = {}

        try:
            cursor.execute("SELECT COUNT(*) FROM search_cache")
            stats['search_cache_count'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM task_templates")
            stats['templates_count'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM micro_task_patterns")
            stats['patterns_count'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM verification_templates")
            stats['verification_count'] = cursor.fetchone()[0]

        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
        finally:
            conn.close()

        return stats

    def vacuum_database(self) -> None:
        """Optimize database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("VACUUM")
            conn.commit()
            logger.info("Database vacuumed and optimized")
        except Exception as e:
            logger.error(f"Error vacuuming database: {str(e)}")
        finally:
            conn.close()
