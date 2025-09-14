"""
Constants for the Ludo game engine.

This module contains all game-related constants used throughout the engine.
"""


class LudoConstants:
    """Constants for the Ludo game board and gameplay."""

    # Standard Ludo board has 56 positions in the main track
    BOARD_SIZE = 56

    # Safe positions where tokens cannot be captured
    SAFE_POSITIONS = {1, 9, 14, 22, 28, 35, 42, 48}

    # Starting positions for each color
    START_POSITIONS = {"red": 0, "blue": 14, "green": 28, "yellow": 42}

    # Home stretch positions for each color (last 6 positions before finish)
    HOME_STRETCH_START = {"red": 50, "blue": 8, "green": 22, "yellow": 36}
