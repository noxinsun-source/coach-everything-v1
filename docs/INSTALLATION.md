# Coach Everything - Installation Guide

Complete installation instructions for all platforms.

## Prerequisites

- **Python**: 3.8 or higher
- **Obsidian**: (optional, for workspace features)
- **pip**: Python package manager (comes with Python)

## Installation Methods

### Method 1: Pip Install (Recommended for Users)

The easiest way to get started.

#### Step 1: Install Package

```bash
pip install coach-everything
```

#### Step 2: Initialize Coach

```bash
coach init
```

This creates:
- `~/.coach/config.yaml` - Configuration file
- `~/.coach/cache.db` - SQLite cache
- `~/.coach/preferences.json` - User preferences

#### Step 3: Verify Installation

```bash
coach --version
```

You should see: `Coach Everything v1.0.0`

### Method 2: Git Clone (Recommended for Development)

For contributing or customizing Coach.

#### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/coach-everything.git
cd coach-everything
```

#### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 3: Install in Development Mode

```bash
pip install -e ".[dev]"
```

This installs Coach and development dependencies (pytest, black, etc.)

#### Step 4: Initialize Coach

```bash
coach init
```

#### Step 5: Verify Installation

```bash
coach --version
coach config
```

### Method 3: Docker (Optional)

If you prefer Docker:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install coach-everything

RUN coach init

ENTRYPOINT ["coach"]
```

Build and run:
```bash
docker build -t coach-everything .
docker run -it -v ~/.coach:/root/.coach coach-everything start
```

## Configuration

### Default Configuration

After `coach init`, edit `~/.coach/config.yaml`:

```yaml
# Required: Path to your Obsidian vault
obsidian_vault_path: /Users/yourname/Documents/Obsidian Vault

# Search configuration
search:
  platforms:
    - reddit
    - github
    - forums
    - blogs
  include_papers: true
  recency_weight: 0.7
  max_results_per_platform: 10

# Task configuration
task_atomization:
  default_micro_task_duration: 120  # minutes
  require_approval: true
  include_verification_criteria: true
  refinement_levels: 3

# Coach Agent configuration
coach_agent:
  personality: encouraging  # encouraging, formal, casual
  check_in_frequency: 60    # minutes
  celebrate_milestones: true
  offer_help_threshold: 30  # minutes before suggesting help
```

### Setting Obsidian Vault Path

Coach needs to know where your Obsidian vault is:

```bash
# Edit config
nano ~/.coach/config.yaml

# Or set via environment variable
export COACH_OBSIDIAN_VAULT_PATH="/path/to/vault"
```

## Platform-Specific Setup

### macOS

```bash
# Using Homebrew
brew install python3

# Install Coach
pip3 install coach-everything

# Initialize
coach init
```

### Linux (Ubuntu/Debian)

```bash
# Install Python
sudo apt-get update
sudo apt-get install python3 python3-pip

# Install Coach
pip3 install coach-everything

# Initialize
coach init
```

### Windows

```bash
# Using Python.org installer or Windows Store
# Then in PowerShell or Command Prompt:

pip install coach-everything
coach init
```

### Windows (WSL)

```bash
# In WSL2 terminal
pip install coach-everything
coach init
```

## Troubleshooting Installation

### Issue: "command not found: coach"

**Solution**:
```bash
# Make sure Coach is in PATH
which coach  # or 'where coach' on Windows

# If not found, reinstall
pip uninstall coach-everything
pip install coach-everything

# Add to PATH if needed
export PATH="$PATH:$(python -m site --user-base)/bin"
```

### Issue: "ModuleNotFoundError"

**Solution**:
```bash
# Verify installation
python -c "import coach; print(coach.__version__)"

# Reinstall with verbose output
pip install -vv coach-everything
```

### Issue: "Permission denied"

**Solution**:
```bash
# Use --user flag
pip install --user coach-everything

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install coach-everything
```

### Issue: "Obsidian vault path not found"

**Solution**:
```yaml
# Edit ~/.coach/config.yaml
obsidian_vault_path: /Users/yourname/Documents/Obsidian Vault

# Make sure the path exists
mkdir -p "/Users/yourname/Documents/Obsidian Vault"
```

### Issue: "Database locked"

**Solution**:
```bash
# SQLite cache issue, usually resolves on restart
# If persistent:
rm ~/.coach/coach_cache.db
coach init
```

## Upgrading Coach

### From Pip

```bash
pip install --upgrade coach-everything
```

### From Git Clone

```bash
cd coach-everything
git pull origin main
pip install -e .
```

## Uninstalling Coach

### Pip

```bash
pip uninstall coach-everything
```

### Keep Configuration (Optional)

Coach stores settings in `~/.coach/`. To keep them:
- Configuration files stay in `~/.coach/`
- Only package code is removed

To remove everything:
```bash
rm -rf ~/.coach/
```

## Optional Dependencies

### Paper Search (Academic Papers)

```bash
pip install arxiv
```

Enables searching arXiv and OpenReview for research papers.

### Anthropic API (For Future Features)

```bash
pip install anthropic
```

Required for future AI-powered coaching features.

### Development Tools

```bash
pip install -e ".[dev]"
```

Installs testing and linting tools:
- pytest - Testing framework
- black - Code formatter
- flake8 - Linter
- mypy - Type checker

## Verification

### Check Installation

```bash
# Show version
coach --version

# Show help
coach --help

# Show configuration
coach config
```

### Test Basic Functionality

```bash
# Start a test project
coach start

# Answer prompts
# Task: "Test learning Python"
# Domain: "learning"
# Hours: 10

# Check status
coach status
```

## Getting Help

### Command Help

```bash
coach --help
coach start --help
coach status --help
```

### Documentation

- **Quick Start**: Read `docs/QUICKSTART.md`
- **Full Guide**: Read `docs/USAGE_GUIDE.md`
- **Architecture**: Read `docs/ARCHITECTURE.md`

### Community

- GitHub Issues: Report bugs
- GitHub Discussions: Ask questions
- GitHub Pull Requests: Contribute improvements

## System Requirements

### Minimum

- Python 3.8+
- 100 MB disk space
- Internet connection (for searches)

### Recommended

- Python 3.10+
- 500 MB disk space (for cache)
- Obsidian (for best workspace experience)
- 2+ GB RAM

### Optional

- Git (for development)
- Docker (for containerized use)
- Academic paper access (for advanced search)

## Environment Variables

### Optional Configuration

```bash
# Set Obsidian vault path
export COACH_OBSIDIAN_VAULT_PATH="/path/to/vault"

# Set cache directory
export COACH_CACHE_DIR="~/.coach"

# Set log level
export COACH_LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR

# Disable paper search (no arxiv)
export COACH_DISABLE_PAPERS="true"
```

## Next Steps

After installation:

1. Run `coach init` if you haven't already
2. Read `docs/QUICKSTART.md`
3. Start your first project with `coach start`
4. Check the generated Obsidian workspace
5. Begin working on your first micro-task!

---

**Happy learning! 🚀**

Questions? Check the documentation or open a GitHub issue.
