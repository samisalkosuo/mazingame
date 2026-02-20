"""Basic tests for mazingame."""
import pytest


def test_version():
    """Test that version is accessible."""
    from mazingame.mazingame import __version__
    assert __version__ == "1.7.0"


def test_imports():
    """Test that main modules can be imported."""
    from mazingame import mazingame
    from mazingame import gameclasses
    from mazingame import highscores
    from mazingame import GameScreen
    from mazingame import globals
    
    assert mazingame is not None
    assert gameclasses is not None
    assert highscores is not None
    assert GameScreen is not None
    assert globals is not None


def test_player_class():
    """Test Player class initialization."""
    from mazingame.gameclasses import Player
    
    player = Player("TestPlayer")
    assert player.name == "TestPlayer"


def test_goal_class():
    """Test Goal class initialization."""
    from mazingame.gameclasses import Goal
    
    goal = Goal(10, 20, 5, 15)
    assert goal.row == 10
    assert goal.column == 20
    assert goal.screenRow == 5
    assert goal.screenColumn == 15


# Placeholder for more comprehensive tests
# These will need to be expanded based on actual game logic

# Made with Bob
