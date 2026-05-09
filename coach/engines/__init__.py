"""
Processing engines for Coach Everything
"""

from coach.engines.search_engine import SearchEngine, SearchResult
from coach.engines.task_atomizer import TaskAtomizer
from coach.engines.workspace_generator import WorkspaceGenerator
from coach.engines.paper_searcher import PaperSearcher, AcademicPaper

__all__ = [
    "SearchEngine",
    "SearchResult",
    "TaskAtomizer",
    "WorkspaceGenerator",
    "PaperSearcher",
    "AcademicPaper",
]
