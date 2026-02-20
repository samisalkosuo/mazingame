# MazinGame

[![CI](https://github.com/samisalkosuo/mazingame/workflows/CI/badge.svg)](https://github.com/samisalkosuo/mazingame/actions)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A game of maze.

Idea of the game is to find a path through the maze to a location marked by 'X'.

Snapshot from an actual game (if you are seeing this in pypi.python.org you may 
not see it correctly, so go to GitHub page to see it)::

	+   +   +   +   +   +   +   +   +---+   +---+---+---+   +   +   +   +---+   +---+
	|   |   |   |   |   |   |   |       |                       |           |   |
	+   +   +---+   +   +   +   +---+   +---+---+   +---+---+   +---+   +   +   +   +
	|   |     X |   |   |   |       |   |       |       |       |       |   |
	+---+---+   +   +   +   +---+   +   +---+   +---+   +   +---+   +---+   +   +---+
	| .   .   @ |       |       |   |       |   |       |       |   |       |       |
	+   +---+---+---+   +   +   +   +---+   +   +   +---+   +---+   +   +   +---+   +
	| .             |       |   |       |   |       |               |           |   |
	+   +---+   +   +---+---+   +   +   +   +---+---+   +---+---+   +---+---+   +   +
	| .   . |   |               |   |       |       |           |   |           |
	+---+   +   +---+---+---+---+   +---+---+   +   +---+---+   +   +   +---+---+---+
	| .   . |           |       |   |       |   |   |           |       |
	+   +---+---+   +   +   +   +   +   +---+   +   +   +---+---+   +---+   +   +---+
	| . |           |       |   |   |   |       |   |   |       |           |
	+   +   +---+---+---+   +   +   +   +   +---+   +   +---+   +---+---+   +---+   +
	| . |       |       |   |   |   |   |   |       |               |       |       |
	+   +---+   +   +   +   +   +   +   +   +   +---+---+---+---+---+   +---+   +---+
	| .   .   . |   |   |       |       |   |           |       |       |           |
	+---+---+   +   +   +---+   +   +---+   +---+---+   +   +   +   +---+   +   +   +
	| .   . | . |   |       |   |           |   |       |   |       |   |       |
	+   +   +   +---+---+   +   +---+---+   +   +   +   +   +---+---+   +---+---+---+
	| . | . | .   .   . |       |           |           |           |   |           |
	+   +   +---+---+   +---+---+   +---+---+   +---+---+   +---+   +   +   +---+   +
	P: (9,2) X: (8,2) Moves: 35/36 Elapsed: 12.670secs Score: 8288

## Requirements

### Docker (Recommended)
[Docker runtime](https://www.docker.com/get-docker) - Makes distribution simple and life easier!

### From Source
- **Python 3.9 or higher** (3.9, 3.10, 3.11, 3.12 supported)
- curses library (included in most Unix/Linux Python installations)
- [mazepy](https://github.com/samisalkosuo/mazepy) (vendored in this project)

**Note**: Does not work with Python 2. On Windows, requires WSL (Windows Subsystem for Linux) or Cygwin.

## 🌐 NEW: Play in Your Browser!

**Mazingame is now available as a web application!** Play directly in your browser without any installation.

### Quick Start - Web Version

```bash
# Using the quick start script (Linux/Mac)
./scripts/start_web.sh

# Or using PowerShell (Windows)
.\scripts\start_web.ps1

# Or manually with docker-compose
docker-compose up -d
```

Then open your browser and navigate to: **http://localhost:5000**

**Features:**
- 🎮 Play directly in browser - no installation needed
- 👥 Multiple concurrent users supported
- 📊 Shared high scores
- 🔄 Automatic session management
- 🐳 Easy Docker deployment

See [WEB_DEPLOYMENT_README.md](WEB_DEPLOYMENT_README.md) for detailed web deployment documentation.

## Install and usage - Docker

Install from Dockerhub:

- docker pull kazhar/mazingame

Using docker image:

- Run using command:
  - *docker run -it --rm kazhar/mazingame [options]*

- Set your own directory for highscore/game replay file:
  - *docker run -it --rm -v &lt;path_to_local_dir>:/data kazhar/mazingame [options]*

About options:

- *-it* runs Docker container with interactive terminal.
- *--rm* removes image after use. No need to keep it.
- *-v* maps local directory to directory used by the program.

## Install and usage - pip

Install from PyPI:

```bash
pip install mazingame
```

**Note**: PyPI version may not be as up-to-date as the Docker image or GitHub repository.

## Development Setup

For contributing or local development:

```bash
# Clone the repository
git clone https://github.com/samisalkosuo/mazingame.git
cd mazingame

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run the game
python -m mazingame
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

## Instructions

You will start at some location in the bottom of the maze. 'X' is somewhere
nearer the top of the maze.

- Move using cursor keys or 'w', 'a', 's', 'd'.
- Quit pressing 'q' or Ctrl-C.

When, or if, you reach 'X', the ending score is saved to SQLite database */data/mazingame_highscores.sqlite*.
Use Docker volume to point */data* to your own directory.

Command line options include:

- -f, --fullscreen      Use terminal to show entire maze. But only if terminal size is larger than the maze.
- --showpath            Show shortest path. Remember: this is cheating.
- --showmaze            Show entire maze. Remember: this is cheating.
- -hs, --highscores     Show high scores.

And a few more.

Note: database in high score file may change from version to version, if you
get SQLite error when saving high scores, delete your high score file.

## Features

- 🎮 Multiple maze generation algorithms (Binary Tree, Recursive Backtracker, Aldous-Broder, Wilson, Hunt and Kill, Sidewinder)
- 📊 High score tracking with SQLite database
- 🎬 Game replay functionality
- 🖥️ Adaptive screen modes (full-screen and scrolling)
- 🐳 Docker support for easy deployment
- 🔍 Optional cheats (show path, show maze)
- ⌨️ Keyboard controls (arrow keys or WASD)

## About

This hobby project was inspired by the book ["Mazes for Programmers" by Jamis Buck](https://pragprog.com/book/jbmaze/mazes-for-programmers).

Python translations of the maze code is in [mazepy-project](https://github.com/samisalkosuo/mazepy).

See [http://sami.salkosuo.net/mazingame/](http://sami.salkosuo.net/mazingame/) for some background about MazinGame.

## Modernization

This project has been modernized to use:
- Python 3.9+ with type hints
- Modern packaging with `pyproject.toml`
- Comprehensive logging
- Automated testing and CI/CD
- Code quality tools (black, ruff, mypy)

See [MODERNIZATION.md](MODERNIZATION.md) for details on all improvements.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
