#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Maze generation library for MazinGame.

This module provides classes and functions for generating and manipulating mazes
using various algorithms. It includes implementations of several classic maze
generation algorithms translated from Ruby code in "Mazes for Programmers" by Jamis Buck.

Supported algorithms:
- Binary Tree (BT)
- Recursive Backtracker (RB)
- Aldous-Broder (AB)
- Wilson (W)
- Hunt and Kill (HK)
- Sidewinder (S)

Classes:
    Cell: Basic cell in a maze with links to neighbors
    Distances: Tracks distances from a root cell to all other cells
    Grid: Represents the maze grid structure
    DistanceGrid: Grid subclass that displays distances

Functions:
    initMaze: Initialize a maze with a specific algorithm
    initMazeFromJSON: Reconstruct a maze from JSON representation
    getRandomMaze: Generate a maze with a random algorithm
"""

# The MIT License (MIT)
#
# Copyright (c) 2016 Sami Salkosuo
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__version__ = "0.3"


PROGRAMNAME="mazepy"
VERSION=__version__
COPYRIGHT="(C) 2016 Sami Salkosuo"


import random
import json
import logging
from typing import Optional, List, Dict, Any, Iterator, Type

logger = logging.getLogger(__name__)

#maze algorithms
MAZE_ALGORITHMS=dict()
MAZE_ALGORITHMS["AB"]="Aldous Broder"
MAZE_ALGORITHMS["BT"]="Binary Tree"
MAZE_ALGORITHMS["HK"]="Hunt And Kill"
MAZE_ALGORITHMS["RB"]="Recursive Backtracker"
MAZE_ALGORITHMS["S"]="Sidewinder"
MAZE_ALGORITHMS["W"]="Wilson"

MAZE_ALGORITHMS_DESC=[]
for a in MAZE_ALGORITHMS.keys():
    MAZE_ALGORITHMS_DESC.append("%s=%s" % (a,MAZE_ALGORITHMS[a]))


#====================
#Maze classes

class Cell:
    """Basic cell class for mazes.
    
    Represents a single cell in a maze grid with links to neighboring cells.
    Cells can be linked (connected) to their neighbors to form passages.
    
    Attributes:
        row: Row position in the grid
        column: Column position in the grid
        north: Reference to northern neighbor cell
        east: Reference to eastern neighbor cell
        south: Reference to southern neighbor cell
        west: Reference to western neighbor cell
        links: Dictionary of linked (connected) neighbor cells
        content: Display content for the cell
    """

    def __init__(self, row: int, column: int) -> None:
        """Initialize a cell at the given position.
        
        Args:
            row: Row position in the grid
            column: Column position in the grid
        """
        self.row=row
        self.column=column
        self.north=None
        self.east=None
        self.south=None
        self.west=None
        self.links=dict()
        self.content="   "

    def setContent(self, content: str) -> None:
        if content==None or len(content)==0:
            self.content="   "
        if len(content)==1:
            self.content=" %s " % content
        if len(content)==2:
            self.content="%s " % content
        if len(content)==3:
            self.content=content
        if len(content)>3:
            self.content=content[0:3]

    def getContent(self) -> str:
        return self.content

    def link(self, cell: 'Cell', bidi: bool = True) -> 'Cell':
        self.links[cell] = True
        if bidi==True:
            cell.link(self,False)
        return self

    def unlink(self, cell: 'Cell', bidi: bool = True) -> 'Cell':
        try:
            del self.links[cell]
        except KeyError:
            pass
        if bidi==True:
            cell.unlink(self, False)
        return self

    def getLinks(self) -> Any:
        return self.links.keys()
    
    def linked(self, cell: Optional['Cell']) -> bool:
        #return self.links.has_key(cell)
        return cell in self.links

    def neighbors(self) -> List['Cell']:
        neighborsList = []
        if self.north:
            neighborsList.append(self.north)
        if self.east:
            neighborsList.append(self.east)
        if self.south:
            neighborsList.append(self.south)
        if self.west:
            neighborsList.append(self.west)
        return neighborsList

    def directionToText(self, direction: Any) -> str:
        if direction==0:
            direction="north"
        if direction==1:
            direction="east"
        if direction==2:
            direction="south"
        if direction==3:
            direction="west"
        
        return direction
        
        
    def getNeighbor(self, direction: Any) -> Optional['Cell']:
        direction=self.directionToText(direction)
        neighborCell=None    
        if direction=="north" and self.linked(self.north):
            neighborCell=self.north
        if direction=="east" and self.linked(self.east):
            neighborCell=self.east
        if direction=="south" and self.linked(self.south):
            neighborCell=self.south
        if direction=="west" and self.linked(self.west):
            neighborCell=self.west
            
        return neighborCell

    def hasNeighbor(self, direction: Any) -> bool:
        direction=self.directionToText(direction)    
        if direction=="north" and self.linked(self.north):
            return True
        if direction=="east" and self.linked(self.east):
            return True
        if direction=="south" and self.linked(self.south):
            return True
        if direction=="west" and self.linked(self.west):
            return True

        return False

    #return Distances from this cell to all other cells
    def getDistances(self) -> 'Distances':
        distances=Distances(self)
        frontier=[]
        frontier.append(self)
        while len(frontier)>0:
            newFrontier=[]
            for cell in frontier:
                for linked in cell.getLinks():
                    if distances.getDistanceTo(linked) is None:
                        dist=distances.getDistanceTo(cell)
                        distances.setDistanceTo(linked,dist+1)
                        newFrontier.append(linked)
            frontier=newFrontier
        return distances

    def toString(self) -> str:
        output="[%d,%d," % (self.row,self.column)
        if self.linked(self.north):
            output=output+"1"
        else:
            output=output+"0"
        output=output+","
        if self.linked(self.east):
            output=output+"1"
        else:
            output=output+"0"
        output=output+","
        if self.linked(self.south):
            output=output+"1"
        else:
            output=output+"0"
        output=output+","
        if self.linked(self.west):
            output=output+"1"
        else:
            output=output+"0"
        output=output+"]"

        return output
    
    def toJSONString(self, prettyprint: bool = False) -> str:
        jsonObj=dict()
        jsonObj["row"]=self.row
        jsonObj["column"]=self.column
        jsonObj["content"]=self.content
        
        jsonObj["north"]=self.linked(self.north)
        jsonObj["east"]=self.linked(self.east)
        jsonObj["south"]=self.linked(self.south)
        jsonObj["west"]=self.linked(self.west)
        
        if prettyprint==True:
            out=json.dumps(jsonObj, indent=2)
        else:
            out=json.dumps(jsonObj)
        return out


    def __str__(self) -> str:
        output="Cell[%d,%d], Linked neighbors: " % (self.row,self.column)
        if self.linked(self.north):
            output=output+" North: YES "
        else:
            output=output+" North: NO "

        if self.linked(self.east):
            output=output+" East: YES "
        else:
            output=output+" East: NO "
        if self.linked(self.south):
            output=output+" South: YES "
        else:
            output=output+" South: NO "
        if self.linked(self.west):
            output=output+" West: YES "
        else:
            output=output+" West: NO "

        return output

class Distances:
    """Tracks distances from a root cell to all other cells in a maze.
    
    Used for pathfinding and calculating shortest paths through the maze.
    
    Attributes:
        rootCell: The starting cell for distance calculations
        cells: Dictionary mapping cells to their distances from root
    """

    def __init__(self, rootCell: Cell) -> None:
        """Initialize distances from a root cell.
        
        Args:
            rootCell: The starting cell for distance calculations
        """
        self.rootCell=rootCell
        self.cells=dict()
        self.cells[self.rootCell]=0

    def getDistanceTo(self, cell: Cell) -> Optional[int]:
        return self.cells.get(cell,None)

    def setDistanceTo(self, cell: Cell, distance: int) -> None:
        self.cells[cell]=distance

    def getCells(self) -> Any:
        return self.cells.keys()

    def isPartOfPath(self, cell: Cell) -> bool:
        #return self.cells.has_key(cell)
        return cell in self.cells

    def __len__(self) -> int:
        return len(self.cells.keys())

    def pathTo(self, goal: Cell) -> 'Distances':
        current=goal
        breadcrumbs = Distances(self.rootCell)
        breadcrumbs.setDistanceTo(current,self.cells[current])

        while current is not self.rootCell:
            for neighbor in current.getLinks():
                if self.cells[neighbor] < self.cells[current]:
                    breadcrumbs.setDistanceTo(neighbor,self.cells[neighbor])
                    current=neighbor
                    break
        return breadcrumbs

class Grid:
    """Represents a maze grid structure.
    
    The Grid class manages the 2D array of cells that make up the maze,
    handles cell configuration, and provides methods for maze manipulation.
    
    Attributes:
        rows: Number of rows in the grid
        columns: Number of columns in the grid
        grid: 2D list of Cell objects
        distances: Optional Distances object for pathfinding
        algorithm: Name of the algorithm used to generate the maze
        algorithm_key: Short key for the algorithm
        braid: Braiding factor (0.0-1.0) for removing dead ends
    """

    def __init__(self, rows: int, columns: int, cellClass: Type[Cell] = Cell) -> None:
        """Initialize a grid with the specified dimensions.
        
        Args:
            rows: Number of rows in the grid
            columns: Number of columns in the grid
            cellClass: Cell class to use for creating cells (default: Cell)
        """
        self.CellClass=cellClass
        self.rows=rows
        self.columns=columns
        self.grid=self.prepareGrid()
        self.distances=None
        self.configureCells()
        self.algorithm_key=None
        self.algorithm=None        
        self.braid=-1.0#no braiding
    
    def prepareGrid(self) -> List[List[Cell]]:
        rowList=[]
        i=0
        j=0
        for i in range(self.rows):
            columnList=[]
            for j in range(self.columns):
                columnList.append(self.CellClass(i,j))
            rowList.append(columnList)
        return rowList

    def eachRow(self) -> Iterator[List[Cell]]:
        for row in self.grid:
            yield row

    def eachCell(self) -> Iterator[Cell]:
        for row in self.grid:
            for cell in row:
                yield cell      

    def configureCells(self) -> None:
        for cell in self.eachCell():
            row=cell.row
            col=cell.column
            cell.north=self.getNeighbor(row-1,col)
            cell.east=self.getNeighbor(row,col+1)
            cell.south=self.getNeighbor(row+1,col)
            cell.west=self.getNeighbor(row,col-1)

    def getCell(self, row: int, column: int) -> Cell:
        
        return self.grid[row][column]
        #return self.grid[row-1][column-1]

    def getNeighbor(self, row: int, column: int) -> Optional[Cell]:
        if not (0 <= row < self.rows):
            return None
        if not (0 <= column < self.columns):
            return None
        return self.grid[row][column]

    def size(self) -> int:
        return self.rows*self.columns

    def randomCell(self) -> Cell:
        row=random.randint(0, self.rows-1)
        column=self.grid
        column = random.randint(0,len(self.grid[row])-1)
        return self.grid[row][column]

    def contentsOf(self, cell: Cell) -> str:
        return "   "

    def getDeadEndCells(self) -> List[Cell]:
        deadends=[]

        for cell in self.eachCell():
            if len(cell.getLinks())==1:
                deadends.append(cell)
        return deadends

    def doBraid(self, p: float = 1.0) -> None:
        self.braid=p
        for cell in self.getDeadEndCells():
            if len(cell.getLinks())!=1 or random.random()>p:
                continue
            
            neighbors=[n for n in cell.neighbors() if cell.linked(n) == False]
            best=[n for n in neighbors if len(cell.getLinks())==1]
            if len(best)==0:
                best=neighbors
            neighbor=random.choice(best)
            cell.link(neighbor)

    def toJSONString(self, prettyprint: bool = False) -> str:
        #get JSON string of this grid
        
        jsonObj=dict()
        jsonObj["algorithm"]=self.algorithm
        jsonObj["algorithm_key"]=self.algorithm_key
        jsonObj["rows"]=self.rows
        jsonObj["columns"]=self.columns
        jsonObj["braid"]=self.braid

        cells=[]
        for cell in self.eachCell():
            cells.append(cell.toJSONString(False))
        jsonObj["cells"]=cells        
        if prettyprint==True:
            out=json.dumps(jsonObj, indent=2)
        else:
            out=json.dumps(jsonObj)
        return out

    def __str__(self) -> str:
        return self.asciiStr()

    def unicodeStr(self) -> None:
        pass

    def asciiStr(self) -> str:
        output = "+" + "---+" * self.columns + "\n"
        for row in self.eachRow():
            top = "|"
            bottom = "+"
            for cell in row:
                if not cell:                
                    cell=Cell(-1,-1)
                body = "%s" % self.contentsOf(cell)
                if cell.linked(cell.east):
                    east_boundary=" "
                else:
                    east_boundary="|"

                top = top + body + east_boundary
                if cell.linked(cell.south):
                    south_boundary="   "
                else:
                    south_boundary="---"
                corner = "+"
                bottom =bottom + south_boundary + corner
            
            output=output+top+"\n"
            output=output+bottom+"\n"
        return output
 
class DistanceGrid(Grid):

    #def __init__(self,rows,columns,cellClass=Cell):
    #    super(Grid, self).__init__(rows,columns,cellClass)

    def contentsOf(self, cell: Cell) -> str:

        if  self.distances.getDistanceTo(cell) is not None and self.distances.getDistanceTo(cell) is not None:
            n=self.distances.getDistanceTo(cell)
            return "%03d" % n
        else:
            return "   " #super(Grid, self).contentsOf(cell)

#====================
#init mazes

def initMazeFromJSON(jsonString: str, cellClass: Type[Cell] = Cell, gridClass: Type[Grid] = Grid) -> Grid:
    """Initialize a maze from a JSON string representation.
    
    Args:
        jsonString: JSON string containing maze data
        cellClass: Cell class to use (default: Cell)
        gridClass: Grid class to use (default: Grid)
        
    Returns:
        Reconstructed Grid object
    """
    
    jsonObj = json.loads(jsonString)
    rows=jsonObj["rows"]
    columns=jsonObj["columns"]
    grid=gridClass(rows,columns,cellClass)
    grid.algorithm=jsonObj["algorithm"]
    grid.algorithm_key=jsonObj["algorithm_key"]
    grid.braid=jsonObj["braid"]

    #init cells
    #for each cell link those that are neigbors
    for _cell in jsonObj["cells"]:
        cell=json.loads(_cell)
        gridCell=grid.getCell(cell["row"],cell["column"])
        if "content" in cell:
            gridCell.content=cell["content"]
        else:
            gridCell.setContent(" ")
        
        if cell["north"]:
            gridCell.link(gridCell.north)
        if cell["east"]:
            gridCell.link(gridCell.east)
        if cell["south"]:
            gridCell.link(gridCell.south)
        if cell["west"]:
            gridCell.link(gridCell.west)

    return grid


def initMaze(grid: Grid, algorithm: str) -> Grid:
    """Initialize a maze using the specified algorithm.
    
    Args:
        grid: Grid object to populate with maze
        algorithm: Algorithm key (BT, RB, AB, W, HK, S)
        
    Returns:
        Grid object with generated maze
    """
    if algorithm=="AB":
        grid=initAldousBroderMaze(grid)
    if algorithm=="BT":
        grid=initBinaryTreeMaze(grid)
    if algorithm=="RB":
        grid=initRecursiveBacktrackerMaze(grid)
    if algorithm=="S":
        grid=initSidewinderMaze(grid)
    if algorithm=="W":
        grid=initWilsonMaze(grid)
    if algorithm=="HK":
        grid=initHuntAndKillMaze(grid)

    grid.algorithm=MAZE_ALGORITHMS[algorithm]
    grid.algorithm_key=algorithm

    return grid

def getRandomMaze(grid: Grid) -> Grid:
  algorithm=random.choice(list(MAZE_ALGORITHMS.keys()))
  return initMaze(grid,algorithm)

def initBinaryTreeMaze(grid: Grid) -> Grid:
    for cell in grid.eachCell():
        neighbors=[]
        if cell.north:
            neighbors.append(cell.north)
        if cell.east:
            neighbors.append(cell.east)
        if len(neighbors)>0:
            if len(neighbors)==1:
                ind=0
            else:
                ind=random.randint(0,len(neighbors)-1)
            neighbor=neighbors[ind]
            if neighbor:
                cell.link(neighbor)
    return grid


def initRecursiveBacktrackerMaze(grid: Grid) -> Grid:
    stack = [] 
    stack.append(grid.randomCell())

    while len(stack)>0: 
        current = stack[-1]
        neighbors=[]
        for n in current.neighbors():
            if len(n.getLinks())==0:
                neighbors.append(n)

        if len(neighbors)==0:
            stack.pop()
        else:
            neighbor = random.choice(neighbors)
            current.link(neighbor) 
            stack.append(neighbor) 

    return grid

def initSidewinderMaze(grid: Grid) -> Grid:
    tf=[True,False]
    for row in grid.eachRow():
        run=[]
        for cell in row:
            run.append(cell)
            at_eastern_boundary = (cell.east == None)
            at_northern_boundary = (cell.north == None)
            #note: ruby: 0 == True
            should_close_out =at_eastern_boundary or ( at_northern_boundary==False and random.choice(tf) == True)
            if should_close_out == True:
                member = random.choice(run)
                if member.north:
                    member.link(member.north)
                run=[]
            else:
                cell.link(cell.east)
    return grid

def initAldousBroderMaze(grid: Grid) -> Grid:
    cell=grid.randomCell()
    unvisited=grid.size()-1
    while unvisited > 0:
        neighbor = random.choice(cell.neighbors())
        if len(neighbor.getLinks())==0:#isempty
            cell.link(neighbor)
            unvisited=unvisited-1
        cell=neighbor
    return grid

def initWilsonMaze(grid: Grid) -> Grid:
    unvisited=[]
    for cell in grid.eachCell():
        unvisited.append(cell)

    first = random.choice(unvisited)
    unvisited.remove(first)

    while len(unvisited)>0:
        cell=random.choice(unvisited)
        path=[cell]
        while cell in unvisited:
            cell=random.choice(cell.neighbors())
            if cell in path:
                position=path.index(cell)
                #in Ruby code: path = path[0..position]
                #is in Python needs the line below
                path=path[:position+1]
            else:
                path.append(cell)
        #in Ryby: 0.upto(path.length-2)
        #is in Python the line below
        for i in range(len(path)-1):
            path[i].link(path[i+1])
            unvisited.remove(path[i])

    return grid

def initHuntAndKillMaze(grid: Grid) -> Grid:
    currentCell = grid.randomCell()

    while currentCell != None:
        unvisitedNeighbors= [n for n in currentCell.neighbors() if len(n.getLinks()) == 0]  
        if len(unvisitedNeighbors)>0:
            neighbor=random.choice(unvisitedNeighbors)
            currentCell.link(neighbor)
            currentCell=neighbor
        else:
            currentCell=None
            for cell in grid.eachCell():
                visitedNeighbors= [n for n in cell.neighbors() if len(n.getLinks()) != 0]
                if len(cell.getLinks())==0 and len(visitedNeighbors)!=0:
                    currentCell=cell
                    neighbor=random.choice(visitedNeighbors)
                    currentCell.link(neighbor)
                    break

    return grid

def printGrid(grid: Grid, withDistance: bool = False) -> None:
    print("%s Maze" % grid.algorithm)
    print("Deadends: %d" % len(grid.getDeadEndCells()))
    if withDistance==False:
        print(grid)
        print()
    else:
        startRow=0#random.randint(0, rows-1)
        startColumn=0#random.randint(0, columns-1)
        start = grid.getCell(startRow,startColumn)
        goalRow=grid.rows-1#random.randint(0, rows-1)
        goalColumn=grid.columns-1#random.randint(0, columns-1)
        goal= grid.getCell(goalRow,goalColumn)
        distances = start.getDistances()
        grid.distances = distances.pathTo(goal)
        print("Start: ", start.toString())
        print("Goal: ", goal.toString())
        print(grid)

def main() -> None:
    rows,columns=10,10
    grid=Grid(rows,columns)
    grid=initMaze(grid,"BT")
    printGrid(grid)
    
    grid=DistanceGrid(rows,columns)
    grid=initMaze(grid,"RB")
    startRow=0#random.randint(0, rows-1)
    startColumn=0#random.randint(0, columns-1)
    start = grid.getCell(startRow,startColumn)
    goalRow=rows-1#random.randint(0, rows-1)
    goalColumn=columns-1#random.randint(0, columns-1)

    goal= grid.getCell(goalRow,goalColumn)
    distances = start.getDistances()
    grid.distances = distances.pathTo(goal)
    print("Recursive Backtracker Maze:")
    print("Start: ", start.toString())
    print("Goal: ", goal.toString())
    print(grid)

    grid=Grid(rows,columns)
    grid=initMaze(grid,"S")
    printGrid(grid)

    grid=Grid(rows,columns)
    grid=initMaze(grid,"AB")
    printGrid(grid)

    grid=Grid(rows,columns)
    grid=initMaze(grid,"W")
    printGrid(grid)

    grid=Grid(rows,columns)
    grid=initMaze(grid,"HK")
    printGrid(grid)

    grid=DistanceGrid(rows,columns)
    grid=initMaze(grid,"W")
    printGrid(grid,withDistance=True)

    grid=Grid(rows,columns)
    grid=getRandomMaze(grid)
    print("Random maze:")
    printGrid(grid)
    print("Same maze but braided (1.0):")
    grid.doBraid()
    printGrid(grid)

    grid=DistanceGrid(rows,columns)
    grid=getRandomMaze(grid)
    print("Random maze:")
    printGrid(grid,withDistance=True)
    print("Same maze but braided (0.4):")
    grid.doBraid(0.4)
    printGrid(grid,withDistance=True)

    grid=Grid(rows,columns)
    grid=getRandomMaze(grid)
    grid.doBraid(0.5)
    print("Random maze to be exported:")
    printGrid(grid)
    #print("Maze as JSON:")
    jsonString=grid.toJSONString(True)
    #print(jsonString)
    print("Same maze from JSON:")
    grid=initMazeFromJSON(jsonString,Cell)
    printGrid(grid)

if __name__ == "__main__": 
    main()

# Made with Bob
