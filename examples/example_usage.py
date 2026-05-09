"""
Example Usage of Coach Everything

This script demonstrates the complete workflow:
1. Start a new project
2. Create an outline
3. Expand to detailed roadmap
4. Atomize into micro-tasks
5. Generate Obsidian workspace
6. Simulate task completion with coaching
"""

from coach import CoachAgent
from coach.config import ConfigManager
from pathlib import Path


def example_learning_python():
    """Example: Learning Python from scratch"""
    print("\n" + "=" * 60)
    print("Example: Learning Python from Scratch")
    print("=" * 60)

    # Initialize config and coach
    config = ConfigManager()
    coach = CoachAgent(config=config)

    # Step 1: Start new project
    print("\n[Step 1] Creating project outline...")
    outline = coach.start_new_project(
        task="Learn Python from scratch",
        domain="learning",
        estimated_hours=30,
        learning_style="hands_on",
    )

    print(f"✅ Created outline with {len(outline.phases)} phases:")
    for i, phase in enumerate(outline.phases, 1):
        print(f"   {i}. {phase}")

    # Step 2: Approve outline
    print("\n[Step 2] Approving outline...")
    outline = coach.wait_for_outline_approval(outline, {"action": "approve"})
    print("✅ Outline approved!")

    # Step 3: Expand to detailed roadmap
    print("\n[Step 3] Expanding to detailed roadmap...")
    roadmap = coach.expand_to_detailed_roadmap(outline)
    print(f"✅ Created {len(roadmap.detailed_roadmap.phases)} phases with steps")

    # Step 4: Atomize to micro-tasks
    print("\n[Step 4] Breaking down into micro-tasks...")
    all_tasks = coach.atomize_to_micro_tasks(roadmap.detailed_roadmap)
    print(f"✅ Created {len(all_tasks)} micro-tasks (1-2 hour each)")

    # Step 5: Generate workspace
    print("\n[Step 5] Generating Obsidian workspace...")
    workspace = coach.generate_workspace(roadmap)
    print(f"✅ Workspace ready: {workspace.workspace_root_path}")

    # Step 6: Simulate task progression
    print("\n[Step 6] Simulating task progression...")

    # Start first task
    first_task = coach.get_next_micro_task()
    if first_task:
        print(f"\n📌 First task: {first_task.title}")
        print(f"   Duration: {first_task.estimated_duration_minutes} minutes")

        coach.start_micro_task(first_task)
        print("✅ Task started!")

        # Simulate completion
        coach.complete_micro_task(first_task, verification_passed=True)
        print("✅ Task completed!")

        # Move to next
        next_task = coach.move_to_next_task()
        if next_task:
            print(f"\n➡️ Next task: {next_task.title}")

    # Show status
    print("\n[Status]")
    status = coach.get_status_summary()
    print(f"Progress: {status['completion_percentage']:.0f}%")
    print(f"Completed: {status['completed_tasks']}/{status['total_micro_tasks']} tasks")

    print("\n✅ Example complete!")


def example_research_project():
    """Example: Starting an ML research project"""
    print("\n" + "=" * 60)
    print("Example: Starting an ML Research Project")
    print("=" * 60)

    config = ConfigManager()
    coach = CoachAgent(config=config)

    print("\n[Creating project outline...]")
    outline = coach.start_new_project(
        task="Build an ML model for time series forecasting",
        domain="research",
        estimated_hours=80,
        learning_style="mixed",
    )

    print(f"\n📋 Research Project Outline:")
    for i, phase in enumerate(outline.phases, 1):
        print(f"   {i}. {phase}")

    outline = coach.wait_for_outline_approval(outline, {"action": "approve"})

    roadmap = coach.expand_to_detailed_roadmap(outline)
    tasks = coach.atomize_to_micro_tasks(roadmap.detailed_roadmap)

    print(f"\n✅ Research plan ready with {len(tasks)} micro-tasks!")

    workspace = coach.generate_workspace(roadmap)
    print(f"📁 Workspace: {workspace.workspace_root_path}")


def example_job_hunting():
    """Example: Job hunting process"""
    print("\n" + "=" * 60)
    print("Example: Job Hunting Process")
    print("=" * 60)

    config = ConfigManager()
    coach = CoachAgent(config=config)

    outline = coach.start_new_project(
        task="Find a software engineering role at top company",
        domain="job_hunting",
        estimated_hours=60,
    )

    print(f"\n🎯 Job hunting roadmap:")
    for phase in outline.phases:
        print(f"   - {phase}")

    outline = coach.wait_for_outline_approval(outline, {"action": "approve"})
    roadmap = coach.expand_to_detailed_roadmap(outline)
    tasks = coach.atomize_to_micro_tasks(roadmap.detailed_roadmap)

    print(f"\n✅ Job search plan ready ({len(tasks)} tasks)")


def example_help_when_stuck():
    """Example: Getting help when stuck"""
    print("\n" + "=" * 60)
    print("Example: Getting Help When Stuck")
    print("=" * 60)

    config = ConfigManager()
    coach = CoachAgent(config=config)

    # Create a simple project
    outline = coach.start_new_project(
        task="Learn web development",
        domain="learning",
    )

    outline = coach.wait_for_outline_approval(outline, {"action": "approve"})
    roadmap = coach.expand_to_detailed_roadmap(outline)
    coach.atomize_to_micro_tasks(roadmap.detailed_roadmap)

    # Simulate getting stuck
    current_task = coach.get_next_micro_task()

    if current_task:
        coach.start_micro_task(current_task)

        print(f"\n📌 Working on: {current_task.title}")
        print("⏳ Stuck for 45 minutes...")

        help_message = coach.get_help(current_task, stuck_for_minutes=45)
        print(f"\n🤖 Coach says:\n{help_message}")

        # Try a blocker
        blocker_help = coach.handle_blocker(
            current_task,
            "Not sure how to set up the development environment"
        )
        print(f"\n{blocker_help}")


def example_progress_and_encouragement():
    """Example: Tracking progress and encouragement"""
    print("\n" + "=" * 60)
    print("Example: Progress Tracking & Encouragement")
    print("=" * 60)

    config = ConfigManager()
    coach = CoachAgent(config=config)

    # Create project
    outline = coach.start_new_project(
        task="Complete Python course",
        domain="learning",
        estimated_hours=40,
    )

    outline = coach.wait_for_outline_approval(outline, {"action": "approve"})
    roadmap = coach.expand_to_detailed_roadmap(outline)
    tasks = coach.atomize_to_micro_tasks(roadmap.detailed_roadmap)

    # Simulate completing some tasks
    print("\n[Completing tasks...]")
    for i, task in enumerate(tasks[:5]):  # Complete first 5 tasks
        coach.start_micro_task(task)
        coach.complete_micro_task(task)
        print(f"   ✅ Completed: {task.title}")

    # Show progress
    print("\n[Progress Status]")
    status = coach.get_status_summary()
    print(f"Project: {status['project_name']}")
    print(f"Progress: {status['completion_percentage']:.0f}%")
    print(f"Tasks: {status['completed_tasks']}/{status['total_micro_tasks']}")

    # Get encouragement
    print("\n[Getting Encouragement...]")
    encouragement = coach.provide_encouragement()
    print(f"\n🤖 {encouragement}")


if __name__ == "__main__":
    print("\n🚀 Coach Everything - Usage Examples\n")

    # Run examples
    example_learning_python()
    example_research_project()
    example_job_hunting()
    example_help_when_stuck()
    example_progress_and_encouragement()

    print("\n" + "=" * 60)
    print("All examples completed! 🎉")
    print("=" * 60)
