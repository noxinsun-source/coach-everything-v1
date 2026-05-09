"""
Data model for task roadmaps
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import uuid4

from coach.models.task import TaskPhase, MicroTask, TaskStatus


class ApprovalStatus(str, Enum):
    """Status of roadmap approval"""
    NOT_SUBMITTED = "not_submitted"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_REVISION = "in_revision"


@dataclass
class RoadmapOutline:
    """
    Initial outline of a roadmap (Stage 1: Rough structure)
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""  # Project/task title
    description: str = ""  # Detailed description
    goal: str = ""  # What success looks like

    # Rough phases
    phases: List[str] = field(default_factory=list)  # ["Phase 1", "Phase 2", ...]
    estimated_total_hours: int = 20  # Rough estimate
    estimated_weeks: int = 4

    # Search sources used to create this
    source_experiences_used: List[str] = field(default_factory=list)

    # Approval
    approval_status: ApprovalStatus = ApprovalStatus.NOT_SUBMITTED
    approval_date: Optional[datetime] = None

    # Feedback
    user_feedback: str = ""  # User edits/notes on outline


@dataclass
class DetailedRoadmap:
    """
    Detailed roadmap with specific steps (Stage 2: Detailed structure)
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    outline_id: str = ""  # Reference to parent outline

    phases: List[TaskPhase] = field(default_factory=list)
    current_phase_index: int = 0

    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    approval_date: Optional[datetime] = None

    # Approval
    approval_status: ApprovalStatus = ApprovalStatus.NOT_SUBMITTED

    # Feedback
    user_feedback: str = ""

    def add_phase(self, phase: TaskPhase) -> None:
        """Add a phase to roadmap"""
        self.phases.append(phase)

    def get_current_phase(self) -> Optional[TaskPhase]:
        """Get current phase"""
        if 0 <= self.current_phase_index < len(self.phases):
            return self.phases[self.current_phase_index]
        return None

    def next_phase(self) -> Optional[TaskPhase]:
        """Move to next phase"""
        if self.current_phase_index < len(self.phases) - 1:
            self.current_phase_index += 1
            return self.get_current_phase()
        return None

    def completion_percentage(self) -> float:
        """Get overall completion percentage"""
        if not self.phases:
            return 0.0
        total_completion = sum(p.completion_percentage() for p in self.phases)
        return total_completion / len(self.phases)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'outline_id': self.outline_id,
            'approval_status': self.approval_status.value,
            'completion_percentage': self.completion_percentage(),
            'total_phases': len(self.phases),
            'current_phase': self.phases[self.current_phase_index].to_dict()
            if self.current_phase_index < len(self.phases) else None,
        }


@dataclass
class TaskRoadmap:
    """
    Complete task roadmap from outline through micro-tasks
    """
    id: str = field(default_factory=lambda: str(uuid4()))

    # Project metadata
    project_name: str = ""
    project_description: str = ""
    domain: str = ""  # e.g., "machine_learning", "job_hunting", "learning"
    learning_style: str = "mixed"  # "visual", "hands_on", "reading", "mixed"

    # Three stages
    outline: Optional[RoadmapOutline] = None
    detailed_roadmap: Optional[DetailedRoadmap] = None

    # Timeline
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Metadata
    tags: List[str] = field(default_factory=list)
    notes: str = ""

    # Coach logs
    coach_logs: List[str] = field(default_factory=list)

    def get_current_micro_task(self) -> Optional[MicroTask]:
        """Get currently active micro-task"""
        if not self.detailed_roadmap:
            return None

        current_phase = self.detailed_roadmap.get_current_phase()
        if not current_phase:
            return None

        return current_phase.get_current_task()

    def get_all_micro_tasks(self) -> List[MicroTask]:
        """Get all micro-tasks in roadmap"""
        if not self.detailed_roadmap:
            return []

        all_tasks = []
        for phase in self.detailed_roadmap.phases:
            all_tasks.extend(phase.micro_tasks)
        return all_tasks

    def completion_percentage(self) -> float:
        """Get overall completion percentage"""
        if not self.detailed_roadmap:
            return 0.0
        return self.detailed_roadmap.completion_percentage()

    def total_time_estimate_hours(self) -> int:
        """Get total time estimate in hours"""
        if not self.detailed_roadmap:
            if self.outline:
                return self.outline.estimated_total_hours
            return 0
        return sum(phase.estimated_duration_hours
                   for phase in self.detailed_roadmap.phases)

    def total_completed_time_minutes(self) -> int:
        """Get total completed time in minutes"""
        if not self.detailed_roadmap:
            return 0

        total_minutes = 0
        for phase in self.detailed_roadmap.phases:
            for task in phase.micro_tasks:
                if task.status == TaskStatus.COMPLETED:
                    total_minutes += task.elapsed_time_minutes()
        return total_minutes

    def start(self) -> None:
        """Mark roadmap as started"""
        self.started_at = datetime.now()

    def complete(self) -> None:
        """Mark roadmap as completed"""
        self.completed_at = datetime.now()

    def add_coach_log(self, message: str) -> None:
        """Add message to coach log"""
        timestamp = datetime.now().isoformat()
        self.coach_logs.append(f"[{timestamp}] {message}")

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'project_name': self.project_name,
            'project_description': self.project_description,
            'domain': self.domain,
            'completion_percentage': self.completion_percentage(),
            'total_time_estimate_hours': self.total_time_estimate_hours(),
            'total_completed_time_minutes': self.total_completed_time_minutes(),
            'total_micro_tasks': len(self.get_all_micro_tasks()),
            'completed_micro_tasks': sum(
                1 for t in self.get_all_micro_tasks()
                if t.status == TaskStatus.COMPLETED
            ),
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }
