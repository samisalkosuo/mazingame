# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# The MIT License (MIT)

# Copyright (c) 2015,2016 Sami Salkosuo

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
__version__ = "1.1.0"

from curses import wrapper
import getpass
import os
import math
import curses
import argparse
import time
import random

from mazepy import mazepy
from .utils import utils
from .gameclasses import Player
from .gameclasses import Goal
from .gameclasses import MazingCell
from .gameclasses import GameGrid

NAME="MazinGame"
VERSION=__version__
COPYRIGHT="(C) 2015,2016 Sami Salkosuo"
LICENSE="Licensed under The MIT License."
DESCRIPTION=["A game of maze.","Inspired by the book 'Mazes for Programmers' by Jamis Buck","(https://pragprog.com/book/jbmaze/mazes-for-programmers)."]

#environment variable that holds high score file path and name
MAZINGAME_HIGHSCORE_FILE="MAZINGAME_HIGHSCORE_FILE"
#default for high score file
DEFAULT_MAZINGAME_HIGHSCORE_FILE=".mazingame_highscores.sqlite"

#maze
MAZE_ROWS=20
MAZE_COLS=25

#game pad screen
PAD_ROWS=MAZE_ROWS*2+2
PAD_COLS=MAZE_COLS*4+1

#game visible screen
SCREEN_ROWS=24
SCREEN_COLUMNS=80

args=None

#maze algorithms
MAZE_ALGORITHMS=mazepy.MAZE_ALGORITHMS
MAZE_ALGORITHMS_DESC=mazepy.MAZE_ALGORITHMS_DESC

def parseCommandLineArgs():
    #parse command line args
    parser = argparse.ArgumentParser(description='MazinGame. A game of maze.')
    parser.add_argument('-l','--level', nargs=1, type=int, help='Choose level. Any integer.')
    parser.add_argument('-r','--replay', nargs=1, type=int, metavar='GAMEID',help='Replay game with specified id.')
    parser.add_argument('-a','--algorithm', nargs=1, choices=MAZE_ALGORITHMS.keys(),help='Choose maze algorithm: %s. Default is random.' % (",".join(MAZE_ALGORITHMS_DESC)))
    parser.add_argument('-f','--fullscreen', action='store_true', help='Use terminal to show entire maze. But only if terminal size is larger than the maze.')
    parser.add_argument('--showpath', action='store_true', help='Show shortest path. Remember: this is cheating.')
    parser.add_argument('--showmaze', action='store_true', help='Show entire maze. Remember: this is cheating.')
    parser.add_argument('-hs','--highscores', action='store_true', help='Show high scores. Specify --level to select scores for the level and --showpath to incude cheat scores. Use %s environment variable to set high score file (default is $HOME/%s).' % (MAZINGAME_HIGHSCORE_FILE,DEFAULT_MAZINGAME_HIGHSCORE_FILE))
    parser.add_argument('--cheat', action='store_true', help='Show also cheat highscores.')
    parser.add_argument('-v','--version', action='store_true', help='Show version info.')
    
    global args
    
    args = parser.parse_args()

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

def getHelpLine():
    return "Use cursor keys to move and 'q' to quit."

