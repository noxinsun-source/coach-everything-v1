"""
Data models for tasks and micro-tasks
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import uuid4


class TaskStatus(str, Enum):
    """Status of a task"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    PAUSED = "paused"


class TaskPriority(str, Enum):
    """Priority level of a task"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class VerificationCriteria:
    """Testable verification criteria for a task"""
    description: str  # What success looks like
    is_testable: bool = True  # Can be objectively verified
    examples: List[str] = field(default_factory=list)  # Examples of success
    command: Optional[str] = None  # Command to verify (e.g., "python --version")


@dataclass
class MicroTask:
    """
    A micro-task: a single, small, actionable step (1-2 hours)
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""  # Brief title
    description: str = ""  # Detailed description

    # Timing
    estimated_duration_minutes: int = 120  # 1-2 hours ideal
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Status
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM

    # Verification
    verification_criteria: Optional[VerificationCriteria] = None

    # Relationships
    parent_task_id: Optional[str] = None  # Link to parent task
    roadmap_id: Optional[str] = None  # Link to roadmap

    # Experience sources
    source_experiences: List[str] = field(default_factory=list)  # URLs/refs to source experiences

    # Notes
    notes: str = ""  # User notes
    blockers: List[str] = field(default_factory=list)  # Things blocking progress

    # Coaching
    coach_messages: List[str] = field(default_factory=list)  # Messages from Coach Agent

    def start(self) -> None:
        """Mark task as started"""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()

    def complete(self) -> None:
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()

    def block(self, reason: str) -> None:
        """Mark task as blocked"""
        self.status = TaskStatus.BLOCKED
        self.blockers.append(reason)

    def elapsed_time_minutes(self) -> int:
        """Get elapsed time in minutes"""
        if self.started_at is None:
            return 0
        end_time = self.completed_at or datetime.now()
        delta = end_time - self.started_at
        return int(delta.total_seconds() / 60)

    def verify(self, verification_passed: bool) -> bool:
        """Verify if verification criteria met"""
        if verification_passed:
            self.complete()
            return True
        return False

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'estimated_duration_minutes': self.estimated_duration_minutes,
            'status': self.status.value,
            'priority': self.priority.value,
            'verification_criteria': {
                'description': self.verification_criteria.description,
                'is_testable': self.verification_criteria.is_testable,
                'examples': self.verification_criteria.examples,
                'command': self.verification_criteria.command,
            } if self.verification_criteria else None,
            'source_experiences': self.source_experiences,
            'notes': self.notes,
            'blockers': self.blockers,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'elapsed_time_minutes': self.elapsed_time_minutes(),
        }


@dataclass
class TaskPhase:
    """
    A phase containing multiple micro-tasks
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""  # Phase name
    description: str = ""  # Phase description
    estimated_duration_hours: int = 8  # Total hours for phase

    # Tasks
    micro_tasks: List[MicroTask] = field(default_factory=list)
    current_task_index: int = 0

    # Timeline
    estimated_start_date: Optional[datetime] = None
    estimated_end_date: Optional[datetime] = None

    # Status
    status: TaskStatus = TaskStatus.PENDING

    def add_task(self, task: MicroTask) -> None:
        """Add a micro-task to phase"""
        task.parent_task_id = self.id
        self.micro_tasks.append(task)

    def get_current_task(self) -> Optional[MicroTask]:
        """Get current micro-task"""
        if 0 <= self.current_task_index < len(self.micro_tasks):
            return self.micro_tasks[self.current_task_index]
        return None

    def next_task(self) -> Optional[MicroTask]:
        """Move to next micro-task"""
        if self.current_task_index < len(self.micro_tasks) - 1:
            self.current_task_index += 1
            return self.get_current_task()
        return None

    def completion_percentage(self) -> float:
        """Get phase completion percentage"""
        if not self.micro_tasks:
            return 0.0
        completed = sum(
            1 for t in self.micro_tasks
            if t.status == TaskStatus.COMPLETED
        )
        return (completed / len(self.micro_tasks)) * 100

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'estimated_duration_hours': self.estimated_duration_hours,
            'status': self.status.value,
            'completion_percentage': self.completion_percentage(),
            'total_tasks': len(self.micro_tasks),
            'completed_tasks': sum(
                1 for t in self.micro_tasks
                if t.status == TaskStatus.COMPLETED
            ),
            'current_task': self.micro_tasks[self.current_task_index].to_dict()
            if self.current_task_index < len(self.micro_tasks) else None,
        }
