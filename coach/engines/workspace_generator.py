"""
Workspace Generator: Creates Obsidian project workspaces
Generates organized folder structure and markdown files
"""

import os
from pathlib import Path
from typing import Optional
from coach.models.workspace import (
    ProjectWorkspace,
    WorkspaceFolder,
    ObsidianNote,
    WORKSPACE_TEMPLATES,
)
from coach.models.roadmap import TaskRoadmap, DetailedRoadmap


class WorkspaceGenerator:
    """
    Generates and manages Obsidian project workspaces
    """

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(parents=True, exist_ok=True)

    def generate_workspace(
        self,
        project_name: str,
        project_description: str,
        project_type: str = "learning",
        roadmap: Optional[TaskRoadmap] = None,
    ) -> ProjectWorkspace:
        """
        Generate a complete project workspace
        """
        workspace = ProjectWorkspace(
            project_name=project_name,
            workspace_root_path=str(self.vault_path / project_name),
        )

        # Create root directory
        workspace_path = self.vault_path / project_name
        workspace_path.mkdir(parents=True, exist_ok=True)

        # Create core files
        workspace.roadmap_note = self._create_roadmap_file(
            workspace_path=workspace_path,
            project_name=project_name,
            project_description=project_description,
            roadmap=roadmap,
        )

        workspace.task_progress_note = self._create_progress_file(
            workspace_path=workspace_path,
            roadmap=roadmap,
        )

        workspace.coach_log_note = self._create_coach_log_file(
            workspace_path=workspace_path,
        )

        # Create folder structure
        workspace.resources_folder = self._create_folder_structure(
            workspace_path=workspace_path,
            folder_name="📚 Resources",
            description="Learning materials, guides, and references",
        )

        workspace.notes_folder = self._create_folder_structure(
            workspace_path=workspace_path,
            folder_name="📝 Notes",
            description="Your personal notes and insights",
        )

        workspace.data_folder = self._create_folder_structure(
            workspace_path=workspace_path,
            folder_name="📁 Data",
            description="Project files, code, data (git-ignored)",
        )

        workspace.archive_folder = self._create_folder_structure(
            workspace_path=workspace_path,
            folder_name="📦 Archive",
            description="Completed tasks and historical reference",
        )

        # Add .gitignore for data folder
        self._create_gitignore(workspace_path / "📁 Data")

        workspace.is_initialized = True
        return workspace

    def _create_roadmap_file(
        self,
        workspace_path: Path,
        project_name: str,
        project_description: str,
        roadmap: Optional[TaskRoadmap] = None,
    ) -> ObsidianNote:
        """Create the roadmap markdown file"""
        content = self._generate_roadmap_markdown(
            project_name=project_name,
            project_description=project_description,
            roadmap=roadmap,
        )

        file_path = workspace_path / "📋 Roadmap.md"
        file_path.write_text(content, encoding="utf-8")

        note = ObsidianNote(
            filename="📋 Roadmap.md",
            path="📋 Roadmap.md",
            content=content,
        )

        return note

    def _create_progress_file(
        self,
        workspace_path: Path,
        roadmap: Optional[TaskRoadmap] = None,
    ) -> ObsidianNote:
        """Create the task progress tracking file"""
        content = self._generate_progress_markdown(roadmap)

        file_path = workspace_path / "📊 Task Progress.md"
        file_path.write_text(content, encoding="utf-8")

        note = ObsidianNote(
            filename="📊 Task Progress.md",
            path="📊 Task Progress.md",
            content=content,
        )

        return note

    def _create_coach_log_file(
        self,
        workspace_path: Path,
    ) -> ObsidianNote:
        """Create the coach log file"""
        content = """# 🤖 Coach Log

Personal coaching feedback and encouragement from Coach Everything.

## Getting Started

Welcome to your personalized coaching workspace! 🎉

Your Coach is here to:
- 📌 Keep you focused on the next micro-task
- 💪 Celebrate your progress
- 🆘 Help when you get stuck
- 📝 Track your journey

## Recent Messages

_(Coach messages will appear here as you work)_

---

## How to Get Help

When stuck, type in your editor:
```
coach help
```

Or just let the Coach know what's blocking you, and it will suggest next steps.

---

**Last Updated**: _Coach will update this automatically_
"""

        file_path = workspace_path / "🤖 Coach Log.md"
        file_path.write_text(content, encoding="utf-8")

        note = ObsidianNote(
            filename="🤖 Coach Log.md",
            path="🤖 Coach Log.md",
            content=content,
        )

        return note

    def _create_folder_structure(
        self,
        workspace_path: Path,
        folder_name: str,
        description: str,
    ) -> WorkspaceFolder:
        """Create a folder with README"""
        folder_path = workspace_path / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)

        # Create folder README
        readme_content = f"""# {folder_name}

{description}

---

You can organize your files here however works best for you.

## Structure Ideas

- Organize by topic
- Organize by date
- Organize by importance
- Use tags for cross-cutting themes

## Links

- [[📋 Roadmap]] - See overall roadmap
- [[📊 Task Progress]] - Track progress
- [[🤖 Coach Log]] - Get coaching feedback
"""

        readme_path = folder_path / "README.md"
        readme_path.write_text(readme_content, encoding="utf-8")

        return WorkspaceFolder(
            name=folder_name,
            path=folder_name,
            description=description,
        )

    def _create_gitignore(self, folder_path: Path) -> None:
        """Create .gitignore for data folder"""
        gitignore_content = """# Ignore most files in data folder
# You'll use git to track code, but data goes to DVC

*
!.gitignore
!README.md

# Exception: Keep source code if tracked separately
# !*.py
# !*.r
# !*.sql
"""
        gitignore_path = folder_path / ".gitignore"
        gitignore_path.write_text(gitignore_content, encoding="utf-8")

    @staticmethod
    def _generate_roadmap_markdown(
        project_name: str,
        project_description: str,
        roadmap: Optional[TaskRoadmap] = None,
    ) -> str:
        """Generate roadmap markdown content"""
        content = f"""# 📋 {project_name} Roadmap

## Project Description

{project_description}

---

## Overall Goal

Achieve clear competency in {project_name.lower()} through structured, progressive learning.

---

## Roadmap Outline

### Phase 1: Setup & Fundamentals
- [ ] Understand core concepts
- [ ] Set up your environment
- [ ] Complete foundational exercises

### Phase 2: Core Learning
- [ ] Study main topics
- [ ] Practice with exercises
- [ ] Build understanding through examples

### Phase 3: Hands-on Application
- [ ] Build a small project
- [ ] Apply concepts in practice
- [ ] Integrate learning

### Phase 4: Advanced Topics & Mastery
- [ ] Explore advanced concepts
- [ ] Refine your skills
- [ ] Prepare for independent work

---

## Key Milestones

- ⭐ Milestone 1: [Milestone description]
- ⭐ Milestone 2: [Milestone description]
- ⭐ Final: Complete project and demonstrate mastery

---

## Resources

See [[📚 Resources]] folder for curated learning materials.

---

## Progress Notes

_(Update as you progress)_

**Last Updated**: {datetime.now().isoformat()}

---

## Links

- [[📊 Task Progress]] - Current micro-tasks
- [[📚 Resources]] - Learning materials
- [[📝 Notes]] - Your learning notes
- [[🤖 Coach Log]] - Coaching feedback
"""

        if roadmap and roadmap.outline:
            content += f"""

## Roadmap Details

**Project**: {roadmap.project_name}
**Domain**: {roadmap.domain}
**Learning Style**: {roadmap.learning_style}

**Estimated Time**: {roadmap.total_time_estimate_hours()} hours

**Phases**:
"""
            for i, phase_name in enumerate(roadmap.outline.phases, 1):
                content += f"- [ ] Phase {i}: {phase_name}\n"

        return content

    @staticmethod
    def _generate_progress_markdown(
        roadmap: Optional[TaskRoadmap] = None,
    ) -> str:
        """Generate progress tracking markdown"""
        content = """# 📊 Task Progress Tracker

Keep track of your micro-tasks and completion status.

---

## Current Phase

_(Will update as you work)_

---

## Micro-Tasks

### Phase 1

- [ ] **Task 1.1**: [Description]
  - ⏱️ Estimated: 60 minutes
  - 🎯 Verification: [What success looks like]
  - 📝 Notes: _Add notes as you work_

- [ ] **Task 1.2**: [Description]
  - ⏱️ Estimated: 90 minutes
  - 🎯 Verification: [What success looks like]

---

### Phase 2

- [ ] **Task 2.1**: [Description]

---

## Completed Tasks

_(Celebrate your progress!)_

---

## Notes & Reflections

What you've learned so far:

-
-
-

---

## Blockers & Questions

_(Things you're stuck on)_

-
-

---

## How to Use This

1. **Check current task**: Which box is unchecked and first in priority?
2. **Work on it**: Spend 1-2 hours focused on this task
3. **Verify**: Does it meet the verification criteria? ✅
4. **Check it off**: Mark as complete
5. **Move to next**: Go to the next unchecked task

**Remember**: You're making progress every time you complete a task! 🎉

---

**Last Updated**: _(Auto-updated by Coach)_
"""

        if roadmap and roadmap.detailed_roadmap:
            content += "\n## Detailed Progress\n\n"
            for phase in roadmap.detailed_roadmap.phases:
                content += f"### {phase.name}\n\n"
                for task in phase.micro_tasks:
                    status = "✅" if task.status.value == "completed" else "⏳"
                    content += f"- {status} {task.title}\n"
                content += "\n"

        return content

    @staticmethod
    def create_template_workspace(
        workspace_path: Path,
        template_type: str = "learning",
    ) -> None:
        """Create workspace from template"""
        if template_type not in WORKSPACE_TEMPLATES:
            template_type = "learning"

        template = WORKSPACE_TEMPLATES[template_type]
        workspace_path.mkdir(parents=True, exist_ok=True)

        for item_name, description in template["structure"].items():
            if item_name.endswith("/"):
                # Create folder
                folder_path = workspace_path / item_name
                folder_path.mkdir(parents=True, exist_ok=True)
            else:
                # Create file
                file_path = workspace_path / item_name
                file_path.touch()


# Helper for markdown generation
from datetime import datetime
