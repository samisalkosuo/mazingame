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

import os
from .utils import utils
from .globals import *


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

def getMazeInfo(gameId):
    dbFile=getHighScoreFile()

    (conn,cursor)=utils.openDatabase(dbFile)
    cursor.execute("select maze_json,player_row,player_column,goal_row,goal_column from mazes where gameid=%d" % gameId)
    row=cursor.fetchone()
    result=dict()
    result["maze_json"]=row["maze_json"]
    result["player_row"]=row["player_row"]
    result["player_column"]=row["player_column"]
    result["goal_row"]=row["goal_row"]
    result["goal_column"]=row["goal_column"]
    utils.closeDatabase(conn)

    return result

def getHighScoreFile():
    dbFile=os.environ.get(MAZINGAME_HIGHSCORE_FILE)
    if dbFile==None:
        from os.path import expanduser
        HOMEDIR = expanduser("~")
        dbFile="%s/%s" % (HOMEDIR,DEFAULT_MAZINGAME_HIGHSCORE_FILE)
    #utils.debug(dbFile)
    return dbFile


def saveScores(args,version,grid,player,goal,level,score,moves,shortestPath,elapsed,cheat,algorithm,braid):
    #TODO: change high score file to text file and use inmemory sqlite to show scores
    #similar to CLI Password Manager

    #do not save score if viewing replay
    if args.view:
        return

    dbFile=getHighScoreFile()

    timestamp=utils.currentTimeISO8601()
    (conn,cursor)=utils.openDatabase(dbFile)

    #SQLite uses boolean value '1' for true and '0' false
    cursor.execute('''CREATE TABLE IF NOT EXISTS highscores (gameid integer primary key autoincrement, timestamp text, score integer, level integer, algorithm text, player_name text, elapsed_secs real,moves integer, shortest_path_moves integer,cheat integer,version text,braid real,replay_of_gameid integer)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS gamemoves (gameid integer, move_index integer, row integer, column integer)''')

    if args.replay:
        replaygameid=args.replay[0]
    else:
        replaygameid=0
    values = (timestamp,score,level,elapsed,moves,shortestPath,cheat,player.name,algorithm,version,braid,replaygameid)
    cursor.execute('insert into highscores (timestamp,score,level,elapsed_secs,moves,shortest_path_moves,cheat,player_name,algorithm,version,braid,replay_of_gameid) values (?,?,?,?,?,?,?,?,?,?,?,?)', values)
    #save player moves for replay
    values= (timestamp,)
    cursor.execute("select gameid from highscores where timestamp=?",values)
    gameid=cursor.fetchone()[0]

    #save maze
    mazeJSON=grid.toJSONString()
    cursor.execute('''CREATE TABLE IF NOT EXISTS mazes (gameid integer,player_row integer,player_column integer, goal_row integer, goal_column integer, maze_json text)''')
    values= (gameid, player.startingRow,player.startingColumn,goal.row,goal.column,mazeJSON)
    cursor.execute('insert into mazes (gameid,player_row, player_column,goal_row,goal_column, maze_json) values (?,?,?,?,?,?)', values)

    moveIndex=0

    for cell in player.visitedCells:
        values = (gameid,moveIndex,cell.row,cell.column)
        cursor.execute('insert into gamemoves (gameid,move_index,row,column) values (?,?,?,?)', values)
        moveIndex=moveIndex+1

    conn.commit()
    utils.closeDatabase(conn)
    return gameid

def selectFromHighScores(gameid, columnName):
    dbFile=getHighScoreFile()
    (conn,cursor)=utils.openDatabase(dbFile)

    sql="select %s from highscores where gameid=%d" % (columnName,gameid)
    result=None
    for row in cursor.execute(sql):
        result=row[columnName]

    utils.closeDatabase(conn)
    return result

def listHighScores(args):
    dbFile=getHighScoreFile()
    (conn,cursor)=utils.openDatabase(dbFile)

    level=None
    algorithm=None

    cheat=False
    if args.showpath or args.showmaze or args.cheat:
        cheat=True

    #if args.level:
    #    level=args.level[0]
    if args.algorithm:
        algorithm=args.algorithm[0]
    
    values= None
    #sql="select gameid,timestamp,score,level,algorithm,player_name,elapsed_secs,moves,shortest_path_moves,cheat,version,braid from highscores"
    sql="select gameid,timestamp,score,algorithm,player_name,elapsed_secs,moves,shortest_path_moves,cheat,version,braid,replay_of_gameid from highscores"
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
    #scores.append(["RANK","SCORE","LEVEL","ALGORITHM/BRAID","MOVES","ELAPSED SECS","GAMEID","PLAYER","VERSION","TIME"])
    scores.append(["RANK","SCORE","GAMEID (REPL. OF)","ALGORITHM/BRAID","MOVES","ELAPSED SECS","PLAYER","VERSION","TIME"])
    for row in cursor.execute(sql):
        scoreRow=[]
        scoreRow.append(rank)
        rank=rank+1
        cheat=row['cheat']
        score=row['score']
        if cheat==1:
            score="%d (cheat)" % score
        scoreRow.append(score)
        replaygameid=row['replay_of_gameid']
        if replaygameid!=0:
            scoreRow.append("%d (%d)" % (row['gameid'],replaygameid))
        else:
            scoreRow.append(row['gameid'])
        #scoreRow.append(row['level'])
        scoreRow.append("%s/%s" % (row['algorithm'], row['braid']))
        scoreRow.append("%d/%d" % (row['moves'],row['shortest_path_moves']))
        scoreRow.append(row['elapsed_secs'])
        scoreRow.append(row['player_name'])
        scoreRow.append(row['version'])
        scoreRow.append(row['timestamp'])
        scores.append(scoreRow)

    output=[]

    rankColumnWidth=5
    output.append(scores[0][0].ljust(rankColumnWidth))
    output.append(" ")
    columnWidth=17
    for c in scores[0][1:]:
        s=str(c)
        output.append(s.ljust(columnWidth))
        output.append(" ")
    print("".join(output))
    output=[]
    output.append("-"*rankColumnWidth)
    output.append(" ")
    columnWidth=17
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
