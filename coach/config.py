"""
Configuration management for Coach Everything
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
from pydantic import BaseModel, Field


class SearchConfig(BaseModel):
    """Configuration for search engine"""
    platforms: list[str] = Field(
        default=["reddit", "forums", "blogs", "github"],
        description="Search platforms to include"
    )
    include_papers: bool = Field(
        default=True,
        description="Include arXiv and OpenReview papers"
    )
    recency_weight: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Weight for recent vs old content (0-1)"
    )
    max_results_per_platform: int = Field(
        default=10,
        description="Maximum search results per platform"
    )


class TaskAtomizationConfig(BaseModel):
    """Configuration for task atomization"""
    default_micro_task_duration: int = Field(
        default=120,
        description="Default micro-task duration in minutes (1-2 hours ideal)"
    )
    require_approval: bool = Field(
        default=True,
        description="Require user approval at each stage"
    )
    include_verification_criteria: bool = Field(
        default=True,
        description="Include testable verification criteria for each task"
    )
    refinement_levels: int = Field(
        default=3,
        description="Number of refinement stages (outline -> details -> micro)"
    )


class CoachAgentConfig(BaseModel):
    """Configuration for Coach Agent behavior"""
    personality: str = Field(
        default="encouraging",
        description="Coach personality: encouraging, formal, casual"
    )
    check_in_frequency: int = Field(
        default=60,
        description="Check-in frequency in minutes"
    )
    celebrate_milestones: bool = Field(
        default=True,
        description="Celebrate task completions"
    )
    offer_help_threshold: int = Field(
        default=30,
        description="Offer help after N minutes stuck"
    )


class LLMConfig(BaseModel):
    """LLM Base Model Configuration"""
    provider: str = Field(
        default="anthropic",
        description="LLM provider: anthropic, openai, custom"
    )
    model_name: str = Field(
        default="claude-3-haiku-20240307",
        description="Model name (Claude, GPT-4, etc.)"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for the provider"
    )
    base_url: Optional[str] = Field(
        default=None,
        description="Custom base URL for API (optional)"
    )


class CoachConfig(BaseModel):
    """Main configuration for Coach Everything"""
    # LLM Configuration
    llm: LLMConfig = Field(
        default_factory=LLMConfig,
        description="Large Language Model configuration"
    )

    # Paths
    obsidian_vault_path: str = Field(
        default=str(Path.home() / "Documents" / "Obsidian Vault"),
        description="Path to Obsidian vault"
    )
    cache_dir: str = Field(
        default=str(Path.home() / ".coach"),
        description="Cache directory for Coach Everything"
    )

    # Subsystem configs
    search: SearchConfig = Field(
        default_factory=SearchConfig,
        description="Search engine configuration"
    )
    task_atomization: TaskAtomizationConfig = Field(
        default_factory=TaskAtomizationConfig,
        description="Task atomization configuration"
    )
    coach_agent: CoachAgentConfig = Field(
        default_factory=CoachAgentConfig,
        description="Coach Agent configuration"
    )

    # API Keys
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key (from env or config)"
    )

    class Config:
        extra = "allow"  # Allow extra fields for extensibility


class ConfigManager:
    """Manages Coach Everything configuration"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or str(
            Path.home() / ".coach" / "config.yaml"
        )
        self.config = self._load_config()

    def _load_config(self) -> CoachConfig:
        """Load configuration from file or use defaults"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                config_dict = yaml.safe_load(f)
                return CoachConfig(**config_dict)
        else:
            return CoachConfig()

    def save_config(self) -> None:
        """Save configuration to file"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(
                json.loads(self.config.model_dump_json()),
                f,
                default_flow_style=False
            )

    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values"""
        config_dict = json.loads(self.config.model_dump_json())

        # Update nested configs
        for key, value in updates.items():
            if key in config_dict and isinstance(config_dict[key], dict):
                config_dict[key].update(value)
            else:
                config_dict[key] = value

        self.config = CoachConfig(**config_dict)
        self.save_config()

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation (e.g., 'search.platforms')"""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            elif isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def __repr__(self) -> str:
        return f"ConfigManager(path={self.config_path})"


# Global config instance
_global_config: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get global config instance"""
    global _global_config
    if _global_config is None:
        _global_config = ConfigManager()
    return _global_config


def init_config(config_path: Optional[str] = None) -> ConfigManager:
    """Initialize global config instance"""
    global _global_config
    _global_config = ConfigManager(config_path)
    return _global_config
