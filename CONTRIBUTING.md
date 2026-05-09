# Contributing to Coach Everything

Thank you for your interest in contributing! We welcome contributions from everyone.

## Getting Started

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/coach-everything.git
cd coach-everything

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=coach

# Run specific test
pytest tests/test_search_engine.py
```

### Code Quality

```bash
# Format code
black coach/ tests/ examples/

# Check linting
flake8 coach/ tests/

# Type checking
mypy coach/

# Sort imports
isort coach/ tests/
```

## What to Contribute

### 🔍 Areas We Need Help

1. **Additional Search Platforms**
   - Discord servers for specific communities
   - Specialized forums (physics.stackexchange.com, etc.)
   - More niche platforms

2. **Task Templates**
   - New domains (music, art, writing, sports, etc.)
   - More detailed templates for existing domains
   - Regional variations

3. **Verification Criteria**
   - Better templates for different task types
   - Command-based verification for coding tasks
   - Assessment frameworks

4. **Integration**
   - Support for other note-taking apps (Notion, Roam, etc.)
   - Mobile progress tracking
   - Slack integration for updates

5. **Coach Agent**
   - Better personality modes
   - More sophisticated help suggestions
   - Learning from user patterns

6. **Documentation**
   - More usage examples
   - Video tutorials
   - FAQ expansion

7. **Tests**
   - Increase test coverage
   - Integration tests
   - E2E tests

## How to Contribute

### 1. Fork & Branch

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/coach-everything.git
cd coach-everything
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Follow our code style:
- **Python**: PEP 8, formatted with Black
- **Docstrings**: Google style
- **Type hints**: Use throughout new code
- **Tests**: Write tests for new features

### 3. Commit Messages

```
Format: <type>: <subject>

Examples:
- feat: add Discord server search
- fix: handle timeout in search_engine
- docs: clarify three-stage roadmap
- test: add tests for task atomizer
```

Types:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `test` - Tests
- `refactor` - Code refactoring
- `perf` - Performance improvement
- `chore` - Build/dependency changes

### 4. Pull Request

1. Push to your fork
2. Open PR on GitHub with:
   - Clear title and description
   - Reference any related issues (#123)
   - Screenshots if UI changes
   - Test results

3. Address review feedback
4. Merge when approved

## Code Style Guidelines

### Python Style

```python
# Type hints
from typing import List, Optional, Dict

def process_results(
    results: List[SearchResult],
    max_items: int = 10,
    filter_by: Optional[str] = None,
) -> Dict[str, Any]:
    """Process search results with filtering.
    
    Args:
        results: Search results to process
        max_items: Maximum items to return
        filter_by: Optional filter criteria
        
    Returns:
        Dictionary with processed results
    """
    return {}

# Classes
class MyClass:
    """Short description.
    
    Longer description if needed.
    """
    
    def __init__(self, name: str):
        self.name = name
    
    def method(self) -> str:
        """Describe what this does."""
        return self.name
```

### Naming Conventions

```python
# Constants
MAX_RESULTS = 100
DEFAULT_TIMEOUT = 30

# Private methods/attributes (single underscore)
def _internal_method(self):
    pass

# Classes use CamelCase
class SearchEngine:
    pass

# Functions/methods use snake_case
def process_results():
    pass

# Variables use snake_case
search_query = "python"
```

### Documentation

Every public function should have:
- Short one-line description
- Args section (if parameters)
- Returns section (if returns something)
- Raises section (if can raise exceptions)
- Examples (for complex functions)

```python
def search_papers(
    query: str,
    max_results: int = 10,
) -> List[AcademicPaper]:
    """Search for academic papers on arXiv.
    
    Uses arXiv API to find papers matching the query,
    sorted by submission date (newest first).
    
    Args:
        query: Search query (e.g., "machine learning")
        max_results: Maximum papers to return (max 100)
        
    Returns:
        List of AcademicPaper objects with metadata
        
    Raises:
        ValueError: If query is empty
        TimeoutError: If API request times out
        
    Example:
        >>> papers = search_papers("neural networks", max_results=5)
        >>> print(f"Found {len(papers)} papers")
    """
```

## Adding New Search Platforms

### Steps

1. Implement search method in `SearchEngine`
2. Add to `self.platforms` dict
3. Create test file
4. Update documentation

### Example

```python
# In coach/engines/search_engine.py

