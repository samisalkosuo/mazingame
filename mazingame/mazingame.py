# -*- coding: utf-8 -*-
#!/usr/bin/env python
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

#add correct version number here
__version__ = "1.7"

from curses import wrapper
import getpass
import os
import math
import curses
import argparse
import time
import random
import json 

from .globals import *

from mazepy import mazepy
from .curses_utils import curses_utils
from .utils import utils
from .highscores import *
from .gameclasses import Player
from .gameclasses import Goal
from .gameclasses import MazingCell
from .gameclasses import GameGrid
from .GameScreen import GameScreen

#command line args
args=None

def parseCommandLineArgs():
    #parse command line args
    parser = argparse.ArgumentParser(description='MazinGame. A game of maze.')
    parser.add_argument('-l','--level', nargs=1, type=int, metavar='LEVELID',help='Maze level. This integer is a random seed to create the maze.')
    parser.add_argument('-r','--replay', nargs=1, type=int, metavar='GAMEID',help='Play again game with specified id.')
    parser.add_argument('-nf','--nofullscreen', action='store_true', help='Do not use full screen. Default is to show entire maze in terminal, but only if terminal size is larger than the maze.')
    parser.add_argument('--showpath', action='store_true', help='Show shortest path. Remember: this is cheating.')
    parser.add_argument('--showmaze', action='store_true', help='Show entire maze. Remember: this is cheating.')
    parser.add_argument('-hs','--highscores', action='store_true', help='Show high scores. Specify --level to select scores for the level and --showpath to incude cheat scores. Use %s environment variable to set high score file (default is $HOME/%s).' % (MAZINGAME_HIGHSCORE_FILE,DEFAULT_MAZINGAME_HIGHSCORE_FILE))
    parser.add_argument('--cheat', action='store_true', help='Show also cheat highscores.')
    parser.add_argument('-v','--version', action='store_true', help='Show version info.')
    
    global args
    args = parser.parse_args()


def getHelpLine():
    return "Use cursor keys to move and 'q' to quit."


