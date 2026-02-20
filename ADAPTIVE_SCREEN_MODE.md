# Adaptive Screen Mode Implementation

## Overview

MazinGame now supports **hybrid screen mode** that automatically adapts to available terminal space. The game can run in either full-screen mode (when terminal is large enough) or scrolling mode (for smaller terminals).

## Changes Summary

### Previous Behavior
- Required minimum **43 rows × 102 columns** to run
- Rejected smaller terminals with error message
- No flexibility for users with larger fonts or smaller screens

### New Behavior
- **Full-Screen Mode**: Activated when terminal ≥ 43 rows × 102 columns
  - Entire maze visible at once
  - No scrolling needed
  - Original experience preserved

- **Scrolling Mode**: Activated when terminal is 15-42 rows or 40-101 columns
  - Viewport follows player through maze
  - Only portion of maze visible at a time
  - Fully playable with dynamic scrolling

- **Minimum Requirements**: 15 rows × 40 columns
  - Below this, terminal is too small to play effectively

## Technical Implementation

### 1. New Constants (`globals.py`)

```python
MIN_SCROLL_ROWS = 15   # Minimum rows for scrolling mode
MIN_SCROLL_COLS = 40   # Minimum columns for scrolling mode
FULLSCREEN_MIN_ROWS = 43  # Full-screen mode threshold
FULLSCREEN_MIN_COLS = 102 # Full-screen mode threshold
```

### 2. Terminal Size Validation (`mazingame.py`)

- Checks against `MIN_SCROLL_ROWS` and `MIN_SCROLL_COLS` instead of full-screen requirements
- Determines display mode based on available space
- Displays mode information in welcome screen
- Automatically forces scrolling mode for smaller terminals

### 3. Dynamic Screen Dimensions (`GameScreen.py`)

**GameScreen.__init__():**
- Accepts `terminalHeight` and `terminalWidth` parameters
- Calculates dynamic `screenRows` and `screenColumns` based on terminal size
- Stores dimensions as instance variables

**initGame():**
- Uses `self.screenRows` and `self.screenColumns` instead of global constants
- Calculates viewport positioning dynamically

**scroll():**
- Computes maximum scroll positions based on terminal size
- Adapts scrolling behavior to viewport dimensions

**refreshScreen():**
- Uses dynamic dimensions for pad refresh operations
- Handles variable viewport sizes

## Benefits

✅ **Accessibility**: Works with larger fonts and smaller terminals  
✅ **Backward Compatible**: Full-screen mode unchanged when space available  
✅ **User-Friendly**: Automatic mode selection, no configuration needed  
✅ **Flexible**: Adapts to different terminal sizes naturally  
✅ **Maintains Gameplay**: Scrolling preserves all game mechanics

## Usage Examples

### Large Terminal (Full-Screen Mode)
```bash
# Terminal: 50 rows × 120 columns
$ python -m mazingame
# Display mode: full-screen (50x120)
# Entire maze visible at once
```

### Medium Terminal (Scrolling Mode)
```bash
# Terminal: 30 rows × 80 columns
$ python -m mazingame
# Display mode: scrolling (30x80)
# Viewport follows player through maze
```

### Small Terminal (Scrolling Mode)
```bash
# Terminal: 20 rows × 50 columns
$ python -m mazingame
# Display mode: scrolling (20x50)
# Smaller viewport, more scrolling
```

### Too Small Terminal (Rejected)
```bash
# Terminal: 10 rows × 30 columns
$ python -m mazingame
# Error: Console screen is too small: 10 rows. Minimum 15 rows required.
```

## Font Size Considerations

Users with larger fonts can now play the game:

- **Before**: Large font → smaller effective terminal → game rejected
- **After**: Large font → smaller effective terminal → scrolling mode activated

The game automatically adapts to the effective terminal size regardless of font settings.

## Testing

The implementation has been validated for:
- ✅ Syntax correctness (Python compilation)
- ✅ Dynamic dimension calculations
- ✅ Backward compatibility with existing code
- ✅ Proper mode selection logic

## Files Modified

1. **`mazingame/globals.py`**
   - Added `MIN_SCROLL_ROWS` and `MIN_SCROLL_COLS` constants
   - Enhanced documentation for screen dimension constants

2. **`mazingame/mazingame.py`**
   - Updated terminal size validation logic
   - Added display mode determination
   - Enhanced welcome screen with mode information
   - Pass terminal dimensions to GameScreen

3. **`mazingame/GameScreen.py`**
   - Modified `__init__()` to accept terminal dimensions
   - Added dynamic screen dimension calculation
   - Updated `initGame()` to use dynamic dimensions
   - Fixed `scroll()` method for variable viewport sizes
   - Updated `refreshScreen()` to use dynamic dimensions

## Migration Notes

- No breaking changes for existing users
- No configuration changes required
- Existing command-line arguments work as before
- `--nofullscreen` flag still forces scrolling mode regardless of terminal size

## Future Enhancements

Potential improvements for future versions:
- Dynamic maze size adjustment based on terminal dimensions
- Terminal resize detection during gameplay
- Configurable minimum dimensions via command-line arguments
- Visual indicators for scrolling direction availability