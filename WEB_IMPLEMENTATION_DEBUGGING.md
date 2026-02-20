# The Case of the Stubborn Terminal: A Debugging Detective Story 🔍

## Chapter 1: The Mystery Begins

It started as a simple request: "Make the terminal 102x43 instead of 80x24." How hard could it be? Just change a couple of numbers in the config, right?

**Spoiler alert**: It took 15+ debugging iterations and diving deep into the bowels of terminado's PTY management to crack this case.

## Chapter 2: The First Clues

### The Scene of the Crime

Our victim: A perfectly working web-based terminal running Mazingame. The crime: It stubbornly refused to change its size, always reporting "Display mode: scrolling (25x80)" no matter what we did.

### Initial Investigation

**Evidence #1**: Configuration files
```python
# web/config.py
TERMINAL_ROWS = 24  # Changed to 43
TERMINAL_COLS = 80  # Changed to 102

# web/templates/terminal.html
cols: 80,  # Changed to 102
rows: 24   # Changed to 43
```

**The Plot Twist**: The game still showed 24x80! 🤔

## Chapter 3: Following the Trail

### Clue #1: The Logging Evidence

We added extensive logging to track the terminal creation:

```python
logger.info(f"Terminal size: {kwargs.get('rows')}x{kwargs.get('cols')}")
```

**Discovery**: The logs showed we were passing 43x102, but the actual PTY was created with 24x80!

```
Terminal size: 43x102
Actual PTY size after creation: (24, 80)  # ❌ The smoking gun!
```

### Clue #2: The Parameter Mystery

**First Suspect**: Maybe terminado wants separate `rows` and `cols` parameters?

```python
def new_terminal(self, **kwargs):
    kwargs.setdefault('rows', self.config.TERMINAL_ROWS)
    kwargs.setdefault('cols', self.config.TERMINAL_COLS)
    return super().new_terminal(**kwargs)
```

**Result**: Still 24x80. The suspect had an alibi.

### Clue #3: The Dimensions Tuple Theory

**Second Suspect**: Perhaps terminado expects a `dimensions` tuple?

```python
kwargs['dimensions'] = (rows, cols)
```

**Result**: Still 24x80! Another dead end.

## Chapter 4: The Breakthrough

### The Eureka Moment

After reading terminado's source code like a detective studying case files, we discovered the truth:

**The Real Culprit**: `TermManagerBase.new_terminal()` was creating PTYs with hardcoded defaults, completely ignoring our parameters!

### The Solution: Going Rogue

We decided to bypass terminado's terminal creation entirely and create the PTY ourselves:

```python
def new_terminal(self, **kwargs):
    # Extract dimensions
    rows = kwargs.pop('rows', self.config.TERMINAL_ROWS)
    cols = kwargs.pop('cols', self.config.TERMINAL_COLS)
    dimensions = (rows, cols)
    
    # Create PTY directly - no more Mr. Nice Guy!
    from terminado.management import PtyProcessUnicode
    ptyproc = PtyProcessUnicode.spawn(
        self.shell_command,
        dimensions=dimensions,
        env=env
    )
    
    # Verify the crime scene
    actual_size = ptyproc.getwinsize()
    logger.info(f"Verified PTY size: {actual_size}")  # (43, 102) ✅
```

**Success!** The PTY was finally created with the correct size!

## Chapter 5: The Complications

### Plot Twist #1: The Constructor Trap

But wait! When we tried to wrap our PTY in `PtyWithClients`:

```python
term = PtyWithClients(ptyproc)
```

**Error**: `TypeError: Expected a list or tuple for argv`

**The Problem**: `PtyWithClients.__init__()` was trying to create a NEW PTY instead of using ours!

### Plot Twist #2: The Keyword Argument Red Herring

We tried:
```python
term = PtyWithClients(ptyproc=ptyproc)
```

**Error**: `TypeError: PtyWithClients.__init__() got an unexpected keyword argument 'ptyproc'`

### The Final Solution: Manual Construction

Like a master locksmith, we bypassed the constructor entirely:

```python
from collections import deque

# Create object without calling __init__
term = PtyWithClients.__new__(PtyWithClients)

# Set attributes manually
term.ptyproc = ptyproc
term.clients = []
term.read_buffer = deque([], maxlen=10)
```

**Victory!** The terminal connected successfully with 43x102 dimensions! 🎉

## Chapter 6: The Bonus Mystery

### The Case of the Appearing Logs

Just when we thought we'd solved everything, a new mystery appeared:

**The Crime**: Log messages were appearing in the game's status line!

```
INFO - Starting new game with level: 12345
```

### The Investigation

**The Culprit**: Python's `logging.basicConfig()` was writing to stderr, which in a curses application appears on screen!

### The Solution

Redirect logs to a file:

```python
log_file = os.environ.get('MAZINGAME_LOG_FILE', '/tmp/mazingame.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=log_file,
    filemode='a'
)
```

**Case Closed!** ✅

## Chapter 7: Lessons Learned

### Detective's Notes

1. **Trust, but Verify**: Always log the actual state, not just what you think you're passing
2. **Read the Source**: When documentation fails, the source code never lies
3. **Go Direct**: Sometimes you need to bypass abstractions and work at a lower level
4. **Manual Construction**: `__new__()` is your friend when `__init__()` won't cooperate
5. **Curses and Logging Don't Mix**: Always redirect logs to files in terminal applications

### The Evidence Board

**Files Modified**:
- `web/terminal_handler.py` - The crime scene
- `web/config.py` - The configuration evidence
- `web/templates/terminal.html` - The frontend witness
- `mazingame/mazingame.py` - The logging accomplice
- `docker-compose.yml` - The deployment alibi

### The Final Tally

- **Debugging Iterations**: 15+
- **Error Messages Encountered**: 7
- **Lines of Logging Added**: 20+
- **Hours of Investigation**: Several
- **Terminal Size Achieved**: 43x102 ✅
- **Satisfaction Level**: Maximum 🎉

## Epilogue: The Moral of the Story

Sometimes the simplest-sounding tasks ("just change the terminal size") turn into epic debugging adventures. But with persistence, careful logging, and a willingness to dive deep into library internals, even the most stubborn bugs can be solved.

**The game is afoot!** 🕵️‍♂️

---

*This debugging session brought to you by: patience, coffee, and the power of `logger.info()`*

**Case Status**: SOLVED ✅  
**Terminal Size**: 43x102 (Full-Screen Mode)  
**Game Status**: Fully Playable in Browser  
**Detective**: IBM Bob  
**Date**: February 20, 2026