class GameScreen:
    #game screen has status line, visible screen area and full maze area as pad
    def __init__(self,stdscr,useFullTerminal):
        self.stdscr=stdscr
        self.grid=None
        self.player=None
        self.gamepad=None
        self.padCornerRow=0
        self.padCornerColumn=0
        self.goal=None
        self.useFullTerminal=useFullTerminal
        self.startTime=utils.currentTimeMillis()
        self.shortestPathLength=0
        self.shortestPath=None
        self.totalMoves=0
        self.score=0
        self.level=0
        self.gameover=False
        self.elapsed=0.0
        self.replayInProgress=False
        self.algorithm=""

    def initGame(self,level=None):
        
        if level is None:
            #set level
            r=random.random()            
            self.level=(int(1000000000*r))
        else:
            self.level=level
        random.seed(self.level)
        #do it always right after setting random seed, to get same maze when using 
        #same seed
        self.grid=GameGrid(MAZE_ROWS,MAZE_COLS,cellClass=MazingCell)
        self.algorithm=""
        
        if level is None and args.algorithm:
            self.algorithm=args.algorithm[0]
        else:
            self.algorithm=random.choice(list(MAZE_ALGORITHMS.keys()))
        
        self.grid=mazepy.initMaze(self.grid,self.algorithm)
    
        #TODO: add export arg to export maze in some format
        #utils.appendToFile("maze2.txt",self.grid.asciiStr()) 
        #set start time after maze has been initialized
        self.startTime=utils.currentTimeMillis()

        name=getpass.getuser()
        self.player=Player(name)
        playerRow=MAZE_ROWS-1
        #playerColumn=MAZE_COLS-1#random.randint(0,MAZE_COLS-1)
        playerColumn=random.randint(0,MAZE_COLS-1)
        self.player.row=playerRow
        self.player.column=playerColumn
        currentCell=self.grid.getCell(playerRow,playerColumn)
        self.player.addVisitedCell(currentCell)

        goalRow=random.randint(0,MAZE_ROWS/2)
        goalColumn=random.randint(0,MAZE_COLS-1)
        goalScreenRow=goalRow*2+1
        goalScreenColumn=(1+goalColumn)*4-2
        self.goal=Goal(goalRow,goalColumn,goalScreenRow,goalScreenColumn)

        #find solution shortest path
        distances = currentCell.getDistances()
        self.shortestPath=distances.pathTo(self.grid.getCell(goalRow,goalColumn))
        self.shortestPathLength=len(self.shortestPath)-1#does not count starting position
        #utils.debug("Shortest path: %d" % self.shortestPathLength)
        

        (tr,tc)=self.stdscr.getmaxyx()
        #utils.debug("Terminal size: rows %d cols %d" % (tr,tc))
        if self.useFullTerminal==False:
            self.gamepad=curses.newpad(PAD_ROWS,PAD_COLS)
        else:
            if tr>PAD_ROWS and tc>PAD_COLS:
                self.gamepad=self.stdscr
            else:
                self.useFullTerminal=False
                self.gamepad=curses.newpad(PAD_ROWS,PAD_COLS)
        for y in range(0, PAD_ROWS):
            for x in range(0, PAD_COLS):
                try:
                    #if y==goalScreenRow and (x==goalScreenColumn or x==goalScreenColumn+2):
                    if y==goalScreenRow and x==goalScreenColumn:
                        self.gamepad.addch(y,x, ord(self.goal.symbol))
                    else:
                        self.gamepad.addch(y,x, ord(' '))
                except curses.error:
                    pass

        if args.showpath:
            for pathCell in self.shortestPath.getCells():
                y=(1+pathCell.row)*2-1
                x=(1+pathCell.column)*4-2
                if y==goalScreenRow and x==goalScreenColumn:
                    self.gamepad.addch(y,x, ord(self.goal.symbol))
                else:
                    self.gamepad.addch(y,x, ord('*'))

        if args.showmaze:
            for row in range(MAZE_ROWS):
                for col in range(MAZE_COLS):
                    currentCell=self.grid.getCell(row,col)
                    screenRow=row*2+1
                    screenColumn=(1+col)*4-2
                    self.renderCell(currentCell,screenRow, screenColumn)


        #player location on screen
        #center of screen in bottom row above status line
        #screen row is location in pad
        self.player.screenRow=PAD_ROWS-3
        self.player.screenColumn=(1+self.player.column)*4-2

        #init game cells
        #set starting location, set goal
        for cell in self.grid.eachCell():
            cell.setContent(" ")

        #visible pad upper left corner
        self.padCornerRow=PAD_ROWS - SCREEN_ROWS
        self.padCornerColumn=PAD_COLS  - SCREEN_COLUMNS
        if self.padCornerColumn<0 or self.player.column<6:
            self.padCornerColumn=0


        self.updatePad()

    def movePlayer(self,direction):
        #direction is 'up', 'down', 'left', 'right'
        #toRow and toColumn are maze coordinates where to move the player
        player=self.player    
        grid=self.grid
        cell=grid.getCell(player.row,player.column)
        toCell=None
        if direction=='up':
            toCell=cell.north
        if direction=='down':
            toCell=cell.south
        if direction=='left':
            toCell=cell.west
        if direction=='right':
            toCell=cell.east

        if cell.linked(toCell):
            #adds . to cell where just left
            if self.shortestPath.isPartOfPath(cell) and args.showpath:
                self.addCharacter(player.screenRow, player.screenColumn, 'o')
            else:
                self.addCharacter(player.screenRow, player.screenColumn, '.')
            if direction=='up':
                player.row=player.row-1
                player.screenRow=player.screenRow-2
            if direction=='right':
                player.column=player.column+1
                player.screenColumn=player.screenColumn+4
            if direction=='down':
                player.row=player.row+1
                player.screenRow=player.screenRow+2
            if direction=='left':
                player.column=player.column-1
                player.screenColumn=player.screenColumn-4
                if player.screenColumn<1:
                    player.screenColumn=1
            #adds cell where just moved to
            player.addVisitedCell(grid.getCell(player.row,player.column))
            self.totalMoves=self.totalMoves+1
        else:
            pass
        self.updatePad()


    def addCharacter(self,row,column,chr):
        #add character to game screen
        #note: this should be only place where actual addstr takes place
        #in gamepad
        self.gamepad.addstr(row,column,chr)

    def updatePad(self):
        #updates game pad

        #update cell
        playerRow=self.player.row
        playerColumn=self.player.column
        currentCell=self.grid.getCell(playerRow,playerColumn)
        self.renderCell(currentCell,self.player.screenRow, self.player.screenColumn)

        #update player
        self.addCharacter(self.player.screenRow, self.player.screenColumn, self.player.symbol)

        self.refreshScreen()

        if self.player.row==self.goal.row and self.player.column==self.goal.column:
            #Player reached the goal
            if self.replayInProgress==False:
                infoWindow(self.stdscr,line1="'X' reached!",line3="Score: %d" % self.score)
            else:
                infoWindow(self.stdscr,line1="Replay complete!",line3="Level: %d" % self.level)
            self.gameover=True


    def scroll(self):
        screenRow=self.player.screenRow
        screenColumn=self.player.screenColumn
        
        visibleWinRows=self.padCornerRow+SCREEN_ROWS-1
        visibleWinColumns=self.padCornerColumn+SCREEN_COLUMNS-1
        if (screenRow-self.padCornerRow)<4:
            self.padCornerRow=self.padCornerRow-2
            if self.padCornerRow<1:
                self.padCornerRow=0
        if (screenRow-self.padCornerRow)>SCREEN_ROWS-5:
            self.padCornerRow=self.padCornerRow+2
            if self.padCornerRow>18:
                self.padCornerRow=18
        if (screenColumn-self.padCornerColumn)<4:
            self.padCornerColumn=self.padCornerColumn-4
            if self.padCornerColumn<4:
                self.padCornerColumn=0
        if (screenColumn-self.padCornerColumn)>77:
            self.padCornerColumn=self.padCornerColumn+4
            if self.padCornerColumn>20:
                self.padCornerColumn=20


    def calculateScore(self,updateStatusLine=True):
        #elapsed since start
        elapsedMsec=(utils.currentTimeMillis() - self.startTime)
        self.elapsed=elapsedMsec/1000.0
        currentTotalMoves=float(self.totalMoves)
        if currentTotalMoves==0:
            self.score=0.0
        else:
            baselineScore=10000#arbitrary optimal score
            defaultMoveTimeMsec=300.0#arbitrary move time
            steps=float(self.shortestPathLength)
            baselineTimeMsec=steps*defaultMoveTimeMsec
            defaultScorePerStep=baselineScore/steps

            #if taken more steps than optimal, it affects negatively to score
            if currentTotalMoves>steps:
                currentDefaultStepScore=(currentTotalMoves*defaultScorePerStep)-(currentTotalMoves-steps)*defaultScorePerStep
            else:
                currentDefaultStepScore=currentTotalMoves*defaultScorePerStep

            #if elapsed time is faster than baseline time if increases the score
            self.score=math.ceil(currentDefaultStepScore*(baselineTimeMsec/float(elapsedMsec)))
        
        if updateStatusLine==True and self.replayInProgress==False:
            self.updateStatusLine("Level: %d Moves: %d/%d Elapsed: %.03fsecs Score: %d" % (self.level,self.totalMoves,self.shortestPathLength,self.elapsed,self.score))

    def refreshScreen(self):
        #show pad in screen
        #Displays a section of the pad in the middle of the screen
        if self.useFullTerminal==False:
            self.scroll()
            repeat=True
            col=SCREEN_COLUMNS
            while repeat:                
                try:
                    self.gamepad.refresh(self.padCornerRow,self.padCornerColumn, 0,0,SCREEN_ROWS-1,col)
                    repeat=False
                except:
                    #Cygwin default bash prompt fails to scroll screen to left
                    #this while,except should fix it
                    #utils.debug("Error scrolling to cols: %d" % col)
                    col=col-1
        else:
            self.gamepad.refresh()

        screenRow=self.player.screenRow
        screenColumn=self.player.screenColumn

        playerRow=self.player.row
        playerColumn=self.player.column
        self.calculateScore()

        if self.replayInProgress==True:
            self.updateStatusLine("REPLAY Level: %d Moves: %d/%d " % (self.level,self.totalMoves,self.shortestPathLength))


    def renderCell(self,cell,centerRow,centerColumn,recursion=True):
    
        #corners are always visible in current cell
        self.addCellChar(centerRow+1, centerColumn-2,"+")
        self.addCellChar(centerRow-1, centerColumn-2,"+")
        self.addCellChar(centerRow+1, centerColumn+2,"+")
        self.addCellChar(centerRow-1, centerColumn+2,"+")

        if not cell.linked(cell.north):
            self.addCellChar(centerRow-1, centerColumn,"-")
            self.addCellChar(centerRow-1, centerColumn-1,"-")
            self.addCellChar(centerRow-1, centerColumn+1,"-")
        else:
            if recursion:
                self.renderCell(cell.north,centerRow-2,centerColumn,False)

        if  not cell.linked(cell.south):
            self.addCellChar(centerRow+1, centerColumn,"-")
            self.addCellChar(centerRow+1, centerColumn-1,"-")
            self.addCellChar(centerRow+1, centerColumn+1,"-")
        else:
            if recursion:
                self.renderCell(cell.south,centerRow+2,centerColumn,False)

        if  not cell.linked(cell.east):
            self.addCellChar(centerRow, centerColumn+2,"|")
        else:
            if recursion:
                self.renderCell(cell.east,centerRow,centerColumn+4,False)

        if  not cell.linked(cell.west):
            self.addCellChar(centerRow, centerColumn-2,"|")
        else:
            if recursion:
                self.renderCell(cell.west,centerRow,centerColumn-4,False)

    def addCellChar(self,row,column,chr):
        if row>PAD_ROWS-2:
            #if row is in the status line, do nothing
            return
        if row<0:
            #if row is above upper screen, do nothing
            return
        if column>=PAD_COLS:
            #if column is right of right border, do nothing
            return
        if column<0:
            #if column is left of left border, do nothing
            return
        #if row,column is empty add character
        _chr=self.gamepad.inch(row,column)
        if _chr == ord(' '):
            self.addCharacter(row,column, chr)

    
    def updateStatusLine(self,status):
        if self.useFullTerminal==False:
            row=SCREEN_ROWS-1
        else:
            row=PAD_ROWS
        self.stdscr.move(row, 0)
        self.stdscr.clrtoeol()
        #do not use addCharacter here
        self.stdscr.addstr(row, 0, status)
        self.stdscr.refresh()



