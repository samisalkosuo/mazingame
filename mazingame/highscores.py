"""High score management for MazinGame.

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

import os
import logging
from typing import List, Tuple, Optional, Dict, Any
from .utils import utils
from .globals import MAZINGAME_HIGHSCORE_FILE, DEFAULT_MAZINGAME_HIGHSCORE_FILE

logger = logging.getLogger(__name__)


def getGameMoves(gameId: int) -> Tuple[int, List[Tuple[int, int]]]:
    """Get game moves from database.
    
    Args:
        gameId: Game ID to retrieve moves for
        
    Returns:
        Tuple of (level, list of (row, column) moves)
        
    Raises:
        sqlite3.Error: If database query fails
    """
    dbFile = getHighScoreFile()
    if dbFile is None:
        logger.error("No high score file available")
        raise ValueError("High score file not available")

    try:
        (conn, cursor) = utils.openDatabase(dbFile)
        cursor.execute("select level from highscores where gameid=?", (gameId,))
        result = cursor.fetchone()
        if result is None:
            raise ValueError(f"Game ID {gameId} not found")
        level = result[0]
        
        moves: List[Tuple[int, int]] = []
        for row in cursor.execute(
            "select row,column from gamemoves where gameid=? order by move_index",
            (gameId,)
        ):
            moves.append((row['row'], row['column']))
        utils.closeDatabase(conn)
        
        logger.debug(f"Retrieved {len(moves)} moves for game {gameId}")
        return (level, moves)
    except Exception as e:
        logger.error(f"Error retrieving game moves for game {gameId}: {e}")
        raise


def getMazeInfo(gameId: int) -> Optional[Dict[str, Any]]:
    """Get maze information from database.
    
    Args:
        gameId: Game ID to retrieve maze info for
        
    Returns:
        Dictionary with maze information or None if not found
    """
    dbFile = getHighScoreFile()
    if dbFile is None:
        logger.warning("No high score file available")
        return None
    
    try:
        (conn, cursor) = utils.openDatabase(dbFile)
        cursor.execute(
            "select maze_json,player_row,player_column,goal_row,goal_column from mazes where gameid=?",
            (gameId,)
        )
        row = cursor.fetchone()
        if row is None:
            logger.warning(f"No maze info found for game {gameId}")
            utils.closeDatabase(conn)
            return None
            
        result: Dict[str, Any] = {
            "maze_json": row["maze_json"],
            "player_row": row["player_row"],
            "player_column": row["player_column"],
            "goal_row": row["goal_row"],
            "goal_column": row["goal_column"]
        }
        utils.closeDatabase(conn)
        
        logger.debug(f"Retrieved maze info for game {gameId}")
        return result
    except Exception as e:
        logger.error(f"Error retrieving maze info for game {gameId}: {e}")
        return None


def getHighScoreFile() -> Optional[str]:
    """Get the path to the high score database file.
    
    Returns:
        Path to high score file or None if not available
    """
    gameDataDir = "/data"
    if not os.path.exists(gameDataDir):
        logger.debug("Game data directory does not exist, scores will not be saved")
        return None
    
    dbFile = os.environ.get(MAZINGAME_HIGHSCORE_FILE)
    if dbFile is None:
        dbFile = f"{gameDataDir}/{DEFAULT_MAZINGAME_HIGHSCORE_FILE}"
    
    logger.debug(f"High score file: {dbFile}")
    return dbFile


def saveScores(
    args: Any,
    version: str,
    grid: Any,
    player: Any,
    goal: Any,
    level: int,
    score: int,
    moves: int,
    shortestPath: int,
    elapsed: float,
    cheat: bool,
    algorithm: str
) -> int:
    """Save game scores to database.
    
    Args:
        args: Command line arguments
        version: Game version
        grid: Game grid object
        player: Player object
        goal: Goal object
        level: Game level
        score: Player score
        moves: Number of moves taken
        shortestPath: Shortest path length
        elapsed: Elapsed time in seconds
        cheat: Whether cheat mode was used
        algorithm: Maze algorithm used
        
    Returns:
        Game ID or -1 if not saved
    """
    # Braid no longer option, hardcoded to 0.5
    braid = 0.5
    
    # Do not save score if viewing replay
    if args.replay:
        logger.debug("Not saving score for replay")
        return -1

    dbFile = getHighScoreFile()
    if dbFile is None:
        logger.warning("No high score file, score not saved")
        return -1

    try:
        timestamp = utils.currentTimeISO8601()
        (conn, cursor) = utils.openDatabase(dbFile)

        # SQLite uses boolean value '1' for true and '0' false
        cursor.execute('''CREATE TABLE IF NOT EXISTS highscores (
            gameid integer primary key autoincrement,
            timestamp text,
            score integer,
            level integer,
            algorithm text,
            player_name text,
            elapsed_secs real,
            moves integer,
            shortest_path_moves integer,
            cheat integer,
            version text,
            braid real,
            replay_of_gameid integer
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS gamemoves (
            gameid integer,
            move_index integer,
            row integer,
            column integer
        )''')

        replaygameid = args.replay[0] if args.replay else 0
        values = (timestamp, score, level, elapsed, moves, shortestPath, int(cheat),
                 player.name, algorithm, version, braid, replaygameid, level)
        cursor.execute(
            'insert into highscores (timestamp,score,level,elapsed_secs,moves,'
            'shortest_path_moves,cheat,player_name,algorithm,version,braid,'
            'replay_of_gameid,level) values (?,?,?,?,?,?,?,?,?,?,?,?,?)',
            values
        )
        
        # Save player moves for replay
        cursor.execute("select gameid from highscores where timestamp=?", (timestamp,))
        result = cursor.fetchone()
        if result is None:
            raise ValueError("Failed to retrieve game ID after insert")
        gameid = result[0]

        # Save maze
        mazeJSON = grid.toJSONString()
        cursor.execute('''CREATE TABLE IF NOT EXISTS mazes (
            gameid integer,
            player_row integer,
            player_column integer,
            goal_row integer,
            goal_column integer,
            maze_json text
        )''')
        values = (gameid, player.startingRow, player.startingColumn,
                 goal.row, goal.column, mazeJSON)
        cursor.execute(
            'insert into mazes (gameid,player_row,player_column,goal_row,'
            'goal_column,maze_json) values (?,?,?,?,?,?)',
            values
        )

        moveIndex = 0
        for cell in player.visitedCells:
            values = (gameid, moveIndex, cell.row, cell.column)
            cursor.execute(
                'insert into gamemoves (gameid,move_index,row,column) values (?,?,?,?)',
                values
            )
            moveIndex += 1

        conn.commit()
        utils.closeDatabase(conn)
        
        logger.info(f"Saved game {gameid} with score {score}")
        return gameid
    except Exception as e:
        logger.error(f"Error saving scores: {e}")
        return -1


def selectFromHighScores(gameid: int, columnName: str) -> Any:
    """Select a specific column from high scores.
    
    Args:
        gameid: Game ID
        columnName: Column name to retrieve
        
    Returns:
        Column value or None
    """
    dbFile = getHighScoreFile()
    if dbFile is None:
        logger.warning("No high score file available")
        return None
    
    try:
        (conn, cursor) = utils.openDatabase(dbFile)
        cursor.execute(
            f"select {columnName} from highscores where gameid=?",
            (gameid,)
        )
        result = None
        row = cursor.fetchone()
        if row:
            result = row[columnName]
        utils.closeDatabase(conn)
        return result
    except Exception as e:
        logger.error(f"Error selecting from high scores: {e}")
        return None


def listHighScores(args: Any) -> None:
    """List high scores from database.
    
    Args:
        args: Command line arguments
    """
    dbFile = getHighScoreFile()

    if dbFile is None or not os.path.exists(dbFile):
        print("No high score file.")
        return

    try:
        (conn, cursor) = utils.openDatabase(dbFile)

        level: Optional[int] = None
        algorithm: Optional[str] = None

        cheat = bool(args.showpath or args.showmaze or args.cheat)

        if args.level:
            level = args.level[0]
        
        sql = ("select gameid,timestamp,score,level,algorithm,player_name,"
              "elapsed_secs,moves,shortest_path_moves,cheat,version,braid,"
              "replay_of_gameid from highscores")
        
        if level is not None:
            sql += f" where level={level}"
            sql += " and "
        else:
            sql += " where "
        
        if cheat:
            sql += " (cheat=0 or cheat=1)"
        else:
            sql += " cheat=0"
        
        if algorithm is not None:
            sql += f" and algorithm='{algorithm}'"

        sql += " order by score desc"
        
        scores: List[List[Any]] = []
        rank = 1
        scores.append(["RANK", "SCORE", "LEVEL", "GAMEID", "ALGORITHM",
                      "MOVES", "ELAPSED SECS", "VERSION", "TIME"])
        
        for row in cursor.execute(sql):
            scoreRow: List[Any] = []
            scoreRow.append(rank)
            rank += 1
            cheat_flag = row['cheat']
            score_val = row['score']
            if cheat_flag == 1:
                score_val = f"{score_val} (cheat)"
            scoreRow.append(score_val)
            scoreRow.append(row['level'])
            scoreRow.append(row['gameid'])
            scoreRow.append(f"{row['algorithm']}")
            scoreRow.append(f"{row['moves']}/{row['shortest_path_moves']}")
            scoreRow.append(row['elapsed_secs'])
            scoreRow.append(row['version'])
            scoreRow.append(row['timestamp'])
            scores.append(scoreRow)

        # Print formatted output
        rankColumnWidth = 5
        columnWidth = 17
        
        # Header
        output = [scores[0][0].ljust(rankColumnWidth), " "]
        for c in scores[0][1:]:
            output.append(str(c).ljust(columnWidth))
            output.append(" ")
        print("".join(output))
        
        # Separator
        output = ["-" * rankColumnWidth, " "]
        for _ in scores[0][1:]:
            output.append("-" * columnWidth)
            output.append(" ")
        print("".join(output))
        
        # Data rows
        for row in scores[1:]:
            output = []
            first = True
            for c in row:
                s = str(c)
                if first:
                    output.append(s.ljust(rankColumnWidth))
                    first = False
                else:
                    output.append(s.ljust(columnWidth))
                output.append(" ")
            print("".join(output))
        
        utils.closeDatabase(conn)
        logger.debug(f"Listed {len(scores)-1} high scores")
    except Exception as e:
        logger.error(f"Error listing high scores: {e}")
        print(f"Error displaying high scores: {e}")
