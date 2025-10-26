"""
Constants and configuration values for the Ludo game.
Centralized location for all game rules and board layout constants.
"""

from typing import Dict, Set

from ludo_engine.models.model import PlayerColor


class GameConstants:
    """Core game constants and rules."""

    # Board dimensions
    MAIN_BOARD_SIZE = 52
    HOME_COLUMN_SIZE = 6
    TOKENS_PER_PLAYER = 4
    MAX_PLAYERS = 4

    # Dice
    DICE_MIN = 1
    DICE_MAX = 6
    EXIT_HOME_ROLL = 6

    # Win condition
    TOKENS_TO_WIN = 4

    # Special positions
    FINISH_POSITION = 105  # Final position in home column
    HOME_POSITION = -1  # Tokens start in home (-1)
    HOME_COLUMN_START = 100  # Start of home column positions


class BoardConstants(GameConstants):
    """Board layout and position constants."""

    # Star squares (safe for all players) - 0-indexed board
    STAR_SQUARES: Set[int] = {8, 21, 34, 47}

    # Starting positions for each color
    START_POSITIONS: Dict[PlayerColor, int] = {
        PlayerColor.RED: 1,
        PlayerColor.GREEN: 14,
        PlayerColor.YELLOW: 27,
        PlayerColor.BLUE: 40,
    }

    # Last position before entering home column for each color
    HOME_COLUMN_ENTRIES: Dict[PlayerColor, int] = {
        PlayerColor.RED: 51,  # Red enters home after position 51
        PlayerColor.GREEN: 12,  # Green enters home after position 12
        PlayerColor.YELLOW: 25,  # Yellow enters home after position 25
        PlayerColor.BLUE: 38,  # Blue enters home after position 38
    }

    # Home column positions (100 to 105)
    HOME_COLUMN_START = GameConstants.HOME_COLUMN_START
    HOME_COLUMN_END = GameConstants.FINISH_POSITION
    FINISH_POSITION = GameConstants.FINISH_POSITION

    # All safe squares (combination of star squares and colored squares)
    @classmethod
    def get_all_safe_squares(cls) -> Set[int]:
        """Get all safe squares on the board."""
        all_safe = cls.STAR_SQUARES.copy()
        all_safe.update(cls.START_POSITIONS.values())
        return all_safe

    @classmethod
    def is_home_column_position(cls, position: int) -> bool:
        """Check if a position is in any home column."""
        return cls.HOME_COLUMN_START <= position <= cls.HOME_COLUMN_END

    @classmethod
    def is_safe_position(cls, position: int, player_color: PlayerColor = None) -> bool:
        """
        Check if a position is safe.

        Args:
            position: Board position to check
            player_color: Optional player color for color-specific safe squares

        Returns:
            bool: True if position is safe
        """
        # Home columns are always safe
        if cls.is_home_column_position(position):
            return True

        # Star squares are safe for everyone
        if position in cls.STAR_SQUARES:
            return True

        # Starting positions (from START_POSITIONS) are safe for everyone
        if position in cls.START_POSITIONS.values():
            return True

        return False


class StrategyConstants:
    """Shared constants for AI strategy calculations."""

    # Strategic values
    FINISH_TOKEN_VALUE = 100.0
    HOME_COLUMN_ADVANCE_VALUE = 20.0
    EXIT_HOME_VALUE = 15.0
    CAPTURE_BONUS = 25.0
    SAFE_MOVE_BONUS = 5.0

    # Threat levels
    HIGH_THREAT_THRESHOLD = 0.7
    MODERATE_THREAT_THRESHOLD = 0.4

    # Player progress thresholds
    SIGNIFICANTLY_BEHIND_THRESHOLD = 0.25
    SIGNIFICANTLY_AHEAD_THRESHOLD = 0.25

    # Heuristic weights shared across strategies
    FORWARD_PROGRESS_WEIGHT = 1.0
    ACCELERATION_WEIGHT = 0.1
    SAFETY_BONUS = SAFE_MOVE_BONUS
    VULNERABILITY_PENALTY_WEIGHT = 8.0
    HOME_COLUMN_DEPTH_MULTIPLIER = 1.0


class KillerStrategyConstants(StrategyConstants):
    """Aggressive capture-first strategy tuning."""

    PROGRESS_WEIGHT = 2.0
    THREAT_WEIGHT = 1.5
    CHAIN_BONUS = 10.0
    SAFE_LAND_BONUS = 4.0
    BLOCK_BONUS = 6.0
    RECAPTURE_PENALTY = 12.0
    WEAK_PREY_PENALTY = 5.0
    FUTURE_CAPTURE_WEIGHT = 3.0


