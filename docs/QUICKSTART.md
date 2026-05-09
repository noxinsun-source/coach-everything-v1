# Coach Everything - Quick Start Guide

Get started with Coach Everything in 5 minutes.

## Installation

### Option 1: Pip Install (Recommended for Users)

```bash
pip install coach-everything
coach init
```

### Option 2: Git Clone (Recommended for Development)

```bash
git clone https://github.com/yourusername/coach-everything.git
cd coach-everything
pip install -e .
coach init
```

## First Project

### 1. Start a Project

```bash
coach start
```

You'll be prompted:
```
What do you want to learn/build?
> I want to learn Python from scratch

What domain? (learning/research/job_hunting/startup)
> learning

Estimated total hours?
> 30
```

### 2. Review the Roadmap

Coach will create an outline:
```
📋 Roadmap Outline:

Title: Learn Python from scratch
Estimated: 30h (4w)

Phases:
1. Setup & Fundamentals
2. Core Concepts & Fundamentals
3. Hands-on Practice
4. Projects & Application
5. Advanced Topics
```

### 3. Approve (or Edit)

```bash
Does this roadmap look good?
Approve this outline? [y/N]
> y
```

Coach will then:
- ✅ Expand to detailed steps
- ✅ Create micro-tasks (1-2 hours each)
- ✅ Generate Obsidian workspace

### 4. Start Working

```bash
coach status
```

Shows current progress:
```
📊 Project Status:
Project: Learn Python from scratch
Progress: 0%
Tasks: 0/24 completed
Time spent: 0.0 hours

📌 Current task: Install Python and set up IDE
   Estimated: 60 minutes
```

### 5. Get Help When Stuck

```bash
coach help
```

Coach responds with:
- Suggested approaches
- Similar experiences from others
- Resources to check out

### 6. Track Progress

```bash
coach next
```

Moves to the next micro-task and updates your workspace.

## Common Commands

| Command | What It Does |
|---------|--------------|
| `coach start` | Start a new project |
| `coach status` | See current progress |
| `coach next` | Move to next task |
| `coach help` | Get coaching when stuck |
| `coach encourage` | Get motivation |
| `coach config` | View configuration |

## Folder Structure

After running `coach start`, you'll have:

```
~/Documents/Obsidian Vault/
└── Learn Python from scratch/
    ├── 📋 Roadmap.md              ← Your approved outline
    ├── 📊 Task Progress.md        ← Current micro-tasks
    ├── 🤖 Coach Log.md            ← Coaching messages
    ├── 📚 Resources/              ← Links to guides
    ├── 📝 Notes/                  ← Your learning notes
    ├── 📁 Data/                   ← Code, files (git-ignored)
    └── 📦 Archive/                ← Completed tasks
```

## Configuration

Coach stores settings in `~/.coach/config.yaml`:

```yaml
# Obsidian vault location
obsidian_vault_path: /Users/you/Documents/Obsidian Vault

# What platforms to search
search:
  platforms: [reddit, github, forums, blogs]
  include_papers: true

# Micro-task size (in minutes)
task_atomization:
  default_micro_task_duration: 120

# Coach personality
coach_agent:
  personality: encouraging
  check_in_frequency: 60  # minutes
```

## Examples

### Learning Python

```bash
coach start
# Task: Learn Python from scratch
# Domain: learning
# Hours: 30
```

### Research Project

```bash
coach start
# Task: Build ML model for time series forecasting
# Domain: research
# Hours: 80
```

### Job Hunting

```bash
coach start
# Task: Find software engineer role
# Domain: job_hunting
# Hours: 60
```

### Building a Startup

```bash
coach start
# Task: Launch SaaS product
# Domain: startup
# Hours: 200
```

## Workflow

1. **Start** project → outline created
2. **Approve** outline → gets expanded
3. **View** task progress → see what's next
4. **Work** on micro-tasks → 1-2 hours each
5. **Get help** when stuck → Coach suggests solutions
6. **Complete** tasks → track progress
7. **Celebrate** milestones → Coach encourages

## Tips for Success

### 1. **Approve Each Stage**
- Don't skip approving the outline
- Review detailed steps before starting
- Tweak verification criteria to match your pace

### 2. **Respect Time Estimates**
- Micro-tasks are 1-2 hours for a reason
- If a task takes 3+ hours, split it
- If a task takes <30 min, combine it

### 3. **Use Verification Criteria**
- They keep you on track
- They define "done"
- They help celebrate progress

### 4. **Review Resources Regularly**
- Coach finds proven strategies for you
- Check the Resources folder
- Don't reinvent the wheel

### 5. **Take Breaks**
- Coach can help you every 60 minutes
- Stand up, move around
- Come back fresh

### 6. **Document Learning**
- Use the Notes folder
- Reference what you learn
- Help your future self

## Troubleshooting

### "No config file found"

```bash
coach init
```

Initialize Coach first.

### "Obsidian vault path not set"

Edit `~/.coach/config.yaml`:
```yaml
obsidian_vault_path: /path/to/your/vault
```

### "Search results not helpful"

Coach searches real experiences, not generic guides. Results quality depends on query. Try:
- More specific queries
- Different keywords
- Check multiple sources

### "Task time estimate too short"

```bash
coach next  # Skip this task
```

Return later, or:
```bash
# Edit config to extend default
task_atomization:
  default_micro_task_duration: 180  # 3 hours
```

## Next Steps

1. **Start your first project**
   ```bash
   coach start
   ```

2. **Read the full docs**
   - See `docs/` folder
   - Architecture guide
   - API reference

3. **Join the community**
   - GitHub discussions
   - Report issues
   - Share projects

4. **Customize Coach**
   - Edit config file
   - Add favorite domains
   - Set personality

---

**You're ready! Let's get started. 🚀**

Run `coach start` and begin your journey!
