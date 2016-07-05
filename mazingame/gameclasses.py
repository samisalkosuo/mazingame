#Classes for MazingGame.
#
# The MIT License (MIT)

# Copyright (c) 2015, 2016 Sami Salkosuo

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

from mazepy import mazepy

class Player:
    
    def __init__(self,name):
        self.name=name
        #row and column are location in maze grid
        self.row=0
        self.column=0
        self.startingRow=0
        self.startingColumn=0
        #screeenRow and screenColumn are location in screen
        self.screenRow=0
        self.screenColumn=0

        self.visitedCells=[]
        self.symbol="@"


    def addVisitedCell(self,cell):
        self.visitedCells.append(cell)        

    def __str__(self):
        output="Name: %s. Maze position:[%d,%d]. Screen position: [%d,%d]" % (self.name,self.row,self.column,self.screenRow,self.screenColumn)
        return output

class Goal:

    def __init__(self,row,column,screenRow,screenColumn):
        self.row=row
        self.column=column
        self.screenRow=screenRow
        self.screenColumn=screenColumn
        self.symbol="X"

    def __str__(self):
        output="Goal maze position: [%d,%d], screen position: [%d,%d]" % (self.row,self.column,self.screenRow,self.screenColumn)
        return output


class MazingCell(mazepy.Cell):
    pass

class GameGrid(mazepy.Grid):

    def contentsOf(self,cell):
        return cell.getContent()
