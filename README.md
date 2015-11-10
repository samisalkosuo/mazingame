# MazinGame

A game of maze.
Inspired by book "Mazes for Programmers" by Jamis Buck
(https://pragprog.com/book/jbmaze/mazes-for-programmers).
Idea of the game is to find a path through the maze to spot marked by 'X'.

========================================================================
Start MazinGame using command: python mazingame.py.

You will start at some location in the bottom of the maze. 'X' is somewhere
upper. Move using cursor keys or 'w','a','s','d'.
Quit pressing 'q' or Ctrl-C.

When, or if, you reach 'X', the ending score is saved to SQLite database.
The default highscore file location is $HOME/.mazingame_highscores.sqlite.
Use environment variable MAZINGAME_HIGHSCORE_FILE to set another file.
Note: database in high score file may change from version to version, if you
get SQLite error when saving high scores, delete your high score file.

See http://sami.salkosuo.net/mazingame/ for some background about MazinGame.

========================================================================
```
usage: mazingame.py [-h] [-l LEVEL] [-r GAMEID] [-a {BT,S,AB,RB}] [-f]
                    [--showpath] [--showmaze] [-hs] [--cheat] [-v]

MazinGame. A game of maze.

optional arguments:
  -h, --help            show this help message and exit
  -l LEVEL, --level LEVEL
                        Choose level. Any integer.
  -r GAMEID, --replay GAMEID
                        Replay game with specified id.
  -a {BT,S,AB,RB}, --algorithm {BT,S,AB,RB}
                        Choose maze algorithm: BT=Binary
                        Tree,S=Sidewinder,AB=Aldous Broder,RB=Recursive
                        Backtracker. Default is random.
  -f, --fullscreen      Use terminal to show entire maze. But only if terminal
                        size is larger than the maze.
  --showpath            Show shortest path. Remember: this is cheating.
  --showmaze            Show entire maze. Remember: this is cheating.
  -hs, --highscores     Show high scores. Specify --level to select scores for
                        the level and --showpath to incude cheat scores. Use
                        MAZINGAME_HIGHSCORE_FILE environment variable to set
                        high score file (default is
                        $HOME/.mazingame_highscores.sqlite).
  --cheat               Show also cheat highscores.
  -v, --version         Show version info.
```
