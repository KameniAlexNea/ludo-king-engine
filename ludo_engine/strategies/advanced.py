"""
Advanced strategy implementations for Ludo.

This module contains more sophisticated strategy implementations
that use complex heuristics and probabilistic reasoning.
"""

from typing import List, Optional

from ..core.constants import HeuristicConstants, LudoConstants
from ..core.token import Token
from .base_strategy import BaseStrategy


class CautiousStrategy(BaseStrategy):
    """Very conservative strategy that minimizes risk."""

    def __init__(self):
        super().__init__("Cautious")

    def choose_move(
        self, movable_tokens: List[Token], dice_roll: int, game_state: dict
    ) -> Optional[Token]:
        """Choose most cautious move available."""
        if not movable_tokens:
            return None

        # Strongly prefer safe moves
        safe_moves = [
            t for t in movable_tokens if self.is_move_safe(t, dice_roll, game_state)
        ]

        if safe_moves:
            # Among safe moves, prefer tokens closer to home (less risk)
            return min(safe_moves, key=lambda t: t.steps_taken)

        # If no safe moves, choose token that's already furthest (least to lose)
        return max(movable_tokens, key=lambda t: t.steps_taken)


class OptimistStrategy(BaseStrategy):
    """Aggressive strategy that takes calculated risks."""

    def __init__(self):
        super().__init__("Optimist")

    def choose_move(
        self, movable_tokens: List[Token], dice_roll: int, game_state: dict
    ) -> Optional[Token]:
        """Choose aggressive move with potential for high reward."""
        if not movable_tokens:
            return None

        # Prioritize captures above all else
        for token in movable_tokens:
            opponents = self.get_opponent_tokens_in_range(token, dice_roll, game_state)
            if opponents:
                return token

        # No captures, prioritize advancing furthest
        return max(movable_tokens, key=lambda t: t.steps_taken + dice_roll)


class WinnerStrategy(BaseStrategy):
    """Focuses on getting tokens to finish as quickly as possible."""

    def __init__(self):
        super().__init__("Winner")

    def choose_move(
        self, movable_tokens: List[Token], dice_roll: int, game_state: dict
    ) -> Optional[Token]:
        """Choose move that best advances toward victory."""
        if not movable_tokens:
            return None

        # Prioritize tokens that can finish
        finishing_tokens = []
        for token in movable_tokens:
            if token.steps_taken + dice_roll >= LudoConstants.BOARD_SIZE:
                finishing_tokens.append(token)

        if finishing_tokens:
            # Choose token closest to finish
            return max(finishing_tokens, key=lambda t: t.steps_taken)

        # No finishing moves, prioritize most advanced token
        return max(movable_tokens, key=lambda t: t.steps_taken)


class ProbabilisticStrategy(BaseStrategy):
    """Uses probability calculations to make optimal decisions."""

    def __init__(self):
        super().__init__("Probabilistic")

    def choose_move(
        self, movable_tokens: List[Token], dice_roll: int, game_state: dict
    ) -> Optional[Token]:
        """Choose move based on probabilistic analysis."""
        if not movable_tokens:
            return None

        # Calculate expected value for each move
        best_token = None
        best_value = float("-inf")

        for token in movable_tokens:
            expected_value = self.calculate_expected_value(token, dice_roll, game_state)
            if expected_value > best_value:
                best_value = expected_value
                best_token = token

        return best_token

    def calculate_expected_value(
        self, token: Token, dice_roll: int, game_state: dict
    ) -> float:
        """Calculate expected value of moving this token."""
        value = 0.0

        # Base value for advancement
        new_position = token.steps_taken + dice_roll
        value += new_position * HeuristicConstants.ADVANCED_ADVANCEMENT_MULTIPLIER

        # High value for finishing
        if new_position >= LudoConstants.BOARD_SIZE:
            value += HeuristicConstants.ADVANCED_FINISH_BONUS

        # Value for captures
        opponents = self.get_opponent_tokens_in_range(token, dice_roll, game_state)
        value += len(opponents) * HeuristicConstants.ADVANCED_CAPTURE_BONUS

        # Cost of being captured (probability-based)
        capture_risk = self.calculate_capture_risk(token, dice_roll, game_state)
        value -= capture_risk * HeuristicConstants.ADVANCED_CAPTURE_RISK_PENALTY

        # Value for getting out of home
        if token.is_at_home() and dice_roll == 6:
            value += HeuristicConstants.ADVANCED_EXIT_HOME_BONUS

        return value

    def calculate_capture_risk(
        self, token: Token, dice_roll: int, game_state: dict
    ) -> float:
        """Calculate probability of being captured after this move."""
        if not token.can_move(dice_roll):
            return 0.0

        # Calculate new position
        new_position = token.position + dice_roll
        if token.is_at_home() and dice_roll == 6:
            new_position = LudoConstants.START_POSITIONS.get(token.color, 0)

        # Check if position is safe
        if self.is_move_safe(token, dice_roll, game_state):
            return 0.0

        # Count opponent tokens that could reach this position
        risk = 0.0
        board_state = game_state.get("board", {})

        for pos_str, tokens_data in board_state.items():
            position = int(pos_str)
            for token_data in tokens_data:
                if token_data["color"] != token.color:
                    # Check if opponent token could reach our new position
                    distance = new_position - position
                    if 1 <= distance <= 6:
                        # Probability that opponent rolls exactly this distance
                        risk += HeuristicConstants.PROBABILITY_PER_DISTANCE

        return min(
            risk, HeuristicConstants.MAX_CAPTURE_PROBABILITY
        )  # Cap at 100% probability