class CautiousStrategyConstants(StrategyConstants):
    """Risk-averse defensive strategy tuning."""

    MAX_ALLOWED_THREAT = 0
    LATE_GAME_ALLOWED_THREAT = 1
    MIN_ACTIVE_TOKENS = 2


class OptimistStrategyConstants(StrategyConstants):
    """High-variance aggressive strategy tuning."""

    HIGH_RISK_THRESHOLD = 10.0
    RISK_REWARD_BONUS = 4.0
    CAPTURE_PROGRESS_WEIGHT = 1.2
    FUTURE_CAPTURE_WEIGHT = 2.0
    EXIT_EARLY_ACTIVE_TARGET = 3
    STACK_BONUS = 2.5


class WinnerStrategyConstants(StrategyConstants):
    """Late-game finishing priorities."""

    HOME_DEPTH_WEIGHT = 1.0
    SAFE_CAPTURE_PROGRESS_WEIGHT = 1.0
    EXIT_MIN_ACTIVE = 1


class DefensiveStrategyConstants(StrategyConstants):
    """Structured defensive play tuning."""

    MIN_ACTIVE_TOKENS = 2
    BLOCK_FORMATION_BONUS = 6.0
    SAFE_CAPTURE_BONUS = 12.0
    HOME_DEPTH_WEIGHT = 0.9
    EXIT_PRESSURE_THRESHOLD = 3
    ALLOW_THREAT_DISTANCE = 2
    MAX_THREAT_COUNT = 1
    REPOSITION_BONUS = 2.5
    AVOID_BREAKING_BLOCK_PENALTY = 5.0


class BalancedStrategyConstants(StrategyConstants):
    """Balanced offence/defence tuning."""

    PROGRESS_WEIGHT = 1.1
    HOME_PRIORITY = 0.95
    SAFE_CAPTURE_WEIGHT = 1.3
    RISK_TOLERANCE_MARGIN = 0.15
    MIN_ACTIVE_TARGET = 2
    BLOCK_VALUE = 4.0
    FUTURE_CAPTURE_PROXIMITY = 5
    FUTURE_CAPTURE_WEIGHT = 1.5
    THREAT_SOFT_CAP = 2
    AHEAD_THREAT_CAP = 1
    LATE_GAME_FINISH_PUSH = 2


class HybridProbabilisticConstants(StrategyConstants):
    """Hybrid probabilistic evaluation constants."""

    IMMEDIATE_RISK_WEIGHT = 0.55
    PROXIMITY_REF = 7
    PROXIMITY_PENALTY_CAP = 6.0
    CLUSTER_INCREMENT = 0.15
    IMPACT_BASE = 0.5
    IMPACT_PROGRESS_POWER = 1.2
    PROGRESS_POWER = 1.4
    PROGRESS_SCALE = 3.0
    HOME_DEPTH_FACTOR = 2.0
    CAPTURE_BASE = 2.0
    EXTRA_TURN_COEFF = 2.2
    EXTRA_TURN_PROGRESS_NORM = 3.5 / GameConstants.MAIN_BOARD_SIZE
    FUTURE_SAFETY_BONUS = 0.2
    SPREAD_ACTIVE_TARGET = 2
    SPREAD_BONUS = 0.5
    RISK_SUPPRESSION_COEFF = 0.7
    FINISH_BONUS = 4.2
    ADVANCE_HOME_BONUS = 1.9
    EXIT_HOME_BONUS = 1.1
    SAFE_LANDING_BONUS = 1.0
    COMPOSITE_RISK_POWER = 1.05
    LATE_GAME_PROGRESS_MULT = 1.15
    EARLY_GAME_PROGRESS_MULT = 0.9
    LEAD_FACTOR_STRONG = 0.8
    BEHIND_FACTOR_STRONG = -0.8


class WeightedRandomStrategyConstants(StrategyConstants):
    """Temperature and weighting controls for weighted-random play."""

    TEMP_EARLY = 1.4
    TEMP_MID = 1.0
    TEMP_LATE = 0.7
    PHASE_EARLY = 0.25
    PHASE_LATE = 0.65
    EPSILON = 0.05
    DIVERSITY_LAMBDA = 0.15
    CAPTURE_BONUS = 0.4
    SAFE_BONUS = 0.2
    RISK_THREAT_CAP = 3
    RISK_PENALTY = 0.5
    MIN_WEIGHT = 1e-4
    DIVERSITY_MEMORY = 25