def _search_discourse_forums(
    self,
    query: str,
    max_results: int = 10,
) -> List[SearchResult]:
    """Search Discourse-based forums"""
    results = []
    
    discourse_forums = [
        "https://forum1.com",
        "https://forum2.com",
    ]
    
    for forum_url in discourse_forums:
        try:
            # API call
            response = requests.get(
                f"{forum_url}/search.json",
                params={"q": query},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                for topic in data.get("topics", []):
                    results.append(SearchResult(
                        title=topic["title"],
                        url=f"{forum_url}/t/{topic['id']}",
                        source="discourse",
                        summary=topic.get("excerpt", ""),
                        upvotes=topic.get("like_count", 0),
                    ))
        except Exception as e:
            logger.warning(f"Error searching {forum_url}: {str(e)}")
    
    return results
```

## Adding New Task Domains

### Steps

1. Add domain to `TaskAtomizer._generate_phases_for_domain`
2. Add workspace template
3. Add example usage
4. Document the domain

### Example

```python
# In coach/engines/task_atomizer.py

domain_phases = {
    # ... existing domains ...
    "music_learning": [
        "Get familiar with instrument",
        "Learn music theory basics",
        "Practice fundamental techniques",
        "Play simple songs",
        "Progressive difficulty increase",
    ],
}

# In coach/models/workspace.py

WORKSPACE_TEMPLATES = {
    # ... existing templates ...
    "music": {
        "structure": {
            "📋 Learning Plan.md": "Your music learning roadmap",
            "📚 Resources/": "Sheet music, tutorials, links",
            "🎵 Practice/": "Practice sessions and recordings",
            "📝 Progress/": "What you've learned",
        }
    },
}
```

## Testing

### Test Structure

```python
# tests/test_my_feature.py
import pytest
from coach.engines.search_engine import SearchEngine

class TestSearchEngine:
    """Tests for SearchEngine"""
    
    def setup_method(self):
        """Setup before each test"""
        self.engine = SearchEngine()
    
    def test_search_returns_results(self):
        """Test that search returns non-empty list"""
        results = self.engine.search("python")
        assert len(results) > 0
    
    def test_search_results_have_required_fields(self):
        """Test that results have all required fields"""
        results = self.engine.search("python", max_results=1)
        result = results[0]
        
        assert result.title
        assert result.url
        assert result.source
        assert hasattr(result, 'relevance_score')
    
    def test_search_with_max_results(self):
        """Test max_results parameter"""
        results = self.engine.search("python", max_results=5)
        assert len(results) <= 5
    
    @pytest.mark.slow
    def test_search_multiple_platforms(self):
        """Test searching multiple platforms (slow)"""
        results = self.engine.search(
            "python",
            platforms=["reddit", "github", "blogs"],
            max_results=30
        )
        
        # Should have results from different platforms
        sources = {r.source for r in results}
        assert len(sources) > 1
```

### Running Tests

```bash
# Run specific test
pytest tests/test_my_feature.py::TestSearchEngine::test_search_returns_results

# Run with print output
pytest -s tests/

# Run fast tests only (exclude slow)
pytest -m "not slow"

# Run with coverage
pytest --cov=coach --cov-report=html
```

## Reporting Issues

### Bug Reports

Include:
- Python version
- OS
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs
- Coach version

### Feature Requests

Include:
- Use case description
- Proposed solution (if you have one)
- Alternative approaches
- Why it's important

## Documentation

### Writing Docs

- Use clear, conversational language
- Include examples
- Keep it up-to-date with code
- Link to related docs

### Doc Style

```markdown
# Feature Name

Brief description (1 paragraph)

## How It Works

Explain the concept

## Usage

```python
# Code examples
```

## Configuration

Parameters and options

## Examples

Real-world examples

## See Also

Links to related content
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Open a GitHub discussion or issue. We're happy to help!

---

## Project Maintainers & Contributors

- **Noxinsun** ([@noxinsun-source](https://github.com/noxinsun-source)) - Product vision, design, ADHD expertise
- **Claude Haiku** (Anthropic) - Architecture, implementation, documentation

**Thank you for contributing to Coach Everything! 🎉**
