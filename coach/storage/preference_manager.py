"""
User preference and state persistence
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PreferenceManager:
    """
    Manages user preferences and state persistence
    Stored in ~/.coach/preferences.json
    """

    def __init__(self, preferences_path: str):
        self.preferences_path = Path(preferences_path)
        self.preferences_path.parent.mkdir(parents=True, exist_ok=True)
        self.preferences = self._load_preferences()

    def _load_preferences(self) -> Dict[str, Any]:
        """Load preferences from file"""
        if self.preferences_path.exists():
            try:
                with open(self.preferences_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading preferences: {str(e)}")

        return self._get_default_preferences()

    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default preferences"""
        return {
            "obsidian_vault_path": str(Path.home() / "Documents" / "Obsidian Vault"),
            "theme": "light",
            "language": "en",
            "search_platforms": ["reddit", "github", "forums", "blogs"],
            "include_papers": True,
            "recency_weight": 0.7,
            "micro_task_duration_minutes": 120,
            "require_approval": True,
            "coach_personality": "encouraging",
            "check_in_frequency_minutes": 60,
            "notification_enabled": True,
            "recent_projects": [],
            "favorite_domains": [],
            "disabled_sources": [],
            "last_used_template": None,
            "api_keys": {},
            "statistics": {
                "total_projects": 0,
                "total_tasks_completed": 0,
                "total_time_spent_hours": 0,
            },
        }

    def save_preferences(self) -> None:
        """Save preferences to file"""
        try:
            with open(self.preferences_path, 'w') as f:
                json.dump(self.preferences, f, indent=2)
            logger.info("Preferences saved")
        except Exception as e:
            logger.error(f"Error saving preferences: {str(e)}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get preference value by dot notation"""
        keys = key.split('.')
        value = self.preferences

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set preference value by dot notation"""
        keys = key.split('.')
        current = self.preferences

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value
        self.save_preferences()

    def add_recent_project(self, project_name: str, project_path: str) -> None:
        """Add project to recent list"""
        recent = self.get("recent_projects", [])

        # Remove if already exists
        recent = [p for p in recent if p["name"] != project_name]

        # Add to front
        recent.insert(0, {
            "name": project_name,
            "path": project_path,
            "opened_at": datetime.now().isoformat(),
        })

        # Keep last 10
        recent = recent[:10]

        self.set("recent_projects", recent)

    def get_recent_projects(self, limit: int = 5) -> list:
        """Get recent projects"""
        recent = self.get("recent_projects", [])
        return recent[:limit]

    def add_favorite_domain(self, domain: str) -> None:
        """Add domain to favorites"""
        favorites = self.get("favorite_domains", [])
        if domain not in favorites:
            favorites.append(domain)
            self.set("favorite_domains", favorites)

    def get_favorite_domains(self) -> list:
        """Get favorite domains"""
        return self.get("favorite_domains", [])

    def update_statistics(
        self,
        projects_completed: int = 0,
        tasks_completed: int = 0,
        time_spent_hours: float = 0.0,
    ) -> None:
        """Update cumulative statistics"""
        stats = self.get("statistics", {})
        stats["total_projects"] += projects_completed
        stats["total_tasks_completed"] += tasks_completed
        stats["total_time_spent_hours"] += time_spent_hours
        self.set("statistics", stats)

    def set_api_key(self, service: str, api_key: str) -> None:
        """Store API key (use with caution)"""
        api_keys = self.get("api_keys", {})
        api_keys[service] = api_key
        self.set("api_keys", api_keys)

    def get_api_key(self, service: str) -> Optional[str]:
        """Retrieve API key"""
        api_keys = self.get("api_keys", {})
        return api_keys.get(service)

    def to_dict(self) -> Dict[str, Any]:
        """Export preferences as dictionary"""
        return self.preferences.copy()

    def __repr__(self) -> str:
        return f"PreferenceManager(path={self.preferences_path})"
