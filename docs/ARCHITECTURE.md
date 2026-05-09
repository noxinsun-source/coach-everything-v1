# Coach Everything - Architecture Guide

## System Overview

Coach Everything is a modular system for breaking down complex tasks into manageable micro-steps and providing real-time AI coaching.

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Interface                         │
│              (coach start / status / next)               │
└────────────────┬────────────────────────────────────────┘
                 │
         ┌───────▼─────────┐
         │   Coach Agent   │  ◄─ Orchestrator
         └───────┬─────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌────────┐  ┌──────────┐  ┌─────────────────┐
│ Search │  │ Task     │  │ Workspace       │
│ Engine │  │ Atomizer │  │ Generator       │
└────────┘  └──────────┘  └─────────────────┘
    │            │              │
    │            │              ▼
    │            │         ┌──────────────┐
    │            │         │  Obsidian    │
    │            │         │  Vault       │
    │            │         │  (User Files)│
    │            │         └──────────────┘
    │            │
    ▼            ▼
┌─────────────────────────────┐
│   Feedback Handlers         │
│ (Roadmap & Task Feedback)   │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│   Storage Layer             │
├─────────────────────────────┤
│ ├─ Cache Manager (SQLite)   │
│ │  (Search, templates)      │
│ └─ Preference Manager       │
│    (User preferences)       │
└─────────────────────────────┘
```

## Core Components

### 1. Coach Agent (`coach/agent.py`)

**Role**: Main orchestrator that coordinates all subsystems

**Responsibilities**:
- Initiate project creation
- Manage task progression
- Provide real-time coaching
- Track progress

**Key Methods**:
- `start_new_project()` - Stage 1: Create outline
- `expand_to_detailed_roadmap()` - Stage 2: Expand to steps
- `atomize_to_micro_tasks()` - Stage 3: Create micro-tasks
- `generate_workspace()` - Create Obsidian vault structure
- `start_micro_task()` / `complete_micro_task()` - Task tracking
- `get_help()` - Coaching support

### 2. Search Engine (`coach/engines/search_engine.py`)

**Role**: Find proven strategies from real people

**Searches**:
- Reddit (r/learnprogramming, r/IWantToLearn, etc.)
- GitHub (repositories, code examples)
- Forums (Stack Overflow, Dev.to)
- Blogs (personal blogs, Medium)
- Academic papers (arXiv, OpenReview)

**Multi-dimensional Search**:
- Platform filtering (Reddit vs. GitHub vs. Forums)
- Domain specificity ("machine learning" vs. "Python")
- Recency weighting (prefer recent advice)
- Content type (guides, tips, code examples)

**Output**: `SearchResult` objects with:
- Title, URL, source
- Summary, author, date
- Upvotes/popularity
- Relevance score

### 3. Task Atomizer (`coach/engines/task_atomizer.py`)

**Role**: Progressive refinement from vague goal to 1-2 hour micro-tasks

**Three Stages**:

#### Stage 1: Outline
```
Input: "Learn machine learning"
Output: RoadmapOutline with 5 phases
  - Phase 1: Setup & Fundamentals
  - Phase 2: Core Concepts
  - Phase 3: Hands-on Practice
  - Phase 4: First Project
  - Phase 5: Advanced Topics
```

#### Stage 2: Detailed Roadmap
```
Input: Approved outline
Output: DetailedRoadmap with TaskPhases
  Each phase contains specific, actionable steps
  - Setup environment
  - Learn Python syntax
  - Understand variables and loops
  - Complete first exercises
  ...
```

#### Stage 3: Micro-Tasks
```
Input: Detailed roadmap
Output: MicroTask objects
  Each task: 60-120 minutes
  - Clear title
  - Detailed description
  - Verification criteria (testable)
  - Time estimate
```

**Key Classes**:
- `RoadmapOutline` - Phase-level structure
- `DetailedRoadmap` - Step-level detail
- `TaskPhase` - A phase with multiple tasks
- `MicroTask` - Atomic 1-2 hour task

### 4. Workspace Generator (`coach/engines/workspace_generator.py`)

**Role**: Create organized Obsidian project structure

**Creates**:
```
Project Name/
├── 📋 Roadmap.md          (Your approved outline)
├── 📊 Task Progress.md    (Micro-tasks & status)
├── 🤖 Coach Log.md        (AI coaching messages)
├── 📚 Resources/          (Links to materials)
├── 📝 Notes/              (Your learning notes)
├── 📁 Data/               (Project files, git-ignored)
└── 📦 Archive/            (Completed tasks)
```

**Features**:
- Template-based generation
- Markdown with wikilinks
- Auto-generated README files
- Git-ignore for data folder

### 5. Feedback Handlers

#### RoadmapFeedbackHandler
Processes user edits to outline:
- Edit phases
- Add/remove phases
- Adjust timeline
- Approve/reject

#### TaskFeedbackHandler
Processes modifications to micro-tasks:
- Split task (too big)
- Extend time (too optimistic)
- Update description
- Mark blocked
- Update verification criteria

### 6. Storage Layer

#### CacheManager (SQLite)
```sql
search_cache          -- Cached search results
task_templates        -- Pre-built task templates
micro_task_patterns   -- Learned successful patterns
verification_templates-- Verification criteria templates
```

**Benefits**:
- Avoid re-searching
- Reuse templates
- Build knowledge over time

#### PreferenceManager (JSON)
```json
{
  "obsidian_vault_path": "...",
  "search_platforms": [...],
  "micro_task_duration": 120,
  "recent_projects": [...],
  "statistics": {
    "total_tasks_completed": 25,
    "total_hours_spent": 45.5
  }
}
```

## Data Models

### TaskRoadmap
```
TaskRoadmap
├── outline: RoadmapOutline          (Stage 1)
├── detailed_roadmap: DetailedRoadmap (Stage 2)
├── project_name: str
├── domain: str ("learning", "research", etc.)
└── learning_style: str ("visual", "hands_on", etc.)
```

### RoadmapOutline
```
RoadmapOutline
├── phases: List[str]                (["Phase 1", "Phase 2", ...])
├── estimated_total_hours: int
├── approval_status: ApprovalStatus   (PENDING, APPROVED, REJECTED)
└── source_experiences: List[str]     (URLs from search results)
```

### DetailedRoadmap
```
DetailedRoadmap
├── phases: List[TaskPhase]
└── current_phase_index: int

