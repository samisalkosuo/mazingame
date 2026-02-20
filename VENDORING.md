# Vendoring mazepy

## What Was Done

The `mazepy` package has been vendored (incorporated directly) into the mazingame repository to eliminate the external dependency.

## Changes Made

### 1. Created `mazingame/mazepy/` Directory
- Copied `mazepy.py` from https://github.com/samisalkosuo/mazepy
- Created `__init__.py` to expose the module

### 2. Updated Imports
Changed all imports from:
```python
from mazepy import mazepy
```

To:
```python
from .mazepy import mazepy
```

Files updated:
- `mazingame/mazingame.py`
- `mazingame/gameclasses.py`
- `mazingame/GameScreen.py`

### 3. Removed External Dependency
- Updated `requirements.txt` - removed `mazepy>=0.3`
- Updated `pyproject.toml` - removed dependency, added `mazingame.mazepy` to packages
- Updated `Dockerfile` - removed pip install step for mazepy

## Why Vendor?

1. **Simplification**: No external dependency to manage
2. **Control**: Full control over the maze generation code
3. **Single Repository**: Everything needed is in one place
4. **Easier Development**: No need to install external packages during development
5. **Stability**: No risk of external package changes breaking the game

## License Compliance

The vendored mazepy code retains its original MIT License:
- Copyright (c) 2016 Sami Salkosuo
- Full license text is preserved in `mazingame/mazepy/mazepy.py`

Both mazingame and mazepy are MIT licensed and by the same author, making vendoring straightforward.

## Original Source

- Repository: https://github.com/samisalkosuo/mazepy
- Version: 0.3
- License: MIT

## Future Maintenance

If updates are needed to the maze generation algorithms:
1. Modify `mazingame/mazepy/mazepy.py` directly
2. No need to coordinate with external package
3. Changes are versioned with mazingame

## Testing

The vendored code works identically to the external package:
- All maze algorithms function the same
- Game compatibility maintained
- No breaking changes to the API