# Publishing Coach Everything to GitHub

Complete step-by-step instructions to publish the project to GitHub.

## Prerequisites

1. GitHub account ([Sign up here](https://github.com))
2. Git installed ([Download here](https://git-scm.com))
3. GitHub CLI (optional but recommended) ([Download here](https://cli.github.com))

## Step-by-Step Guide

### Option A: Using GitHub CLI (Recommended - 3 steps)

```bash
# Step 1: Navigate to project directory
cd /tmp/coach-everything

# Step 2: Initialize git and create repository
gh repo create coach-everything \
  --public \
  --description "Universal Task Breakdown & AI Coaching Agent" \
  --source=. \
  --push

# Done! Your repo is now on GitHub
```

### Option B: Using Git Commands

#### Step 1: Initialize Git Repository

```bash
cd /tmp/coach-everything

git init
git add .
git config user.name "Your Name"
git config user.email "your.email@example.com"
git commit -m "Initial commit: Coach Everything v1.0.0

- Complete CLI tool for task breakdown
- Multi-dimensional search engine
- Progressive task atomization
- Obsidian workspace generation
- Real-time coaching agent
- SQLite caching
- MIT License"
```

#### Step 2: Create Repository on GitHub

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `coach-everything`
3. Description: "Universal Task Breakdown & AI Coaching Agent for ADHD and executive function"
4. Visibility: **Public**
5. **Do NOT** initialize with README (we have one)
6. Click "Create repository"

#### Step 3: Add Remote and Push

```bash
cd /tmp/coach-everything

# Add remote (replace USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/coach-everything.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

## After Publishing

### 1. Update README.md Links

In `README.md`, replace these placeholders:

```markdown
# Change these:
[github/langchain-ai/langgraph](url)
https://github.com/yourusername/coach-everything

# To your actual URLs:
https://github.com/YOUR_USERNAME/coach-everything
```

Update in:
- README.md (GitHub URL references)
- setup.py (repository URL)
- pyproject.toml (project URLs)
- docs/ARCHITECTURE.md (any GitHub links)

```bash
# Quick replacement (macOS/Linux)
sed -i 's|yourusername|YOUR_USERNAME|g' README.md setup.py pyproject.toml

# Or edit manually in your text editor
```

### 2. Add More Details to GitHub

1. Go to `https://github.com/YOUR_USERNAME/coach-everything`
2. Click "Edit" (pencil icon) next to repository description
3. Add:
   - **Description**: "Universal Task Breakdown & AI Coaching Agent"
   - **Website**: (optional)
   - **Topics**: Add tags like:
     - `task-breakdown`
     - `adhd`
     - `productivity`
     - `ai-coaching`
     - `learning`
     - `obsidian`

### 3. Enable GitHub Pages (Optional - for hosting docs)

1. Go to Settings → Pages
2. Under "Source": select "Deploy from a branch"
3. Select: main branch, /docs folder
4. Click Save

Your docs will be at: `https://YOUR_USERNAME.github.io/coach-everything/`

### 4. Add Topics to GitHub

1. Go to Settings
2. Scroll to "Topics" section
3. Add relevant tags:
   ```
   python cli ai task-management adhd productivity obsidian
   ```

### 5. Set Up GitHub Actions (CI/CD)

The `.github/workflows/` files are already included. They'll automatically:
- Run tests on every push
- Check code quality (linting, type checking)
- Report coverage

No additional setup needed!

### 6. (Optional) Release Your First Version

```bash
# Create a release tag
git tag v1.0.0
git push origin v1.0.0

# Or do it on GitHub:
# Go to Releases → Draft a new release
# Tag: v1.0.0
# Title: Coach Everything v1.0.0
# Description: [copy from CHANGELOG if you have one]
# Publish release
```

### 7. (Optional) Push to PyPI

To allow `pip install coach-everything`:

```bash
# Install build tools
pip install build twine

# Build distribution
python -m build

# Upload to PyPI (requires account)
twine upload dist/*
```

## Verify Everything Works

```bash
# Clone your newly published repo
cd /tmp
git clone https://github.com/YOUR_USERNAME/coach-everything.git
cd coach-everything

# Install and test
pip install -e .
coach --version
coach init
```

## Update Your Git Configuration

Edit `.github/workflows/tests.yml` if you want to customize CI/CD:

```yaml
# Change notification emails
# Modify Python versions to test
# Add more checks
```

## Future Pushes

After the initial setup, push changes normally:

```bash
cd coach-everything

# Make changes
git add .
git commit -m "fix: resolve timeout in search engine"

# Push
git push
```

## Best Practices Going Forward

### Commit Messages

Follow conventional commits:
```
feat: add Discord server search
fix: handle timeout in search_engine
docs: clarify three-stage roadmap
test: add tests for task atomizer
```

### Branching

```bash
# For features
git checkout -b feature/new-platform

# For fixes
git checkout -b fix/search-timeout

# Make changes, commit, push
git push -u origin feature/new-platform

# Open Pull Request on GitHub
```

### Regular Updates

```bash
# Update dependencies
pip list --outdated
pip install --upgrade [packages]

# Commit updates
git add requirements.txt
git commit -m "chore: update dependencies"
git push
```

## Troubleshooting

### "fatal: 'origin' does not appear to be a 'git' repository"

```bash
# You need to be in the project directory
cd /tmp/coach-everything

# Then try again
git push -u origin main
```

### "Permission denied (publickey)"

You need to set up SSH keys:

```bash
# Generate SSH key (macOS/Linux)
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add to GitHub:
# 1. Go to GitHub Settings → SSH and GPG keys
# 2. Click "New SSH key"
# 3. Paste your public key
# 4. Save

# Test
ssh -T git@github.com
```

### "Updates were rejected because the tip of your current branch is behind"

```bash
# Pull latest changes first
git pull origin main

# Then push
git push origin main
```

## What's Included in Your Repository

```
coach-everything/
├── README.md ......................... Full documentation (EN & CN)
├── LICENSE ........................... MIT License
├── .gitignore ........................ Git ignore rules
├── setup.py .......................... Package configuration
├── pyproject.toml .................... Modern Python configuration
├── requirements.txt .................. Dependencies
├── coach/ ............................ Main package
│   ├── __init__.py
│   ├── main.py ....................... CLI entry point
│   ├── agent.py ...................... Core Coach Agent
│   ├── config.py ..................... Configuration management
│   ├── models/ ....................... Data models
│   ├── engines/ ...................... Processing engines
│   ├── feedback/ ..................... Feedback handlers
│   └── storage/ ...................... Data persistence
├── examples/ ......................... Usage examples
├── docs/ ............................. Documentation
│   ├── ARCHITECTURE.md
│   ├── QUICKSTART.md
│   └── INSTALLATION.md
├── tests/ ............................ Test suite (ready to expand)
├── .github/
│   └── workflows/ .................... CI/CD configuration
└── CONTRIBUTING.md ................... Contributing guide
```

## Success Checklist

- [ ] GitHub account created
- [ ] Repository created on GitHub
- [ ] Local repository pushed to GitHub
- [ ] README verified with correct links
- [ ] Topics added
- [ ] GitHub Actions enabled
- [ ] First successful test run
- [ ] Documentation pages viewable
- [ ] (Optional) First release published
- [ ] (Optional) Package published to PyPI

## Next Steps

1. **Announce Your Project**
   - Share on Reddit (r/learnprogramming, r/Python, r/ADHD_Help)
   - Post on ProductHunt
   - Share in Hacker News
   - Tweet with #OpenSource #Python #ADHD

2. **Build Community**
   - Respond to GitHub issues
   - Review pull requests
   - Welcome contributors
   - Celebrate milestones

3. **Keep Growing**
   - Add more features based on feedback
   - Expand documentation
   - Build examples
   - Create video tutorials

---

**Congratulations! Your project is now publicly available! 🎉**

Share it with the world and start building a community of users and contributors.

For questions, check GitHub's official guides:
- [GitHub Quickstart](https://docs.github.com/en/get-started)
- [Creating a Repository](https://docs.github.com/en/get-started/quickstart/create-a-repo)
- [Publishing Packages](https://docs.github.com/en/packages)
