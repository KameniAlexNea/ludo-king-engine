"""
Base strategy classes and interfaces for Ludo AI.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ludo_engine.model import AIDecisionContext, ValidMove


class Strategy(ABC):
    """
    Abstract base class for Ludo AI strategies.
    Each strategy implements a different playing style.
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def decide(self, game_context: AIDecisionContext) -> int:
        """
        Make a strategic decision based on game context.

        Args:
            game_context: Complete game state and available moves

        Returns:
            int: token_id to move (0-3)
        """
        pass

    def _get_valid_moves(self, game_context: AIDecisionContext) -> List[ValidMove]:
        """Helper to get valid moves from context."""
        return game_context.valid_moves

    def _get_move_by_type(
        self, valid_moves: List[ValidMove], move_type: str
    ) -> Optional[ValidMove]:
        """Get first move of specified type."""
        for move in valid_moves:
            if move.move_type == move_type:
                return move
        return None

    def _get_moves_by_type(
        self, valid_moves: List[ValidMove], move_type: str
    ) -> List[ValidMove]:
        """Get all moves of specified type."""
        return [move for move in valid_moves if move.move_type == move_type]

    def _get_capture_moves(self, valid_moves: List[ValidMove]) -> List[ValidMove]:
        """Get all moves that capture opponents."""
        return [move for move in valid_moves if move.captures_opponent]

    def _get_safe_moves(self, valid_moves: List[ValidMove]) -> List[ValidMove]:
        """Get all safe moves."""
        return [move for move in valid_moves if move.is_safe_move]

    def _get_risky_moves(self, valid_moves: List[ValidMove]) -> List[ValidMove]:
        """Get all risky moves."""
        return [move for move in valid_moves if not move.is_safe_move]

    def _get_highest_value_move(
        self, valid_moves: List[ValidMove]
    ) -> Optional[ValidMove]:
        """Get move with highest strategic value."""
        if not valid_moves:
            return None
        return max(valid_moves, key=lambda m: m.strategic_value)

    def _get_lowest_value_move(
        self, valid_moves: List[ValidMove]
    ) -> Optional[ValidMove]:
        """Get move with lowest strategic value."""
        if not valid_moves:
            return None
        return min(valid_moves, key=lambda m: m.strategic_value)

    def __str__(self):
        return f"Strategy(name={self.name}, description={self.description})"

    def __repr__(self):
        return str(self)