TaskPhase
├── micro_tasks: List[MicroTask]
├── estimated_duration_hours: int
└── description: str

MicroTask
├── title: str
├── description: str
├── estimated_duration_minutes: int   (60-120 recommended)
├── verification_criteria: VerificationCriteria
├── status: TaskStatus                (pending, in_progress, completed)
└── source_experiences: List[str]     (Where this came from)
```

### ProjectWorkspace
```
ProjectWorkspace
├── roadmap_note: ObsidianNote       (📋 Roadmap.md)
├── task_progress_note: ObsidianNote (📊 Task Progress.md)
├── coach_log_note: ObsidianNote     (🤖 Coach Log.md)
├── resources_folder: WorkspaceFolder (📚 Resources/)
├── notes_folder: WorkspaceFolder     (📝 Notes/)
├── data_folder: WorkspaceFolder      (📁 Data/)
└── archive_folder: WorkspaceFolder   (📦 Archive/)
```

## Workflow

### User Journey

```
1. User runs: coach start
   └─> CoachAgent.start_new_project()
       ├─> SearchEngine searches for strategies
       ├─> TaskAtomizer creates outline
       └─> Display outline for approval

2. User approves outline
   └─> CoachAgent.wait_for_outline_approval()
       └─> Mark as APPROVED

3. Outline expanded to detailed roadmap
   └─> CoachAgent.expand_to_detailed_roadmap()
       └─> TaskAtomizer creates phases with steps

4. Detailed roadmap atomized to micro-tasks
   └─> CoachAgent.atomize_to_micro_tasks()
       └─> Each step becomes 1-2 hour micro-task

5. Obsidian workspace generated
   └─> WorkspaceGenerator creates folder structure
       └─> User sees organized project

6. User works on micro-tasks
   └─> CoachAgent.start_micro_task()
   └─> User completes task
   └─> CoachAgent.complete_micro_task()

7. Coach provides support
   └─> CoachAgent.get_help()         (when stuck)
   └─> CoachAgent.handle_blocker()    (when blocked)
   └─> CoachAgent.provide_encouragement() (progress)

8. Progress tracked
   └─> CoachAgent.get_status_summary()
   └─> Coach logs updated
```

## Configuration

Coach uses a three-tier configuration system:

### 1. System Config (`~/.coach/config.yaml`)
```yaml
obsidian_vault_path: /path/to/vault
search:
  platforms: [reddit, github, forums, blogs]
  include_papers: true
  recency_weight: 0.7
task_atomization:
  default_micro_task_duration: 120
  require_approval: true
coach_agent:
  personality: encouraging
  check_in_frequency: 60
```

### 2. Preferences (`~/.coach/preferences.json`)
User's learned preferences, recent projects, statistics

### 3. Code Config (`coach/config.py`)
Pydantic models with validation

## Design Principles

### 1. **Separation of Concerns**
- Search engine only searches
- Atomizer only breaks down
- Workspace generator only creates files
- Agent orchestrates

### 2. **User Approval at Each Stage**
- Never auto-generate everything
- Approve outline, then details, then tasks
- Build trust through transparency

### 3. **Local-First**
- Obsidian vault is user-editable
- SQLite cache is local
- No cloud dependencies

### 4. **Experience-Based**
- Route to real human experiences
- AI finds patterns, humans interpret
- No generic advice

### 5. **ADHD-Friendly**
- Clear "next task" at all times
- 1-2 hour chunks (not vague)
- Regular encouragement
- Progress celebration

## Extensibility

### Adding New Search Platforms
```python
# In SearchEngine class
def _search_custom_platform(self, query, max_results=10):
    # Implement search
    return results
    
# Register in platforms dict
self.platforms['custom'] = self._search_custom_platform
```

### Adding New Task Domains
```python
# In TaskAtomizer._generate_phases_for_domain
domain_phases = {
    "new_domain": [
        "Phase 1: ...",
        "Phase 2: ...",
    ]
}
```

### Custom Verification Criteria
```python
def generate_verification_criteria(task_title, task_type="custom"):
    return VerificationCriteria(
        description="...",
        examples=["...", "..."],
        command="custom --command"
    )
```

## Performance Considerations

### Caching Strategy
- Search results: 24h TTL
- Templates: No expiry
- Patterns: No expiry
- Clear every 7 days

### Database Optimization
- Indices on frequently queried columns
- VACUUM for maintenance
- JSON column storage

### Search Optimization
- Cache popular queries
- Limit results per platform
- Parallel requests (future)

## Error Handling

### Graceful Degradation
- Missing API key → offline mode
- Search timeout → use cache
- Obsidian error → save JSON fallback
- DB error → use in-memory store

### User Feedback
- Clear error messages
- Suggestion for next steps
- No silent failures

## Testing

Core test categories:
- Unit tests (individual components)
- Integration tests (workflow)
- E2E tests (full user journey)

See `tests/` folder for examples.
