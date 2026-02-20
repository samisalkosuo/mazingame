# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""MazinGame - A game of maze.

The MIT License (MIT)

Copyright (c) 2015,2018 Sami Salkosuo

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

__version__ = "1.7.0"

from curses import wrapper
import curses
import argparse
import time
import random
import logging
from typing import List, Optional, Any

from .globals import (
    NAME, DESCRIPTION, COPYRIGHT, LICENSE,
    MIN_SCROLL_ROWS, MIN_SCROLL_COLS,
    FULLSCREEN_MIN_ROWS, FULLSCREEN_MIN_COLS
)
from .mazepy import mazepy
from .curses_utils import curses_utils
from .utils import utils
from .highscores import getGameMoves, getMazeInfo, saveScores, listHighScores
from .gameclasses import Player, Goal, MazingCell, GameGrid
from .GameScreen import GameScreen

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Command line args (global for compatibility)
args: Optional[argparse.Namespace] = None


def parseCommandLineArgs() -> None:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='MazinGame. A game of maze.')
    parser.add_argument(
        '-l', '--level',
        nargs=1,
        type=int,
        metavar='LEVELID',
        help='Maze level. This integer is a random seed to create the maze.'
    )
    parser.add_argument(
        '-r', '--replay',
        nargs=1,
        type=int,
        metavar='GAMEID',
        help='Replay game with specified id.'
    )
    parser.add_argument(
        '-nf', '--nofullscreen',
        action='store_true',
        help='Do not use full screen. Default is to show entire maze in terminal, '
             'but only if terminal size is larger than the maze.'
    )
    parser.add_argument(
        '--showpath',
        action='store_true',
        help='Show shortest path. Remember: this is cheating.'
    )
    parser.add_argument(
        '--showmaze',
        action='store_true',
        help='Show entire maze. Remember: this is cheating.'
    )
    parser.add_argument(
        '-hs', '--highscores',
        action='store_true',
        help='Show high scores. Specify --level to select scores for the level '
             'and --cheat to include cheat scores.'
    )
    parser.add_argument(
        '--cheat',
        action='store_true',
        help='Show also cheat highscores.'
    )
    parser.add_argument(
        '-v', '--version',
        action='store_true',
        help='Show version info.'
    )
    
    global args
    args = parser.parse_args()
    logger.debug(f"Parsed command line args: {args}")


def getHelpLine() -> str:
    """Get help text for the game.
    
    Returns:
        Help text string
    """
    return "Use cursor keys to move and 'q' to quit."


def start(stdscr: Any, textList: List[str]) -> None:
    """Start the game.
    
    Args:
        stdscr: Curses standard screen object
        textList: List to append result messages to
    """
    
    height,width = stdscr.getmaxyx()
    logger.info(f"Terminal size: {height}x{width}")
    
    # Check minimum dimensions for scrolling mode
    if height < MIN_SCROLL_ROWS:
        error_msg = f"Console screen is too small: {height} rows. Minimum {MIN_SCROLL_ROWS} rows required."
        logger.error(error_msg)
        input(f"{error_msg} CTRL-C to exit.")
        return
    if width < MIN_SCROLL_COLS:
        error_msg = f"Console screen is too small: {width} columns. Minimum {MIN_SCROLL_COLS} columns required."
        logger.error(error_msg)
        input(f"{error_msg} CTRL-C to exit.")
        return

    # Determine display mode based on terminal size
    displayMode = "scrolling"
    if height >= FULLSCREEN_MIN_ROWS and width >= FULLSCREEN_MIN_COLS:
        displayMode = "full-screen"
    logger.info(f"Display mode: {displayMode}")
    
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
    
    # Add display mode information
    line4 = "Display mode: %s (%dx%d)" % (displayMode, height, width)
    curses_utils.infoWindow(stdscr,line1=line1,line3=line3,line4=line4)

    stdscr.clear()

    # Determine if full terminal should be used
    useFullTerminal=True
    if args.nofullscreen:
        useFullTerminal=False
    elif displayMode == "scrolling":
        # Force scrolling mode for smaller terminals
        useFullTerminal=False
    
    # Pass terminal dimensions to GameScreen
    gameScreen=GameScreen(stdscr,useFullTerminal,args,height,width)
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
        logger.info(f"Starting new game with level: {level}")
        gameScreen.initGame(level)
        while 1:
            if gameScreen.gameover==False:
                c = stdscr.getch()
            else:
                logger.info("Game completed successfully")
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



def main() -> None:
    """Main entry point for MazinGame."""
    try:
        parseCommandLineArgs()
        logger.info("MazinGame started")
        
        if args.highscores:
            logger.info("Displaying high scores")
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
            logger.info(f"Replaying game ID: {replayGameId}")
            mazeInfo=getMazeInfo(replayGameId)
            if mazeInfo is None:
                logger.error(f"Cannot replay game {replayGameId}. No game info found.")
                print("Can not replay game. No game info.")
                return
        
        textList=[]
        wrapper(start,textList)
        if textList:
            print("\n".join(textList))
        logger.info("MazinGame ended normally")
            
    except KeyboardInterrupt:
        logger.info("Game interrupted by user (Ctrl-C)")
        # Gracefully handle user interruption
        pass
    except Exception as e:
        logger.exception(f"Unexpected error in main: {e}")
        print(f"An unexpected error occurred: {e}")
        raise

if __name__ == "__main__": 
    main()
