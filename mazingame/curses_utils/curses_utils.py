# -*- coding: utf-8 -*-
#
# The MIT License (MIT)

# Copyright (c) 2015,2018 Sami Salkosuo

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

#some curses util functions
from ..globals import *
import curses

def infoWindow(stdscr,line1=None,line2=None,line3=None,line4=None):
    (cr,cc)=center(stdscr,rows=SCREEN_ROWS,columns=SCREEN_COLUMNS)
    height = 6; width = 36
    lineLen=width-2
    winRow=int(cr-height/2)
    winCol=int(cc-width/2)
    win = curses.newwin(height, width, winRow, winCol)
    if line1 is not None:
        win.addstr(1,1,line1.center(lineLen))
    if line2 is not None:
        win.addstr(2,1,line2.center(lineLen))
    if line3 is not None:
        win.addstr(3,1,line3.center(lineLen))
    if line4 is not None:
        win.addstr(4,1,line4.center(lineLen))

    win.border(0,0,0,0,0,0,0,0)
    win.overlay(stdscr)
    stdscr.refresh()
    waitForWindowClose(win)

def center(win,rows=None,columns=None):
    '''Return center point of Curses window.'''
    (_rows,_columns)=win.getmaxyx()
    if rows is not None:
        _rows=rows
    if columns is not None:
        _columns=columns

    return (_rows/2,_columns/2)


def waitForWindowClose(window,seconds=None):
    
    if seconds is not None:
        time.sleep(seconds)
    else:
        #wait for keypress in given window
        #while 1:
            c = window.getch()
        #    if c == ord('c'):
        #        break  # Exit the while()
    window.erase()
    del window