def start(stdscr,textList):
    
    height,width = stdscr.getmaxyx()
    if height < FULLSCREEN_MIN_ROWS:
        input("Console screen is too small: %d rows. Full screen needs minimum of %d rows. CTRL-C to exit." % (height,FULLSCREEN_MIN_ROWS))
        return
    if width < FULLSCREEN_MIN_COLS:
        input("Console screen is too small: %d columns. Full screen needs minimum of %d columns. CTRL-C to exit." % (width,FULLSCREEN_MIN_COLS))
        return

    try:
        cursorVisibility=curses.curs_set(0)
    except:
        cursorVisibility=-1
    # Clear screen
    stdscr.clear()
    #call refresh before anything so that pads work
    #http://stackoverflow.com/a/26305933
    stdscr.refresh()

    replayGameId=None
    if args.replay:
        replayGameId=args.replay[0]


    #show welcome screen
    line1="Welcome to MazinGame!"
    if replayGameId is not None:
        line3="REPLAY: game %d" % replayGameId
    else:
        line3="'X' marks the spot. Go there."
    curses_utils.infoWindow(stdscr,line1=line1,line3=line3)

    stdscr.clear()

    useFullTerminal=True
    if args.nofullscreen:
        useFullTerminal=False
    gameScreen=GameScreen(stdscr,useFullTerminal,args)
    level=None
    if args.level:
        level=args.level[0]

    gameScreen.updateStatusLine("Welcome to Maze. 'X' marks the spot. Go there.")#" %s" % getHelpLine())
    if replayGameId is not None:
        #replay
        #get game level and moves from db
        (level,moves)=getGameMoves(replayGameId)
        gameScreen.replayInProgress=True
        gameScreen.initGame(level)
        player=gameScreen.player
        currentRow=player.row
        currentColumn=player.column
        stdscr.nodelay(1)
        statusMsg="complete"
        for move in moves[1:]:
            direction=None
            toRow=move[0]
            toColumn=move[1]
            if toRow>currentRow:
                direction='down'
            if toRow<currentRow:
                direction='up'
            if toColumn>currentColumn:
                direction='right'
            if toColumn<currentColumn:
                direction='left'

            gameScreen.movePlayer(direction)
            currentRow=toRow
            currentColumn=toColumn
            time.sleep(0.1)
            c = stdscr.getch()
            if c == ord('q'):
                statusMsg="aborted"
                break
        textList.append("Replay of game %d %s." % (replayGameId,statusMsg))
    else:
        gameScreen.initGame(level)
        while 1:
            if gameScreen.gameover==False:
                c = stdscr.getch()
            else:
                break
            if c == ord('h'):
                gameScreen.updateStatusLine(getHelpLine())
            elif c == curses.KEY_UP or c== ord('w'):
                gameScreen.movePlayer('up')
            elif c == curses.KEY_DOWN or c== ord('s'):
                gameScreen.movePlayer('down')
            elif c == curses.KEY_LEFT or c== ord('a'):
                gameScreen.movePlayer('left')
            elif c == curses.KEY_RIGHT or c== ord('d'):
                gameScreen.movePlayer('right')
            elif c== ord('i'):
                #info
                player=gameScreen.player
                #gameScreen.gamepad.cursyncup()
                (screenRow,screenColumn)=gameScreen.gamepad.getyx()
                #gameScreen.updateStatusLine("%s screen: (%d,%d) pad corner: (%d,%d)" % (player.__str__(),screenRow,screenColumn,gameScreen.padCornerRow,gameScreen.padCornerColumn))
                gameScreen.updateStatusLine("%s" % (player))
            elif c== ord('I'):
                player=gameScreen.player
                (screenRow,screenColumn)=stdscr.getyx()
                gameScreen.updateStatusLine("%s screen: (%d,%d) pad corner: (%d,%d)" % (player.__str__(),screenRow,screenColumn,gameScreen.padCornerRow,gameScreen.padCornerColumn))
                #gameScreen.updateStatusLine("Screen row,col: (%d,%d)" % (screenRow,screenColumn))
            elif c== ord('T'):
                #stdscr.deleteln()
                #stdscr.insdelln(2)
                infoWindow(stdscr,line1="This is line1",line2="line 2",line3="Then line 3",line4="and line4")
                gameScreen.updateStatusLine("Test: %d" % random.randint(1,99999))
            elif c == ord('q'):
                #utils.debug(time.mktime(time.gmtime()))            
                break  # Exit the while()

    if cursorVisibility>-1:
        curses.curs_set(cursorVisibility)

    if not (replayGameId is not None):
        if gameScreen.gameover==True:
            cheat=False
            if args.showpath or args.showmaze:
                cheat=True
            gameid=saveScores(args,__version__,gameScreen.grid,gameScreen.player,gameScreen.goal,gameScreen.level,gameScreen.score,gameScreen.totalMoves,gameScreen.shortestPathLength,gameScreen.elapsed,cheat,gameScreen.grid.algorithm_key)
            textList.append("'X' reached:")
            if gameid == -1:
                textList.append("  Game ID  : %d (score not saved, MazinGame is meant to be run as Docker image)" % gameid)            
            else:
                textList.append("  Game ID  : %d" % gameid)
            textList.append("  Level    : %d" % gameScreen.level)
            textList.append("  Algorithm: %s" % gameScreen.grid.algorithm)
            #textList.append("  Braiding : %f" % args.braid)
            textList.append("  Moves    : %d/%d" % (gameScreen.totalMoves,gameScreen.shortestPathLength))
            textList.append("  Elapsed  : %.03fsecs" % gameScreen.elapsed)
            textList.append("  Score    : %d" % gameScreen.score)
            if args.showpath:
                textList.append("  --showpath cheat was active.")
            if args.showmaze:
                textList.append("  --showmaze cheat was active.")
        else:
            textList.append("'X' not reached.")
            #textList.append("  Level  : %d" % gameScreen.level)



def main():
    try:
        parseCommandLineArgs()
        if args.highscores:
            listHighScores(args)
            return
        if args.version:
            print("%s v%s" % (NAME,__version__))
            print("")
            print("\n".join(DESCRIPTION))
            print("")
            print(COPYRIGHT)
            print(LICENSE)
            return
        if args.replay:
            replayGameId=args.replay[0]
            mazeInfo=getMazeInfo(replayGameId)
            if mazeInfo is None:
                print("Can not replay game. No game info.")
                return
        
        textList=[]
        wrapper(start,textList)
        if textList:
            print("\n".join(textList))        
    except KeyboardInterrupt:
        #ignore ctrl-c
        pass

if __name__ == "__main__": 
    main()
