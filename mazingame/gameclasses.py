"""Classes for MazingGame.

The MIT License (MIT)

Copyright (c) 2015, 2016 Sami Salkosuo

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

from typing import List
from .mazepy import mazepy


class Player:
    """Represents the player in the maze game."""
    
    def __init__(self, name: str) -> None:
        """Initialize a player.
        
        Args:
            name: Player's name
        """
        self.name: str = name
        # Row and column are location in maze grid
        self.row: int = 0
        self.column: int = 0
        self.startingRow: int = 0
        self.startingColumn: int = 0
        # screenRow and screenColumn are location in screen
        self.screenRow: int = 0
        self.screenColumn: int = 0
        self.visitedCells: List[mazepy.Cell] = []
        self.symbol: str = "@"

    def addVisitedCell(self, cell: mazepy.Cell) -> None:
        """Add a cell to the list of visited cells.
        
        Args:
            cell: Cell that was visited
        """
        self.visitedCells.append(cell)

    def __str__(self) -> str:
        """Return string representation of player.
        
        Returns:
            String with player name and position information
        """
        return (f"Name: {self.name}. Maze position:[{self.row},{self.column}]. "
                f"Screen position: [{self.screenRow},{self.screenColumn}]")


class Goal:
    """Represents the goal location in the maze."""

    def __init__(self, row: int, column: int, screenRow: int, screenColumn: int) -> None:
        """Initialize a goal.
        
        Args:
            row: Goal row in maze grid
            column: Goal column in maze grid
            screenRow: Goal row on screen
            screenColumn: Goal column on screen
        """
        self.row: int = row
        self.column: int = column
        self.screenRow: int = screenRow
        self.screenColumn: int = screenColumn
        self.symbol: str = "X"

    def __str__(self) -> str:
        """Return string representation of goal.
        
        Returns:
            String with goal position information
        """
        return (f"Goal maze position: [{self.row},{self.column}], "
                f"screen position: [{self.screenRow},{self.screenColumn}]")


class MazingCell(mazepy.Cell):
    """Custom cell class for MazinGame, extends mazepy.Cell."""
    pass


class GameGrid(mazepy.Grid):
    """Custom grid class for MazinGame, extends mazepy.Grid."""

    def contentsOf(self, cell: mazepy.Cell) -> str:
        """Get the content of a cell.
        
        Args:
            cell: Cell to get content from
            
        Returns:
            Cell content as string
        """
        return cell.getContent()
