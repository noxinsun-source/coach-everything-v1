"""
Handle user modifications to tasks and micro-tasks
"""

from typing import List, Optional
from coach.models.task import MicroTask, TaskStatus, VerificationCriteria


class TaskFeedbackHandler:
    """
    Handles user feedback and modifications to micro-tasks
    """

    def __init__(self):
        pass

    def process_feedback(
        self,
        task: MicroTask,
        feedback_type: str,
        feedback_data: dict,
    ) -> MicroTask:
        """
        Process user feedback on task
        feedback_type: "split", "merge", "extend_time", "update_description", "mark_blocked"
        """
        if feedback_type == "split":
            return self.split_task(task, feedback_data)
        elif feedback_type == "extend_time":
            return self.extend_time(task, feedback_data)
        elif feedback_type == "update_description":
            return self.update_description(task, feedback_data)
        elif feedback_type == "mark_blocked":
            return self.mark_blocked(task, feedback_data)
        elif feedback_type == "update_verification":
            return self.update_verification(task, feedback_data)
        else:
            return task

    def split_task(
        self,
        task: MicroTask,
        feedback_data: dict,
    ) -> MicroTask:
        """
        Split task into smaller pieces
        Reduce estimated duration
        """
        original_duration = task.estimated_duration_minutes
        task.estimated_duration_minutes = max(30, original_duration // 2)

        task.notes += f"\n[User split this task from {original_duration}m to {task.estimated_duration_minutes}m]"

        return task

    def extend_time(
        self,
        task: MicroTask,
        feedback_data: dict,
    ) -> MicroTask:
        """Extend time estimate"""
        new_duration = feedback_data.get("new_duration_minutes")
        reason = feedback_data.get("reason", "")

        if new_duration and new_duration > task.estimated_duration_minutes:
            old_duration = task.estimated_duration_minutes
            task.estimated_duration_minutes = new_duration
            task.notes += f"\n[Extended from {old_duration}m to {new_duration}m. Reason: {reason}]"

        return task

    def update_description(
        self,
        task: MicroTask,
        feedback_data: dict,
    ) -> MicroTask:
        """Update task description"""
        new_description = feedback_data.get("new_description")

        if new_description:
            task.description = new_description
            task.notes += "\n[Description updated by user]"

        return task

    def mark_blocked(
        self,
        task: MicroTask,
        feedback_data: dict,
    ) -> MicroTask:
        """Mark task as blocked"""
        blocker_reason = feedback_data.get("reason")

        task.block(blocker_reason)
        task.notes += f"\n[Marked as blocked: {blocker_reason}]"

        return task

    def update_verification(
        self,
        task: MicroTask,
        feedback_data: dict,
    ) -> MicroTask:
        """Update verification criteria"""
        new_description = feedback_data.get("description")
        new_examples = feedback_data.get("examples", [])
        new_command = feedback_data.get("command")

        if not task.verification_criteria:
            task.verification_criteria = VerificationCriteria(
                description=new_description or "Verify completion"
            )

        if new_description:
            task.verification_criteria.description = new_description

        if new_examples:
            task.verification_criteria.examples = new_examples

        if new_command:
            task.verification_criteria.command = new_command

        task.notes += "\n[Verification criteria updated]"

        return task

    def validate_task(self, task: MicroTask) -> tuple[bool, List[str]]:
        """Validate task has required components"""
        errors = []

        if not task.title:
            errors.append("Task must have a title")

        if task.estimated_duration_minutes < 15:
            errors.append("Task should be at least 15 minutes")

        if task.estimated_duration_minutes > 240:
            errors.append("Task should not exceed 4 hours (try splitting)")

        if not task.verification_criteria:
            errors.append("Task should have verification criteria")

        return len(errors) == 0, errors

    def suggest_next_task(self, current_task: MicroTask) -> Optional[str]:
        """Suggest next steps after completing task"""
        suggestions = [
            "🎉 Great work! Celebrate this completion.",
            "📝 Document what you learned.",
            "🔍 Review your work for quality.",
            "➡️ Move to the next task.",
            "🤔 Reflect on what could improve next time.",
        ]

        # Rotate suggestions
        suggestion_index = hash(current_task.id) % len(suggestions)
        return suggestions[suggestion_index]
