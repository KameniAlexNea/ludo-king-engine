"""
Base strategy class for Ludo game AI.

This module defines the abstract base class that all strategy implementations
must inherit from. It provides the interface for making move decisions.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from ..core.model import GameStateData
    from ..core.player import Player
    from ..core.token import Token

from ..core.constants import LudoConstants


class BaseStrategy(ABC):
    """
    Abstract base class for all Ludo game strategies.

    Strategies are responsible for making move decisions given the current
    game state and available options.
    """

    def __init__(self, name: str):
        """
        Initialize the strategy.

        Args:
            name: Human-readable name for this strategy
        """
        self.name = name
        self.player: Optional["Player"] = None

    def set_player(self, player: "Player"):
        """
        Set the player that this strategy is controlling.

        Args:
            player: The player this strategy will make decisions for
        """
        self.player = player

    @abstractmethod
    def choose_move(
        self, movable_tokens: List["Token"], dice_roll: int, game_state: "GameStateData"
    ) -> Optional["Token"]:
        """
        Choose which token to move from the available options.

        Args:
            movable_tokens: List of tokens that can be moved
            dice_roll: The dice roll value (1-6)
            game_state: Current game state (GameStateData object)

        Returns:
            The token to move, or None if no move should be made
        """

    def evaluate_move(self, token: "Token", dice_roll: int, game_state: "GameStateData") -> float:
        """
        Evaluate the desirability of moving a specific token.

        Args:
            token: The token to evaluate
            dice_roll: The dice roll result
            game_state: Current game state

        Returns:
            Score representing how good this move is (higher = better)
        """
        # Default implementation - override in subclasses for better evaluation
        return 1.0

    def get_opponent_tokens_in_range(
        self, token: "Token", dice_roll: int, game_state: "GameStateData"
    ) -> List["Token"]:
        """
        Get opponent tokens that could be captured by this move.

        Args:
            token: The token making the move
            dice_roll: The dice roll result
            game_state: Current game state

        Returns:
            List of opponent tokens that could be captured
        """
        if not token.can_move(dice_roll):
            return []

        # Calculate new position after move
        new_position = token.position + dice_roll
        if token.is_at_home() and dice_roll == 6:
            # Moving from home
            new_position = LudoConstants.START_POSITIONS.get(token.color, 0)
        elif new_position >= LudoConstants.BOARD_SIZE:
            return []  # Moving to finish, no captures possible

        # Check game state for opponent tokens at new position
        board_state = game_state.board
        tokens_at_position = board_state.get(str(new_position), [])

        opponent_tokens = []
        for token_data in tokens_at_position:
            if token_data["color"] != token.color:
                # Create a temporary token object for evaluation
                from ..core.token import Token

                opponent_token = Token.from_dict(token_data)
                opponent_tokens.append(opponent_token)

        return opponent_tokens

    def is_move_safe(self, token: "Token", dice_roll: int, game_state: "GameStateData") -> bool:
        """
        Check if a move would leave the token in a safe position.

        Args:
            token: The token making the move
            dice_roll: The dice roll result
            game_state: Current game state

        Returns:
            True if the move is safe, False otherwise
        """
        if not token.can_move(dice_roll):
            return False

        # Calculate new position
        new_position = token.position + dice_roll
        if token.is_at_home() and dice_roll == 6:
            new_position = LudoConstants.START_POSITIONS.get(token.color, 0)

        # Safe positions where tokens cannot be captured
        return (
            new_position in LudoConstants.SAFE_POSITIONS
            or new_position >= LudoConstants.BOARD_SIZE
        )

    def count_tokens_ahead(self, token: "Token", game_state: "GameStateData") -> int:
        """
        Count how many of player's own tokens are ahead of this token.

        Args:
            token: The token to check
            game_state: Current game state

        Returns:
            Number of own tokens ahead
        """
        if not self.player:
            return 0

        count = 0
        for other_token in self.player.tokens:
            if other_token != token and other_token.steps_taken > token.steps_taken:
                count += 1

        return count

    def __repr__(self) -> str:
        """String representation of the strategy."""
        return f"{self.__class__.__name__}('{self.name}')"
