"""
Ludo Core Engine - A pure Python implementation of Ludo game.

This package provides a deterministic Ludo game engine designed for
reinforcement learning and strategy testing. It cleanly separates
game mechanics from strategies and requires no external libraries.
"""

from . import utils
from .core.board import Board
from .core.game import LudoGame
from .core.player import Player
from .core.token import Token
from .strategies.factory import StrategyFactory

__version__ = "0.1.0"
__author__ = "KameniAlexNea"

__all__ = ["LudoGame", "Board", "Token", "Player", "StrategyFactory", "utils"]


def main():
    """Main entry point for the ludo-demo command."""
    print("Welcome to Ludo King Engine!")
    print("For a complete demo, run: python examples/tournament_demo.py")
    print("For Gradio interface, run: ludo-gradio")