def start(stdscr,textList):
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
    infoWindow(stdscr,line1=line1,line3=line3)

    stdscr.clear()

    useFullTerminal=False
    if args.fullscreen:
        useFullTerminal=True
    gameScreen=GameScreen(stdscr,useFullTerminal)
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

    if replayGameId is None:
        if gameScreen.gameover==True:
            cheat=False
            if args.showpath or args.showmaze:
                cheat=True
            gameid=saveScores(gameScreen.player,gameScreen.level,gameScreen.score,gameScreen.totalMoves,gameScreen.shortestPathLength,gameScreen.elapsed,cheat,gameScreen.algorithm)
            textList.append("'X' reached:")
            textList.append("  Game ID  : %d" % gameid)
            textList.append("  Level    : %d" % gameScreen.level)
            textList.append("  Algorithm: %s" % MAZE_ALGORITHMS[gameScreen.algorithm])
            textList.append("  Moves    : %d/%d" % (gameScreen.totalMoves,gameScreen.shortestPathLength))
            textList.append("  Elapsed  : %.03fsecs" % gameScreen.elapsed)
            textList.append("  Score    : %d" % gameScreen.score)
            if args.showpath:
                textList.append("  --showpath cheat was active.")
            if args.showmaze:
                textList.append("  --showmaze cheat was active.")
        else:
            textList.append("'X' not reached:")
            textList.append("  Level  : %d" % gameScreen.level)


