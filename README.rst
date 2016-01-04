MazinGame
=========
A game of maze.

Idea of the game is to find a path through the maze to spot marked by 'X'.


Requirements
------------

Python 2.7 with curses. Does not work with Python3. Tested with Cygwin and 
Mac OS X.

Install
-------

Install latest version: *pip install mazingame*


Instructions
------------

You will start at some location in the bottom of the maze. 'X' is somewhere
nearer the top of the maze.
Move using cursor keys or 'w','a','s','d'.
Quit pressing 'q' or Ctrl-C.

When, or if, you reach 'X', the ending score is saved to SQLite database.
The default highscore file location is $HOME/.mazingame_highscores.sqlite.
Use environment variable MAZINGAME_HIGHSCORE_FILE to set another file.

Command line options include:
	-f, --fullscreen      Use terminal to show entire maze. But only if terminal size is larger than the maze.
	--showpath            Show shortest path. Remember: this is cheating.
	--showmaze            Show entire maze. Remember: this is cheating.
	-hs, --highscores     Show high scores.

And a few more.

Note: database in high score file may change from version to version, if you
get SQLite error when saving high scores, delete your high score file.


About
-----

This hobby project was inspired by the book "Mazes for Programmers" by Jamis Buck
(https://pragprog.com/book/jbmaze/mazes-for-programmers).

See http://sami.salkosuo.net/mazingame/ for some background about MazinGame.
