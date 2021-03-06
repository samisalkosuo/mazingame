## Version 1.7 (22.02.2018)

- Removed --view option. --replay now replays game. 
- Removed --algorithm and --braid options. 

## Version 1.6 (13.02.2018)

- Changed data dir /mazingame/gamedata to /data.
- Refactoring. Moved code to files.

## Version 1.5 (12.02.2018)

- Added -nf, --nofullscreen option to disable full screen.
- Removed -f, --fulscreen option. Default is now full screen.
- Now checks if console is big enough for full screen.
- Added -l, --level argument to specify level. Level is
  the random seed to create the maze.
- Refactored to be run primarily as Docker image.

## Version 1.4 (09.02.2018)

- Added Docker distribution.
- pip-distribution no longer actively maintained.

## Version 1.3 (05.07.2016)

- Requires mazepy v0.3.
- Bug fix when viewing game replays.

## Version 1.2 (15.06.2016)

- Requires mazepy v0.2.
- Added braiding mazes.
- Removed --level option.
- Added --view option to view replay of existing game.
- Changed --replay option so that you can play the maze again.
- Refactoring.

## Version 1.1.0 (13.06.2016)

- Moved to Python3 (Python2 no longer supported).
- Added Hunt And Kill-algorithm.
- Removed base maze classes and functions.
- And added dependency to mazepy-project, that includes
  base maze classes and functions.

## Version 1.0.0 (03.01.2016)

- Pip distribution.

## Version 0.4 (29.12.2015)

- Added Aldous Broder-algorithm.
- Added Wilson's algorithm.

## Version 0.3 (17.09.2015)

- Added --showmaze option to show entire maze (this is cheating).
- Changed high score file format.
- Added --cheat option to show cheat high scores.
- Added Sidewinder-algorithm.

## Version 0.2 (07.09.2015)

- Added Binary Tree algorithm.
- Algorithm and version info into high scores.

## Version 0.1 (23.08.2015)

- Initial version.
