"""
Handle user modifications to roadmap outline
"""

from typing import List, Optional
from coach.models.roadmap import RoadmapOutline, ApprovalStatus


class RoadmapFeedbackHandler:
    """
    Handles user feedback and modifications to roadmap outline
    """

    def __init__(self):
        pass

    def process_feedback(
        self,
        outline: RoadmapOutline,
        feedback_type: str,
        feedback_data: dict,
    ) -> RoadmapOutline:
        """
        Process user feedback on roadmap
        feedback_type: "edit_phase", "add_phase", "remove_phase", "adjust_timeline"
        """
        if feedback_type == "edit_phase":
            return self.edit_phase(outline, feedback_data)
        elif feedback_type == "add_phase":
            return self.add_phase(outline, feedback_data)
        elif feedback_type == "remove_phase":
            return self.remove_phase(outline, feedback_data)
        elif feedback_type == "adjust_timeline":
            return self.adjust_timeline(outline, feedback_data)
        elif feedback_type == "approve":
            return self.approve(outline)
        elif feedback_type == "reject":
            return self.reject(outline, feedback_data)
        else:
            return outline

    def edit_phase(
        self,
        outline: RoadmapOutline,
        feedback_data: dict,
    ) -> RoadmapOutline:
        """Edit an existing phase"""
        phase_index = feedback_data.get("index")
        new_name = feedback_data.get("new_name")
        new_description = feedback_data.get("new_description")

        if 0 <= phase_index < len(outline.phases):
            outline.phases[phase_index] = new_name

        if new_description:
            outline.user_feedback += f"\n[Phase {phase_index} edited]: {new_description}"

        outline.approval_status = ApprovalStatus.IN_REVISION
        return outline

    def add_phase(
        self,
        outline: RoadmapOutline,
        feedback_data: dict,
    ) -> RoadmapOutline:
        """Add a new phase"""
        new_phase = feedback_data.get("phase_name")
        position = feedback_data.get("position", len(outline.phases))

        outline.phases.insert(position, new_phase)
        outline.user_feedback += f"\n[Phase added]: {new_phase}"
        outline.approval_status = ApprovalStatus.IN_REVISION

        return outline

    def remove_phase(
        self,
        outline: RoadmapOutline,
        feedback_data: dict,
    ) -> RoadmapOutline:
        """Remove a phase"""
        phase_index = feedback_data.get("index")

        if 0 <= phase_index < len(outline.phases):
            removed_phase = outline.phases.pop(phase_index)
            outline.user_feedback += f"\n[Phase removed]: {removed_phase}"
            outline.approval_status = ApprovalStatus.IN_REVISION

        return outline

    def adjust_timeline(
        self,
        outline: RoadmapOutline,
        feedback_data: dict,
    ) -> RoadmapOutline:
        """Adjust time estimate"""
        new_hours = feedback_data.get("estimated_hours")
        new_weeks = feedback_data.get("estimated_weeks")

        if new_hours:
            outline.estimated_total_hours = new_hours
        if new_weeks:
            outline.estimated_weeks = new_weeks

        outline.user_feedback += (
            f"\n[Timeline adjusted]: {new_hours}h, {new_weeks}w"
        )
        outline.approval_status = ApprovalStatus.IN_REVISION

        return outline

    def approve(
        self,
        outline: RoadmapOutline,
    ) -> RoadmapOutline:
        """Approve the outline"""
        outline.approval_status = ApprovalStatus.APPROVED
        outline.approval_date = datetime.now()
        return outline

    def reject(
        self,
        outline: RoadmapOutline,
        feedback_data: dict,
    ) -> RoadmapOutline:
        """Reject the outline"""
        outline.approval_status = ApprovalStatus.REJECTED
        outline.user_feedback = feedback_data.get("reason", "No specific reason provided")
        return outline

    def validate_outline(self, outline: RoadmapOutline) -> tuple[bool, List[str]]:
        """Validate outline has minimum required components"""
        errors = []

        if not outline.title:
            errors.append("Outline must have a title")

        if not outline.phases or len(outline.phases) < 2:
            errors.append("Outline must have at least 2 phases")

        if outline.estimated_total_hours < 1:
            errors.append("Estimated hours must be at least 1")

        return len(errors) == 0, errors


from datetime import datetime
