"""
Task Atomizer: Progressive task breakdown and refinement
Converts vague goals into crystal-clear 1-2 hour micro-tasks
"""

from typing import List, Optional, Tuple
from coach.models.roadmap import TaskRoadmap, RoadmapOutline, DetailedRoadmap
from coach.models.task import TaskPhase, MicroTask, VerificationCriteria, TaskStatus


class TaskAtomizer:
    """
    Progressively breaks down tasks into micro-steps
    Three stages:
    1. Outline: Rough phases
    2. Detailed: Specific steps within each phase
    3. Micro: 1-2 hour actionable tasks with verification
    """

    def __init__(self):
        self.default_micro_task_duration = 120  # minutes

    def create_outline(
        self,
        task: str,
        domain: str,
        estimated_total_hours: int = 20,
        estimated_weeks: int = 4,
        sources: Optional[List[str]] = None,
    ) -> RoadmapOutline:
        """
        Stage 1: Create rough outline of phases
        Input: Vague task description
        Output: 3-5 phase outline
        """
        outline = RoadmapOutline(
            title=task,
            description=task,
            goal=f"Successfully complete: {task}",
            estimated_total_hours=estimated_total_hours,
            estimated_weeks=estimated_weeks,
        )

        # Generate phases based on domain
        phases = self._generate_phases_for_domain(domain, task)
        outline.phases = phases

        if sources:
            outline.source_experiences_used = sources

        return outline

    def expand_to_detailed_roadmap(
        self,
        outline: RoadmapOutline,
        domain: str,
    ) -> DetailedRoadmap:
        """
        Stage 2: Expand outline into detailed steps
        Input: Approved outline
        Output: Detailed phases with specific steps
        """
        detailed = DetailedRoadmap(
            outline_id=outline.id,
        )

        for phase_name in outline.phases:
            phase = self._create_detailed_phase(
                phase_name=phase_name,
                domain=domain,
            )
            detailed.add_phase(phase)

        return detailed

    def atomize_to_micro_tasks(
        self,
        detailed_roadmap: DetailedRoadmap,
        max_duration_minutes: int = 120,
    ) -> DetailedRoadmap:
        """
        Stage 3: Break down detailed steps into micro-tasks (1-2 hours)
        Input: Detailed roadmap with phases/steps
        Output: Same roadmap with micro-tasks in each phase
        """
        for phase in detailed_roadmap.phases:
            # Each phase should have micro-tasks
            if not phase.micro_tasks:
                # If no tasks yet, create them from phase description
                phase.micro_tasks = self._create_micro_tasks_for_phase(
                    phase=phase,
                    max_duration_minutes=max_duration_minutes,
                )

        return detailed_roadmap

    def refine_micro_task(
        self,
        task: MicroTask,
        feedback: str,
    ) -> MicroTask:
        """
        Refine a micro-task based on user feedback
        Can split, merge, or modify based on feedback
        """
        # This is where we'd implement refinement logic
        # For now, just update the task
        if "split" in feedback.lower():
            # User wants this split into smaller tasks
            task.estimated_duration_minutes = max(30, task.estimated_duration_minutes // 2)
        elif "merge" in feedback.lower():
            # Combine with next task
            pass
        elif "change" in feedback.lower():
            # User has specific changes
            pass

        return task

    # Private methods

    @staticmethod
    def _generate_phases_for_domain(domain: str, task: str) -> List[str]:
        """Generate appropriate phases based on domain"""
        domain_phases = {
            "learning": [
                "Setup & Environment",
                "Core Concepts & Fundamentals",
                "Hands-on Practice",
                "Projects & Application",
                "Advanced Topics",
            ],
            "research": [
                "Literature Review & Planning",
                "Setup & Data Preparation",
                "Experimentation",
                "Analysis & Validation",
                "Writing & Documentation",
            ],
            "job_hunting": [
                "Resume & Profile Optimization",
                "Target Companies & Positions",
                "Application & Networking",
                "Interview Preparation",
                "Negotiation & Offer",
            ],
            "startup": [
                "Idea Validation & Planning",
                "MVP Development",
                "User Testing & Feedback",
                "Iteration & Refinement",
                "Launch & Marketing",
            ],
            "default": [
                "Planning & Preparation",
                "Learning & Research",
                "Implementation",
                "Testing & Validation",
                "Completion & Review",
            ],
        }

        phases = domain_phases.get(domain, domain_phases["default"])
        return phases

    @staticmethod
    def _create_detailed_phase(
        phase_name: str,
        domain: str,
    ) -> TaskPhase:
        """Create a detailed phase with specific steps"""
        phase = TaskPhase(name=phase_name)

        # Example steps for learning domain
        if domain == "learning":
            if "Setup" in phase_name:
                phase.description = "Install tools and set up your environment"
            elif "Core" in phase_name:
                phase.description = "Learn fundamental concepts and theory"
            elif "Practice" in phase_name:
                phase.description = "Hands-on exercises and coding practice"
            elif "Projects" in phase_name:
                phase.description = "Build small projects to apply knowledge"
            elif "Advanced" in phase_name:
                phase.description = "Explore advanced topics and patterns"

        return phase

    @staticmethod
    def _create_micro_tasks_for_phase(
        phase: TaskPhase,
        max_duration_minutes: int = 120,
    ) -> List[MicroTask]:
        """Create micro-tasks for a phase"""
        tasks = []

        # Example micro-task structure
        task = MicroTask(
            title=f"Start: {phase.name}",
            description=phase.description,
            estimated_duration_minutes=max_duration_minutes,
        )

        # Add verification criteria
        task.verification_criteria = VerificationCriteria(
            description=f"Completed: {phase.name}",
            is_testable=True,
            examples=[
                "All steps in this phase completed",
                "Work saved and documented",
            ],
        )

        tasks.append(task)
        return tasks

    @staticmethod
    def estimate_time_for_task(
        task_title: str,
        task_description: str,
        complexity: str = "medium",
    ) -> int:
        """Estimate time for a micro-task in minutes"""
        base_times = {
            "simple": 30,
            "medium": 90,
            "complex": 150,
        }

        return base_times.get(complexity, 90)

    @staticmethod
    def generate_verification_criteria(
        task_title: str,
        task_type: str = "general",
    ) -> VerificationCriteria:
        """Generate testable verification criteria"""
        criteria_templates = {
            "learning": {
                "description": "Can explain and demonstrate the concept",
                "examples": [
                    "Complete practice exercises",
                    "Pass quiz or test",
                    "Explain concept to someone else",
                ],
                "command": None,
            },
            "coding": {
                "description": "Code runs without errors and meets requirements",
                "examples": [
                    "All tests pass",
                    "Code lints without warnings",
                    "Output matches expected behavior",
                ],
                "command": "python -m pytest",
            },
            "research": {
                "description": "Analysis complete and documented",
                "examples": [
                    "Results saved with metadata",
                    "Notes document findings",
                    "Ready for next phase",
                ],
                "command": None,
            },
            "writing": {
                "description": "Written content complete and reviewed",
                "examples": [
                    "First draft complete",
                    "Reviewed for clarity",
                    "Ready for editing",
                ],
                "command": None,
            },
        }

        template = criteria_templates.get(task_type, criteria_templates["coding"])
        return VerificationCriteria(
            description=template["description"],
            examples=template["examples"],
            command=template.get("command"),
        )


# Helper functions for template generation

def generate_learning_roadmap_template(
    topic: str,
    experience_level: str = "beginner",
    time_available_hours: int = 20,
) -> RoadmapOutline:
    """Generate a learning roadmap template"""
    atomizer = TaskAtomizer()

    outline = RoadmapOutline(
        title=f"Learn {topic}",
        description=f"Complete guide to learning {topic} from scratch",
        goal=f"Master {topic} and be able to build real projects",
        estimated_total_hours=time_available_hours,
        estimated_weeks=max(2, time_available_hours // 10),
    )

    outline.phases = [
        "Setup & Environment",
        "Core Concepts",
        "Hands-on Practice",
        "First Project",
        "Advanced Topics",
    ]

    return outline


def generate_project_roadmap_template(
    project_name: str,
    project_type: str = "web",
    team_size: int = 1,
) -> RoadmapOutline:
    """Generate a project roadmap template"""
    outline = RoadmapOutline(
        title=f"Build {project_name}",
        description=f"Step-by-step guide to building {project_name}",
        goal=f"Launch {project_name} and get first users",
        estimated_total_hours=100,
        estimated_weeks=6,
    )

    outline.phases = [
        "Planning & Design",
        "Setup & Architecture",
        "Core Features",
        "Testing & Refinement",
        "Deployment & Launch",
    ]

    return outline
