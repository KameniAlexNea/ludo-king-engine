"""
Ludo Core Engine - A pure Python implementation of Ludo game.

This package provides a deterministic Ludo game engine designed for
reinforcement learning and strategy testing. It cleanly separates
game mechanics from strategies and requires no external libraries.
"""

from .core.game import LudoGame
from .core.board import Board
from .core.token import Token
from .core.player import Player
from .strategies.factory import StrategyFactory
from . import utils

__version__ = "1.0.0"
__author__ = "Ludo Engine Team"

__all__ = [
    "LudoGame",
    "Board", 
    "Token",
    "Player",
    "StrategyFactory",
    "utils"
]