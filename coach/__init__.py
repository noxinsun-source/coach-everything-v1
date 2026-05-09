"""
Coach Everything - Universal Task Breakdown & AI Coaching Agent

A system designed to help anyone (especially those with ADHD or executive dysfunction)
transform vague, overwhelming tasks into crystal-clear, bite-sized micro-steps.

Key Components:
- Multi-dimensional search engine for real human experiences
- Progressive task atomization with user approval
- Obsidian workspace generation
- Real-time Coach Agent for guidance and encouragement
- SQLite caching for performance
"""

__version__ = "1.0.0"
__author__ = "Coach Everything Contributors"
__all__ = [
    "CoachAgent",
    "TaskRoadmap",
    "MicroTask",
    "SearchEngine",
    "TaskAtomizer",
    "WorkspaceGenerator",
    "CacheManager",
]

from coach.agent import CoachAgent
from coach.models.roadmap import TaskRoadmap
from coach.models.task import MicroTask
from coach.engines.search_engine import SearchEngine
from coach.engines.task_atomizer import TaskAtomizer
from coach.engines.workspace_generator import WorkspaceGenerator
from coach.storage.cache_manager import CacheManager
