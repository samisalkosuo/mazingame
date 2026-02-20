# Contributing to MazinGame

Thank you for your interest in contributing to MazinGame! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project follows a simple code of conduct:
- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment for all contributors

## Getting Started

### Prerequisites

- Python 3.9 or higher (3.9, 3.10, 3.11, 3.12 supported)
- Git
- Docker (optional, for testing Docker builds)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/mazingame.git
   cd mazingame
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/samisalkosuo/mazingame.git
   ```

## Development Setup

1. **Create a virtual environment:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install development dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```
   This will automatically run code quality checks before each commit.

4. **Verify setup:**
   ```bash
   pytest
   python -m mazingame --version
   ```

## Development Workflow

### Creating a Branch

Create a feature branch for your work:
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### Making Changes

1. Make your changes in your feature branch
2. Write or update tests as needed
3. Update documentation if necessary
4. Ensure all tests pass
5. Commit your changes with clear, descriptive messages

### Commit Messages

Follow these guidelines for commit messages:
- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests when relevant

Examples:
```
Add support for custom maze sizes

Fix cursor visibility issue on Windows
Closes #123

Update documentation for new features
```

## Coding Standards

### Python Style

This project follows PEP 8 and uses automated tools to enforce style:

- **Black**: Code formatting (line length: 100)
- **isort**: Import sorting
- **Ruff**: Fast linting
- **mypy**: Type checking

These tools run automatically via pre-commit hooks, but you can also run them manually:

```bash
# Format code
black mazingame tests

# Sort imports
isort mazingame tests

# Lint code
ruff check mazingame tests

# Type check
mypy mazingame
```

### Type Hints

- Add type hints to all new functions and methods
- Use `typing` module for complex types
- Follow existing patterns in the codebase

Example:
```python
from typing import Optional, List

def process_maze(rows: int, columns: int, seed: Optional[int] = None) -> List[str]:
    """Process maze with given dimensions."""
    # Implementation
    pass
```

### Docstrings

Use Google-style docstrings for all public functions, classes, and methods:

```python
def calculate_score(moves: int, time_elapsed: float, optimal_moves: int) -> int:
    """Calculate the game score based on performance.
    
    Args:
        moves: Number of moves taken by the player
        time_elapsed: Time taken in seconds
        optimal_moves: Minimum number of moves possible
        
    Returns:
        The calculated score as an integer
        
    Raises:
        ValueError: If moves or optimal_moves is negative
    """
    # Implementation
    pass
```

### Logging

Use the logging module instead of print statements:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Game started")
logger.debug(f"Maze size: {rows}x{columns}")
logger.error(f"Failed to load game: {error}")
```

### Exception Handling

- Use specific exception types
- Always log exceptions
- Provide context in error messages

```python
try:
    result = process_data(data)
except ValueError as e:
    logger.error(f"Invalid data format: {e}")
    raise
except Exception as e:
    logger.exception(f"Unexpected error processing data: {e}")
    raise
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mazingame --cov-report=html

# Run specific test file
pytest tests/test_basic.py

# Run with verbose output
pytest -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names
- Test both success and failure cases

Example:
```python
def test_maze_generation_with_valid_seed():
    """Test that maze generation works with a valid seed."""
    grid = GameGrid(10, 10, MazingCell)
    maze = initMaze(grid, "BT")
    assert maze is not None
    assert maze.rows == 10
    assert maze.columns == 10
```

## Submitting Changes

### Before Submitting

1. **Update your branch:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all checks:**
   ```bash
   pytest
   black --check mazingame tests
   ruff check mazingame tests
   mypy mazingame
   ```

3. **Update documentation** if you've changed functionality

### Creating a Pull Request

1. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Go to the GitHub repository and create a Pull Request

3. Fill in the PR template with:
   - Clear description of changes
   - Related issue numbers
   - Testing performed
   - Screenshots (if UI changes)

4. Wait for review and address any feedback

### Pull Request Guidelines

- Keep PRs focused on a single feature or fix
- Include tests for new functionality
- Update documentation as needed
- Ensure CI passes
- Respond to review comments promptly

## Reporting Issues

### Bug Reports

When reporting bugs, include:
- Python version
- Operating system
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages or logs
- Screenshots if applicable

### Feature Requests

When requesting features, include:
- Clear description of the feature
- Use cases and benefits
- Possible implementation approach
- Willingness to contribute

### Security Issues

For security vulnerabilities, please email the maintainer directly rather than opening a public issue.

## Development Tips

### Running the Game Locally

```bash
# Run from source
python -m mazingame

# With options
python -m mazingame --level 12345
python -m mazingame --showpath
python -m mazingame --highscores
```

### Building Docker Image

```bash
# Build
docker build -t mazingame:dev .

# Run
docker run -it --rm mazingame:dev
```

### Debugging

- Use logging instead of print statements
- Set log level to DEBUG for detailed output
- Use Python debugger (pdb) when needed:
  ```python
  import pdb; pdb.set_trace()
  ```

## Questions?

If you have questions:
- Check existing issues and discussions
- Open a new issue with the "question" label
- Reach out to maintainers

## License

By contributing to MazinGame, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to MazinGame! 🎮