def getGameMoves(gameId):
    dbFile=getHighScoreFile()

    (conn,cursor)=utils.openDatabase(dbFile)
    cursor.execute("select level from highscores where gameid=%d" % gameId)
    level=cursor.fetchone()[0]
    moves=[]
    for row in cursor.execute("select row,column from gamemoves where gameid=%d order by move_index" % gameId):
        moves.append((row['row'],row['column']))
    utils.closeDatabase(conn)

    return (level,moves)

def getHighScoreFile():
    dbFile=os.environ.get(MAZINGAME_HIGHSCORE_FILE)
    if dbFile==None:
        from os.path import expanduser
        HOMEDIR = expanduser("~")
        dbFile="%s/%s" % (HOMEDIR,DEFAULT_MAZINGAME_HIGHSCORE_FILE)
    #utils.debug(dbFile)
    return dbFile

def saveScores(player,level,score,moves,shortestPath,elapsed,cheat,algorithm):
    #TODO: change high score file to text file and use inmemory sqlite to show scores
    #similar to CLI Password Manager
    dbFile=getHighScoreFile()

    timestamp=utils.currentTimeISO8601()
    (conn,cursor)=utils.openDatabase(dbFile)

    #SQLite uses boolean value '1' for true and '0' false
    cursor.execute('''CREATE TABLE IF NOT EXISTS highscores (gameid integer primary key autoincrement, timestamp text, score integer, level integer, algorithm text, player_name text, elapsed_secs real,moves integer, shortest_path_moves integer,cheat integer,version text)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS gamemoves (gameid integer, move_index integer, row integer, column integer)''')

    values = (timestamp,score,level,elapsed,moves,shortestPath,cheat,player.name,algorithm,VERSION)
    cursor.execute('insert into highscores (timestamp,score,level,elapsed_secs,moves,shortest_path_moves,cheat,player_name,algorithm,version) values (?,?,?,?,?,?,?,?,?,?)', values)
    #save player moves for replay
    values= (timestamp,)
    cursor.execute("select gameid from highscores where timestamp=?",values)
    gameid=cursor.fetchone()[0]
    moveIndex=0

    for cell in player.visitedCells:
        values = (gameid,moveIndex,cell.row,cell.column)
        cursor.execute('insert into gamemoves (gameid,move_index,row,column) values (?,?,?,?)', values)
        moveIndex=moveIndex+1

    conn.commit()
    utils.closeDatabase(conn)
    return gameid

