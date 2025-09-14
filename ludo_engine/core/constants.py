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


class HeuristicConstants:
    """Constants for heuristic strategy evaluation scoring."""

    # Heuristic strategy constants
    HEURISTIC_ADVANCEMENT_MULTIPLIER = 0.1
    HEURISTIC_CAPTURE_BONUS = 10.0
    HEURISTIC_SAFE_MOVE_BONUS = 5.0
    HEURISTIC_EXIT_HOME_BONUS = 15.0
    HEURISTIC_FINISH_BONUS = 20.0
    HEURISTIC_VULNERABILITY_PENALTY = 2.0

    # Advanced strategy evaluation constants
    ADVANCED_ADVANCEMENT_MULTIPLIER = 0.5
    ADVANCED_FINISH_BONUS = 100.0
    ADVANCED_CAPTURE_BONUS = 25.0
    ADVANCED_CAPTURE_RISK_PENALTY = 15.0
    ADVANCED_EXIT_HOME_BONUS = 30.0

    # Capture risk calculation constants
    PROBABILITY_PER_DISTANCE = 1.0 / 6.0
    MAX_CAPTURE_PROBABILITY = 1.0
