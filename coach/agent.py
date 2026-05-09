"""
Coach Agent: Core AI coaching system
Orchestrates search, task breakdown, workspace generation, and real-time coaching
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path

from coach.config import ConfigManager, get_config
from coach.models.roadmap import TaskRoadmap, RoadmapOutline, ApprovalStatus
from coach.models.task import MicroTask, TaskPhase, VerificationCriteria, TaskStatus
from coach.models.workspace import ProjectWorkspace
from coach.engines.search_engine import SearchEngine, SearchResult
from coach.engines.task_atomizer import TaskAtomizer
from coach.engines.workspace_generator import WorkspaceGenerator
from coach.engines.paper_searcher import PaperSearcher
from coach.feedback.roadmap_feedback import RoadmapFeedbackHandler
from coach.feedback.task_feedback import TaskFeedbackHandler
from coach.storage.cache_manager import CacheManager
from coach.storage.preference_manager import PreferenceManager

logger = logging.getLogger(__name__)


class CoachAgent:
    """
    Main Coach Agent - orchestrates the entire task breakdown and coaching process
    """

    def __init__(
        self,
        vault_path: Optional[str] = None,
        config: Optional[ConfigManager] = None,
    ):
        """Initialize Coach Agent"""
        self.config = config or get_config()
        self.vault_path = Path(vault_path or self.config.get("obsidian_vault_path"))

        # Initialize components
        self.search_engine = SearchEngine()
        self.task_atomizer = TaskAtomizer()
        self.workspace_generator = WorkspaceGenerator(str(self.vault_path))
        self.paper_searcher = PaperSearcher()

        # Feedback handlers
        self.roadmap_feedback = RoadmapFeedbackHandler()
        self.task_feedback = TaskFeedbackHandler()

        # Storage
        cache_path = self.config.get("cache_dir", str(Path.home() / ".coach"))
        self.cache_manager = CacheManager(cache_path)

        prefs_path = Path(cache_path) / "preferences.json"
        self.preference_manager = PreferenceManager(str(prefs_path))

        # Current roadmap
        self.current_roadmap: Optional[TaskRoadmap] = None

    def start_new_project(
        self,
        task: str,
        domain: str,
        estimated_hours: int = 20,
        learning_style: str = "mixed",
    ) -> RoadmapOutline:
        """
        Stage 1: Start a new project
        Search for experiences and create rough outline
        """
        logger.info(f"Starting new project: {task}")

        # Check cache
        cached_results = self.cache_manager.get_cached_results(task, domain)

        # Search for experiences
        search_results = self.search_engine.search(
            query=task,
            platforms=self.config.get("search.platforms"),
            include_papers=self.config.get("search.include_papers"),
            recency_weight=self.config.get("search.recency_weight"),
            max_results=20,
        )

        # Cache results
        self.cache_manager.cache_search_results(
            query=task,
            results=[
                {
                    "title": r.title,
                    "url": r.url,
                    "source": r.source,
                    "summary": r.summary,
                    "upvotes": r.upvotes,
                }
                for r in search_results
            ],
            domain=domain,
            ttl_hours=24,
        )

        # Create roadmap and outline
        self.current_roadmap = TaskRoadmap(
            project_name=task,
            project_description=task,
            domain=domain,
            learning_style=learning_style,
        )

        # Create outline based on experiences
        outline = self.task_atomizer.create_outline(
            task=task,
            domain=domain,
            estimated_total_hours=estimated_hours,
            sources=[r.url for r in search_results[:5]],
        )

        self.current_roadmap.outline = outline

        logger.info(f"Created outline with {len(outline.phases)} phases")

        return outline

    def wait_for_outline_approval(
        self,
        outline: RoadmapOutline,
        user_feedback: Optional[Dict[str, Any]] = None,
    ) -> RoadmapOutline:
        """
        Wait for user approval of outline
        Allow modifications and resubmission
        """
        outline.approval_status = ApprovalStatus.PENDING_APPROVAL

        if user_feedback:
            # Process feedback
            if user_feedback.get("action") == "approve":
                outline = self.roadmap_feedback.approve(outline)
                logger.info("Outline approved by user")

            elif user_feedback.get("action") == "edit":
                outline = self.roadmap_feedback.process_feedback(
                    outline,
                    user_feedback.get("type"),
                    user_feedback.get("data"),
                )
                logger.info("Outline edited by user")

            elif user_feedback.get("action") == "reject":
                outline = self.roadmap_feedback.reject(outline, user_feedback)
                logger.info("Outline rejected by user")

        if self.current_roadmap:
            self.current_roadmap.outline = outline

        return outline

    def expand_to_detailed_roadmap(
        self,
        outline: RoadmapOutline,
    ) -> 'TaskRoadmap':
        """
        Stage 2: Expand outline into detailed steps
        Create specific tasks for each phase
        """
        logger.info("Expanding outline to detailed roadmap")

        if not self.current_roadmap:
            self.current_roadmap = TaskRoadmap(
                project_name=outline.title,
                project_description=outline.description,
            )

        # Create detailed roadmap
        detailed_roadmap = self.task_atomizer.expand_to_detailed_roadmap(
            outline=outline,
            domain=self.current_roadmap.domain,
        )

        self.current_roadmap.detailed_roadmap = detailed_roadmap

        return self.current_roadmap

    def atomize_to_micro_tasks(
        self,
        detailed_roadmap: 'DetailedRoadmap',
    ) -> List[MicroTask]:
        """
        Stage 3: Break down into 1-2 hour micro-tasks
        """
        logger.info("Atomizing tasks into micro-tasks")

        max_duration = self.config.get(
            "task_atomization.default_micro_task_duration",
            120,
        )

        detailed_roadmap = self.task_atomizer.atomize_to_micro_tasks(
            detailed_roadmap=detailed_roadmap,
            max_duration_minutes=max_duration,
        )

        all_tasks = []
        for phase in detailed_roadmap.phases:
            all_tasks.extend(phase.micro_tasks)

        logger.info(f"Created {len(all_tasks)} micro-tasks")

        return all_tasks

    def generate_workspace(
        self,
        roadmap: TaskRoadmap,
    ) -> ProjectWorkspace:
        """
        Generate Obsidian workspace for project
        """
        logger.info(f"Generating workspace for {roadmap.project_name}")

        workspace = self.workspace_generator.generate_workspace(
            project_name=roadmap.project_name,
            project_description=roadmap.project_description,
            project_type=roadmap.domain,
            roadmap=roadmap,
        )

        return workspace

    def start_micro_task(
        self,
        task: MicroTask,
    ) -> None:
        """
        User starts a micro-task
        """
        task.start()
        self._add_coach_message(
            f"Started: {task.title}. "
            f"You have ~{task.estimated_duration_minutes} minutes. Let's go! 💪"
        )

    def complete_micro_task(
        self,
        task: MicroTask,
        verification_passed: bool = True,
    ) -> None:
        """
        User completes a micro-task
        """
        if verification_passed:
            task.complete()
            self._add_coach_message(
                f"✅ Completed: {task.title}! "
                f"You took {task.elapsed_time_minutes()} minutes. Great work! 🎉"
            )
        else:
            self._add_coach_message(
                f"⚠️ Verification criteria not fully met for {task.title}. "
                f"Try again or ask for help."
            )

    def get_help(
        self,
        task: MicroTask,
        stuck_for_minutes: int = 30,
    ) -> str:
        """
        Provide coaching help when user is stuck
        """
        personality = self.config.get("coach_agent.personality", "encouraging")

        help_messages = {
            "encouraging": [
                f"You've been working for {stuck_for_minutes} minutes. That's progress! 💪\n"
                "Try breaking this down even further, or take a quick break.",
                "Stuck? That's normal - learning means hitting walls.\n"
                "Here are some options:\n"
                "1. Search for similar problems online\n"
                "2. Try a different approach\n"
                "3. Ask for help (post on forums, Discord, etc.)",
                "You're doing great! Sometimes the best solution comes after a break.\n"
                "Try:\n- 10 minute walk\n- Debugging one step at a time\n- Explaining the problem to someone",
            ],
            "formal": [
                f"Task duration: {stuck_for_minutes} minutes.\n"
                "Recommended actions:\n"
                "1. Review task criteria\n"
                "2. Check available resources\n"
                "3. Escalate if necessary",
            ],
            "casual": [
                "Yo, stuck? That's cool, happens to everyone.\n"
                "Maybe try:\n- Check the error message\n- Google it\n- Ask a friend",
            ],
        }

        messages = help_messages.get(personality, help_messages["encouraging"])
        message = messages[hash(task.id) % len(messages)]

        self._add_coach_message(message)

        return message

    def provide_encouragement(self) -> str:
        """
        Provide encouragement to user
        """
        if not self.current_roadmap:
            return ""

        completion = self.current_roadmap.completion_percentage()
        time_spent = self.current_roadmap.total_completed_time_minutes() / 60

        if completion < 25:
            message = (
                f"🚀 You're building momentum! {completion:.0f}% complete.\n"
                "You've put in {:.1f} hours of focused work already. Keep it up!"
            )
        elif completion < 50:
            message = (
                f"💪 Halfway there! {completion:.0f}% complete.\n"
                "You're doing amazing. The second half will be easier!"
            )
        elif completion < 75:
            message = (
                f"🌟 Three-quarters of the way! {completion:.0f}% complete.\n"
                "You're crushing this. The finish line is in sight!"
            )
        else:
            message = (
                f"🏆 Almost there! {completion:.0f}% complete.\n"
                "You're so close. Let's finish strong!"
            )

        message = message.format(time_spent)
        self._add_coach_message(message)

        return message

    def handle_blocker(
        self,
        task: MicroTask,
        blocker_description: str,
    ) -> str:
        """
        Handle when user hits a blocker
        """
        task.block(blocker_description)

        # Search for solutions
        search_results = self.search_engine.search(
            query=f"{task.title} {blocker_description}",
            max_results=5,
        )

        help_text = f"I found some resources that might help:\n\n"

        for result in search_results[:3]:
            help_text += f"- [{result.title}]({result.url}) - {result.source}\n"

        help_text += (
            "\nYou can:\n"
            "1. Try one of these resources\n"
            "2. Break the task into smaller pieces\n"
            "3. Skip this for now and come back later\n"
        )

        self._add_coach_message(help_text)

        return help_text

    def get_next_micro_task(self) -> Optional[MicroTask]:
        """
        Get the next micro-task to work on
        """
        if not self.current_roadmap or not self.current_roadmap.detailed_roadmap:
            return None

        current_phase = self.current_roadmap.detailed_roadmap.get_current_phase()

        if not current_phase:
            return None

        current_task = current_phase.get_current_task()

        if current_task and current_task.status == TaskStatus.COMPLETED:
            # Move to next task in phase
            current_task = current_phase.next_task()

        if not current_task and current_phase.status != TaskStatus.COMPLETED:
            # Phase not started yet
            if current_phase.micro_tasks:
                current_task = current_phase.micro_tasks[0]

        return current_task

    def move_to_next_task(self) -> Optional[MicroTask]:
        """
        Move to next micro-task
        """
        if not self.current_roadmap or not self.current_roadmap.detailed_roadmap:
            return None

        current_phase = self.current_roadmap.detailed_roadmap.get_current_phase()

        if not current_phase:
            return None

        next_task = current_phase.next_task()

        if not next_task:
            # Try next phase
            next_phase = self.current_roadmap.detailed_roadmap.next_phase()
            if next_phase:
                next_task = next_phase.get_current_task()

        if next_task:
            self._add_coach_message(
                f"➡️ Next task: {next_task.title}\n"
                f"Estimated time: {next_task.estimated_duration_minutes} minutes\n"
                f"Ready? Let's go! 🚀"
            )

        return next_task

    def get_status_summary(self) -> Dict[str, Any]:
        """
        Get current progress status
        """
        if not self.current_roadmap:
            return {"status": "no_project"}

        current_task = self.get_next_micro_task()

        return {
            "project_name": self.current_roadmap.project_name,
            "completion_percentage": self.current_roadmap.completion_percentage(),
            "total_micro_tasks": len(self.current_roadmap.get_all_micro_tasks()),
            "completed_tasks": sum(
                1 for t in self.current_roadmap.get_all_micro_tasks()
                if t.status == TaskStatus.COMPLETED
            ),
            "current_task": {
                "title": current_task.title,
                "duration_minutes": current_task.estimated_duration_minutes,
            } if current_task else None,
            "time_spent_hours": self.current_roadmap.total_completed_time_minutes() / 60,
        }

    def _add_coach_message(self, message: str) -> None:
        """Add message to coach log"""
        if self.current_roadmap:
            self.current_roadmap.add_coach_log(message)
