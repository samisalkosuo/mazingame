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

#GameScreen class
import random
import getpass
import math

from mazepy import mazepy
from .curses_utils import curses_utils
from .utils import utils
from .highscores import *
from .gameclasses import Player
from .gameclasses import Goal
from .gameclasses import MazingCell
from .gameclasses import GameGrid
from .curses_utils import curses_utils

class GameScreen:
    #game screen has status line, visible screen area and full maze area as pad
    def __init__(self,stdscr,useFullTerminal,args):
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
        self.args=args
        #screenshot index
        self.screenshotIndex=0   

    def initGame(self,level=None):
        
        if level is None:
            #set level
            r=random.random()            
            self.level=(int(1000000000*r))
        else:
            self.level=level
            
        random.seed(self.level)

        name=getpass.getuser()
        self.player=Player(name)

        #if replay get saved grid
        if self.args.replay:
            replayGameId=self.args.replay[0]
            mazeInfo=getMazeInfo(replayGameId)
            jsonString=mazeInfo["maze_json"]

            self.grid=mazepy.initMazeFromJSON(jsonString,MazingCell)
            self.algorithm=self.algorithm
    
            playerRow=mazeInfo["player_row"]
            playerColumn=mazeInfo["player_column"]
            goalRow=mazeInfo["goal_row"]
            goalColumn=mazeInfo["goal_column"]
        else:
            #do it always right after setting random seed, to get same maze when using 
            #same seed
            self.grid=GameGrid(MAZE_ROWS,MAZE_COLS,MazingCell)
            self.algorithm=""
            #if level is None and self.args.algorithm:
            #    self.algorithm=self.args.algorithm[0]
            #else:
            self.algorithm=random.choice(list(mazepy.MAZE_ALGORITHMS.keys()))
        
            self.grid=mazepy.initMaze(self.grid,self.algorithm)

            braid=0.5#self.args.braid
            #if braid<0:
            #    braid=0.0
            #if braid>1.0:
            #    braid=1.0
            self.grid.doBraid(braid)

            playerRow=MAZE_ROWS-1
            playerColumn=random.randint(0,MAZE_COLS-1)
            goalRow=random.randint(0,MAZE_ROWS/2)
            goalColumn=random.randint(0,MAZE_COLS-1)
        
        #set start time after maze has been initialized
        self.startTime=utils.currentTimeMillis()

        self.player.row=playerRow
        self.player.column=playerColumn
        self.player.startingRow=playerRow
        self.player.startingColumn=playerColumn

        currentCell=self.grid.getCell(playerRow,playerColumn)
        self.player.addVisitedCell(currentCell)

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

        if self.args.showpath:
            for pathCell in self.shortestPath.getCells():
                y=(1+pathCell.row)*2-1
                x=(1+pathCell.column)*4-2
                if y==goalScreenRow and x==goalScreenColumn:
                    self.gamepad.addch(y,x, ord(self.goal.symbol))
                else:
                    self.gamepad.addch(y,x, ord('*'))

        if self.args.showmaze:
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
            if self.shortestPath.isPartOfPath(cell) and self.args.showpath:
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


    def takeScreenshot(self):
        #take screenshot to specified directory
        #hardcoded to use Cygwin
        os.system('/usr/bin/import.exe -window "/cygdrive/c/Dropbox/git/mazingame" /cygdrive/c/Dropbox/git/mazingame/temp/image_%03d.png' % screenshotIndex)
        self.screenshotIndex=self.screenshotIndex+1

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
                curses_utils.infoWindow(self.stdscr,line1="'X' reached!",line3="Score: %d" % self.score)
            else:
                curses_utils.infoWindow(self.stdscr,line1="Replay complete!",line3="Game id: %d" % self.args.replay[0])
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
        if self.args.replay:
        #if self.args.view:
            #do not calculate score if replaying
            return
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
            self.updateStatusLine("P: (%d,%d) X: (%d,%d) Moves: %d/%d Elapsed: %.03fsecs Score: %d" % (self.player.row,self.player.column,self.goal.row,self.goal.column,self.totalMoves,self.shortestPathLength,self.elapsed,self.score))
            #self.updateStatusLine("Level: %d Moves: %d/%d Elapsed: %.03fsecs Score: %d" % (self.level,self.totalMoves,self.shortestPathLength,self.elapsed,self.score))

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
        #take screenshot
        #self.takeScreenshot()

        if self.replayInProgress==True:
            self.updateStatusLine("REPLAY Game ID: %d Moves: %d/%d " % (self.args.replay[0],self.totalMoves,self.shortestPathLength))

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


