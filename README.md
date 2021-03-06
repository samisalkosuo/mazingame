# MazinGame

A game of maze.

Idea of the game is to find a path through the maze to a location marked by 'X'.

Snapshot from an actual game (if you are seeing this in pypi.python.org you may 
not see it correctly, so go to GitHub page to see it)::

	+   +   +   +   +   +   +   +   +---+   +---+---+---+   +   +   +   +---+   +---+
	|   |   |   |   |   |   |   |       |                       |           |   |
	+   +   +---+   +   +   +   +---+   +---+---+   +---+---+   +---+   +   +   +   +
	|   |     X |   |   |   |       |   |       |       |       |       |   |
	+---+---+   +   +   +   +---+   +   +---+   +---+   +   +---+   +---+   +   +---+
	| .   .   @ |       |       |   |       |   |       |       |   |       |       |
	+   +---+---+---+   +   +   +   +---+   +   +   +---+   +---+   +   +   +---+   +
	| .             |       |   |       |   |       |               |           |   |
	+   +---+   +   +---+---+   +   +   +   +---+---+   +---+---+   +---+---+   +   +
	| .   . |   |               |   |       |       |           |   |           |
	+---+   +   +---+---+---+---+   +---+---+   +   +---+---+   +   +   +---+---+---+
	| .   . |           |       |   |       |   |   |           |       |
	+   +---+---+   +   +   +   +   +   +---+   +   +   +---+---+   +---+   +   +---+
	| . |           |       |   |   |   |       |   |   |       |           |
	+   +   +---+---+---+   +   +   +   +   +---+   +   +---+   +---+---+   +---+   +
	| . |       |       |   |   |   |   |   |       |               |       |       |
	+   +---+   +   +   +   +   +   +   +   +   +---+---+---+---+---+   +---+   +---+
	| .   .   . |   |   |       |       |   |           |       |       |           |
	+---+---+   +   +   +---+   +   +---+   +---+---+   +   +   +   +---+   +   +   +
	| .   . | . |   |       |   |           |   |       |   |       |   |       |
	+   +   +   +---+---+   +   +---+---+   +   +   +   +   +---+---+   +---+---+---+
	| . | . | .   .   . |       |           |           |           |   |           |
	+   +   +---+---+   +---+---+   +---+---+   +---+---+   +---+   +   +   +---+   +
	P: (9,2) X: (8,2) Moves: 35/36 Elapsed: 12.670secs Score: 8288

## Requirements

[Docker runtime](https://www.docker.com/get-docker). If you ask why? Because it makes distribution simple and life easier :-).

If using sources, Python 3.x with curses and [mazepy](https://github.com/samisalkosuo/mazepy). Does not work with Python2 or Windows without Cygwin.

## Install and usage - Docker

Install from Dockerhub:

- docker pull kazhar/mazingame

Using docker image:

- Run using command:
  - *docker run -it --rm kazhar/mazingame [options]*

- Set your own directory for highscore/game replay file:
  - *docker run -it --rm -v &lt;path_to_local_dir>:/data kazhar/mazingame [options]*

About options:

- *-it* runs Docker container with interactive terminal.
- *--rm* removes image after use. No need to keep it.
- *-v* maps local directory to directory used by the program.

## Install and usage - pip

There is a version in pip. Install from pip:

- **pip install mazingame**.

Note that this is not regularly updated.

## Instructions

You will start at some location in the bottom of the maze. 'X' is somewhere
nearer the top of the maze.

- Move using cursor keys or 'w', 'a', 's', 'd'.
- Quit pressing 'q' or Ctrl-C.

When, or if, you reach 'X', the ending score is saved to SQLite database */data/mazingame_highscores.sqlite*.
Use Docker volume to point */data* to your own directory.

Command line options include:

- -f, --fullscreen      Use terminal to show entire maze. But only if terminal size is larger than the maze.
- --showpath            Show shortest path. Remember: this is cheating.
- --showmaze            Show entire maze. Remember: this is cheating.
- -hs, --highscores     Show high scores.

And a few more.

Note: database in high score file may change from version to version, if you
get SQLite error when saving high scores, delete your high score file.

## About

This hobby project was inspired by the book ["Mazes for Programmers" by Jamis Buck](https://pragprog.com/book/jbmaze/mazes-for-programmers).

Python translations of the maze code is in [mazepy-project](https://github.com/samisalkosuo/mazepy).

See [http://sami.salkosuo.net/mazingame/](http://sami.salkosuo.net/mazingame/) for some background about MazinGame.
