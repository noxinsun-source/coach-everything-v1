"""
Coach Everything CLI Entry Point
"""

import click
import logging
from typing import Optional
from pathlib import Path

from coach.agent import CoachAgent
from coach.config import ConfigManager, init_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def cli(ctx):
    """
    🚀 Coach Everything - Universal Task Breakdown & AI Coaching Agent

    Break down any task into manageable micro-steps. Get personalized guidance.
    Never feel stuck on "what to do next" again.
    """
    if ctx.invoked_subcommand is None:
        click.echo(cli.get_help(ctx))


@cli.command()
def init():
    """Initialize Coach Everything"""
    click.echo("🚀 Initializing Coach Everything...")

    config = init_config()

    # Create cache directory
    cache_dir = Path.home() / ".coach"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Save default config
    config.save_config()

    click.echo(f"✅ Initialized!")
    click.echo(f"Configuration: {config.config_path}")
    click.echo(f"Cache directory: {cache_dir}")
    click.echo("\nNext: Try 'coach start' to begin a project")


@cli.command()
@click.option(
    '--task',
    prompt='What do you want to learn/build?',
    help='The task or goal',
)
@click.option(
    '--domain',
    prompt='What domain? (learning/research/job_hunting/startup)',
    default='learning',
    help='Domain or project type',
)
@click.option(
    '--hours',
    default=20,
    help='Estimated total hours',
)
@click.pass_context
def start(ctx, task: str, domain: str, hours: int):
    """Start a new project"""
    click.echo("\n🚀 Starting new project...")
    click.echo(f"Task: {task}")
    click.echo(f"Domain: {domain}")

    config = ConfigManager()
    coach = CoachAgent(config=config)

    # Create outline
    with click.progressbar(
        length=100,
        label="Searching for proven strategies...",
    ) as bar:
        outline = coach.start_new_project(
            task=task,
            domain=domain,
            estimated_hours=hours,
        )
        bar.update(100)

    # Display outline
    click.echo("\n📋 Roadmap Outline:\n")
    click.echo(f"Title: {outline.title}")
    click.echo(f"Estimated: {outline.estimated_total_hours}h ({outline.estimated_weeks}w)")
    click.echo("\nPhases:")
    for i, phase in enumerate(outline.phases, 1):
        click.echo(f"  {i}. {phase}")

    # Ask for approval
    click.echo("\nDoes this roadmap look good?")
    if click.confirm("Approve this outline?"):
        outline = coach.wait_for_outline_approval(
            outline,
            {"action": "approve"}
        )
        click.echo("✅ Outline approved!")

        # Expand to detailed roadmap
        with click.progressbar(
            length=100,
            label="Creating detailed roadmap...",
        ) as bar:
            roadmap = coach.expand_to_detailed_roadmap(outline)
            bar.update(50)

            # Atomize to micro-tasks
            tasks = coach.atomize_to_micro_tasks(roadmap.detailed_roadmap)
            bar.update(50)

        click.echo(f"\n✅ Created {len(tasks)} micro-tasks!")

        # Generate workspace
        with click.progressbar(
            length=100,
            label="Generating Obsidian workspace...",
        ) as bar:
            workspace = coach.generate_workspace(roadmap)
            bar.update(100)

        click.echo(f"✅ Workspace created at: {workspace.workspace_root_path}")
        click.echo("\n🎉 Project ready! Next step: 'coach status'")

    else:
        click.echo("Edit the outline and try again.")


@cli.command()
@click.pass_context
def status(ctx):
    """Show current project status"""
    config = ConfigManager()
    coach = CoachAgent(config=config)

    summary = coach.get_status_summary()

    if summary.get("status") == "no_project":
        click.echo("No active project. Start one with: coach start")
        return

    click.echo("\n📊 Project Status:")
    click.echo(f"Project: {summary['project_name']}")
    click.echo(f"Progress: {summary['completion_percentage']:.0f}%")
    click.echo(
        f"Tasks: {summary['completed_tasks']}/{summary['total_micro_tasks']} completed"
    )
    click.echo(f"Time spent: {summary['time_spent_hours']:.1f} hours")

    if summary.get("current_task"):
        click.echo(f"\n📌 Current task: {summary['current_task']['title']}")
        click.echo(
            f"   Estimated: {summary['current_task']['duration_minutes']} minutes"
        )

    click.echo("\nNext: 'coach next' to move forward, or 'coach help' if stuck")


@cli.command()
@click.pass_context
def next(ctx):
    """Move to next micro-task"""
    config = ConfigManager()
    coach = CoachAgent(config=config)

    next_task = coach.move_to_next_task()

    if next_task:
        click.echo(f"\n➡️ Next task: {next_task.title}")
        click.echo(f"Estimated: {next_task.estimated_duration_minutes} minutes")
        if next_task.verification_criteria:
            click.echo(
                f"Verification: {next_task.verification_criteria.description}"
            )
    else:
        click.echo("No more tasks! 🎉 Project complete!")


@cli.command()
@click.pass_context
def help(ctx):
    """Get coaching help"""
    config = ConfigManager()
    coach = CoachAgent(config=config)

    current_task = coach.get_next_micro_task()

    if current_task:
        help_message = coach.get_help(current_task, stuck_for_minutes=45)
        click.echo("\n🤖 Coach says:\n")
        click.echo(help_message)
    else:
        click.echo("Start a project first: coach start")


@cli.command()
@click.pass_context
def encourage(ctx):
    """Get encouragement from Coach"""
    config = ConfigManager()
    coach = CoachAgent(config=config)

    message = coach.provide_encouragement()
    click.echo(f"\n🤖 Coach says:\n")
    click.echo(message)


@cli.command()
@click.pass_context
def config(ctx):
    """Show current configuration"""
    config_manager = ConfigManager()

    click.echo("\n⚙️ Current Configuration:\n")
    click.echo(f"Config file: {config_manager.config_path}")
    click.echo(f"Vault path: {config_manager.get('obsidian_vault_path')}")
    click.echo(f"Search platforms: {config_manager.get('search.platforms')}")
    click.echo(f"Micro-task duration: {config_manager.get('task_atomization.default_micro_task_duration')}m")
    click.echo(f"Coach personality: {config_manager.get('coach_agent.personality')}")


@cli.command()
@click.pass_context
def version(ctx):
    """Show version"""
    from coach import __version__
    click.echo(f"Coach Everything v{__version__}")


if __name__ == '__main__':
    cli()