def listHighScores():
    dbFile=getHighScoreFile()
    (conn,cursor)=utils.openDatabase(dbFile)

    level=None
    algorithm=None

    cheat=False
    if args.showpath or args.showmaze or args.cheat:
        cheat=True

    if args.level:
        level=args.level[0]
    if args.algorithm:
        algorithm=args.algorithm[0]
    
    values= None
    sql="select gameid,timestamp,score,level,algorithm,player_name,elapsed_secs,moves,shortest_path_moves,cheat,version from highscores"
    if level is not None:
        sql=sql+" where level=%d" % level
    if level is not None:
        sql=sql+" and " 
    else:
        sql=sql+" where " 
    if cheat==True:
        sql=sql+" (cheat=0 or cheat=1)"
    else:
        sql=sql+" cheat=0"
    if algorithm is not None:
        sql=sql+" and algorithm='%s'" % algorithm


    sql=sql+" order by score desc"
    #print(sql)
    scores=[]
    rank=1
    #TODO: refactor code below
    #better formatting
    scores.append(["RANK","SCORE","LEVEL","ALGORITHM","MOVES","ELAPSED SECS","GAMEID","PLAYER","VERSION","TIME"])
    for row in cursor.execute(sql):
        scoreRow=[]
        scoreRow.append(rank)
        rank=rank+1
        cheat=row['cheat']
        score=row['score']
        if cheat==1:
            score="%d (cheat)" % score
        scoreRow.append(score)
        scoreRow.append(row['level'])
        scoreRow.append(row['algorithm'])
        scoreRow.append("%d/%d" % (row['moves'],row['shortest_path_moves']))
        scoreRow.append(row['elapsed_secs'])
        scoreRow.append(row['gameid'])
        scoreRow.append(row['player_name'])
        scoreRow.append(row['version'])
        scoreRow.append(row['timestamp'])
        scores.append(scoreRow)

    output=[]

    rankColumnWidth=5
    output.append(scores[0][0].ljust(rankColumnWidth))
    output.append(" ")
    columnWidth=13
    for c in scores[0][1:]:
        s=str(c)
        output.append(s.ljust(columnWidth))
        output.append(" ")
    print("".join(output))
    output=[]
    output.append("-"*rankColumnWidth)
    output.append(" ")
    columnWidth=13
    for c in scores[0][1:]:
        output.append("-"*columnWidth)
        output.append(" ")
    print("".join(output))
    
    for row in scores[1:]:
        output=[]
        first=True
        for c in row:
            s=str(c)           
            if first:
                output.append(s.ljust(rankColumnWidth))
                first=False
            else:
                output.append(s.ljust(columnWidth))
            output.append(" ")
        print("".join(output))
    
    utils.closeDatabase(conn)

def main():
    try:
        parseCommandLineArgs()
        if args.highscores:
            listHighScores()
            return
        if args.version:
            print("%s v%s" % (NAME,VERSION))
            print("")
            print("\n".join(DESCRIPTION))
            print("")
            print(COPYRIGHT)
            print(LICENSE)
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
