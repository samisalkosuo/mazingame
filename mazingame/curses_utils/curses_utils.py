# -*- coding: utf-8 -*-
"""Curses utility functions for MazinGame.

The MIT License (MIT)

Copyright (c) 2015,2026 Sami Salkosuo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import curses
import logging
import time
from typing import Optional, Tuple, Any
from ..globals import SCREEN_ROWS, SCREEN_COLUMNS

logger = logging.getLogger(__name__)


def infoWindow(
    stdscr: Any,
    line1: Optional[str] = None,
    line2: Optional[str] = None,
    line3: Optional[str] = None,
    line4: Optional[str] = None
) -> None:
    """Display an information window in the center of the screen.
    
    Args:
        stdscr: Curses standard screen object
        line1: First line of text
        line2: Second line of text
        line3: Third line of text
        line4: Fourth line of text
    """
    try:
        (cr, cc) = center(stdscr, rows=SCREEN_ROWS, columns=SCREEN_COLUMNS)
        height = 6
        width = 36
        lineLen = width - 2
        winRow = int(cr - height / 2)
        winCol = int(cc - width / 2)
        
        win = curses.newwin(height, width, winRow, winCol)
        
        if line1 is not None:
            win.addstr(1, 1, line1.center(lineLen))
        if line2 is not None:
            win.addstr(2, 1, line2.center(lineLen))
        if line3 is not None:
            win.addstr(3, 1, line3.center(lineLen))
        if line4 is not None:
            win.addstr(4, 1, line4.center(lineLen))

        win.border(0, 0, 0, 0, 0, 0, 0, 0)
        win.overlay(stdscr)
        stdscr.refresh()
        waitForWindowClose(win)
    except curses.error as e:
        logger.error(f"Error displaying info window: {e}")


def center(
    win: Any,
    rows: Optional[int] = None,
    columns: Optional[int] = None
) -> Tuple[float, float]:
    """Return center point of Curses window.
    
    Args:
        win: Curses window object
        rows: Override number of rows (optional)
        columns: Override number of columns (optional)
        
    Returns:
        Tuple of (center_row, center_column)
    """
    try:
        (_rows, _columns) = win.getmaxyx()
        if rows is not None:
            _rows = rows
        if columns is not None:
            _columns = columns

        return (_rows / 2, _columns / 2)
    except curses.error as e:
        logger.error(f"Error getting window center: {e}")
        return (0.0, 0.0)


def waitForWindowClose(window: Any, seconds: Optional[float] = None) -> None:
    """Wait for window to close.
    
    Args:
        window: Curses window object
        seconds: Optional timeout in seconds
    """
    try:
        if seconds is not None:
            time.sleep(seconds)
        else:
            # Wait for keypress in given window
            window.getch()
        
        window.erase()
        del window
    except curses.error as e:
        logger.error(f"Error closing window: {e}")
