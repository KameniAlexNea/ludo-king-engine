"""
Board representation for Ludo game.
Manages the game board state and validates moves.
"""

from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ludo_engine.core.player import Player, Token, TokenState
from ludo_engine.models import (
    BoardConstants,
    BoardPositionInfo,
    BoardState,
    GameConstants,
    PlayerColor,
    PositionInfo,
)

_HOME_COLUMN_RANGE = range(
    BoardConstants.HOME_COLUMN_START, BoardConstants.HOME_COLUMN_END + 1
)


@dataclass(frozen=True)
class Position:
    """Lightweight representation of a board position for compatibility."""

    index: int
    is_safe: bool
    is_star: bool
    color: Optional[PlayerColor] = None


class Board:
    """
    Represents the Ludo game board and manages token positions.
    """

    def __init__(self):
        """Initialize board state and precompute convenience lookups."""
        self.start_positions = BoardConstants.START_POSITIONS
        self.home_entries = BoardConstants.HOME_COLUMN_ENTRIES
        self.safe_positions = BoardConstants.get_all_safe_squares()
        self.star_positions = set(BoardConstants.STAR_SQUARES)
        self.colored_square_lookup = {
            start: color for color, start in self.start_positions.items()
        }

        self.positions: Dict[int, Position] = {
            index: Position(
                index=index,
                is_safe=BoardConstants.is_safe_position(index),
                is_star=index in self.star_positions,
                color=self.colored_square_lookup.get(index),
            )
            for index in range(GameConstants.MAIN_BOARD_SIZE)
        }
        self.positions.update(
            {
                index: Position(index=index, is_safe=True, is_star=False)
                for index in _HOME_COLUMN_RANGE
            }
        )

        self.token_positions: Dict[int, List[Token]] = {}
        self.reset_token_positions()

    def reset_token_positions(self):
        """Reset all token position tracking."""
        self.token_positions = {
            **{index: [] for index in range(GameConstants.MAIN_BOARD_SIZE)},
            **{index: [] for index in _HOME_COLUMN_RANGE},
        }

    def add_token(self, token: Token, position: int):
        """Add a token to a specific position on the board."""
        if position not in self.token_positions:
            self.token_positions[position] = []

        self.token_positions[position].append(token)

    def remove_token(self, token: Token, position: int):
        """Remove a token from a specific position on the board."""
        if position in self.token_positions and token in self.token_positions[position]:
            self.token_positions[position].remove(token)

    def get_tokens_at_position(self, position: int) -> List[Token]:
        """Get all tokens at a specific position."""
        return self.token_positions.get(position, [])

    def is_position_safe(self, position: int, player_color: PlayerColor) -> bool:
        """Check if a position is safe for a given player color."""
        return BoardConstants.is_safe_position(position, player_color)

    @staticmethod
    def _has_blocking_stack(tokens: List[Token]) -> bool:
        """Return True if any color has two or more tokens at the position."""
        return any(
            count >= 2
            for count in Counter(token.player_color for token in tokens).values()
        )

    @staticmethod
    def _partition_tokens(
        player_color: PlayerColor, tokens: List[Token]
    ) -> Tuple[List[Token], List[Token]]:
        """Split tokens into friendly and opponent groups."""
        same_color = [token for token in tokens if token.player_color == player_color]
        opponents = [token for token in tokens if token.player_color != player_color]
        return same_color, opponents

    def can_move_to_position(
        self, token: Token, target_position: int
    ) -> Tuple[bool, List[Token]]:
        """Check if a token can move to a target position."""
        tokens_at_target = self.get_tokens_at_position(target_position)
        if not tokens_at_target:
            return True, []

        if self.is_position_safe(target_position, token.player_color):
            return True, []

        _, opponent_tokens = self._partition_tokens(
            token.player_color, tokens_at_target
        )

        if opponent_tokens and self._has_blocking_stack(opponent_tokens):
            return False, []

        return True, opponent_tokens

    def execute_move(
        self, token: Token, old_position: int, new_position: int
    ) -> List[Token]:
        """Execute a move on the board and return any captured tokens."""
        if old_position >= 0:
            self.remove_token(token, old_position)

        can_move, tokens_to_capture = self.can_move_to_position(token, new_position)
        if not can_move:
            if old_position >= 0:
                self.add_token(token, old_position)
            return []

        captured_tokens: List[Token] = []
        for captured in tokens_to_capture:
            self.remove_token(captured, new_position)
            captured.state = TokenState.HOME
            captured.position = GameConstants.HOME_POSITION
            captured_tokens.append(captured)

        self.add_token(token, new_position)
        return captured_tokens

    def get_board_state_for_ai(self, current_player: Player) -> BoardState:
        """
        Get the current board state in a format suitable for AI analysis.

        Args:
            current_player: The player whose turn it is

        Returns:
            BoardState: Complete board state information
        """
        board_positions = {
            position: [
                BoardPositionInfo(
                    player_color=token.player_color,
                    token_id=token.token_id,
                    state=token.state.value,
                )
                for token in tokens
            ]
            for position, tokens in self.token_positions.items()
            if tokens
        }

        safe_positions = sorted(self.safe_positions | set(_HOME_COLUMN_RANGE))

        return BoardState(
            current_player=current_player.color,
            board_positions=board_positions,
            safe_positions=safe_positions,
            star_positions=sorted(self.star_positions),
            player_start_positions=self.start_positions,
            home_column_entries=self.home_entries,
        )

    def get_position_info(self, position: int) -> PositionInfo:
        """Get detailed information about a specific position."""
        if position == GameConstants.HOME_POSITION:
            return PositionInfo(type="home", position=position, is_safe=True, tokens=[])

        tokens = [token.to_dict() for token in self.get_tokens_at_position(position)]

        if BoardConstants.is_home_column_position(position):
            return PositionInfo(
                type="home_column", position=position, is_safe=True, tokens=tokens
            )

        if 0 <= position < GameConstants.MAIN_BOARD_SIZE:
            return PositionInfo(
                type="main_board",
                position=position,
                is_safe=BoardConstants.is_safe_position(position),
                is_star=position in self.star_positions,
                color=self.colored_square_lookup.get(position),
                tokens=tokens,
            )

        # @TODO: Log warning about invalid position
        return PositionInfo(type="unknown", position=position, is_safe=False, tokens=[])

    def update_token_position(self, token: Token, old_position: int, new_position: int):
        """Update token position tracking on the board."""
        if old_position >= 0:
            self.remove_token(token, old_position)
        if new_position >= 0:
            self.add_token(token, new_position)

    def __str__(self) -> str:
        """String representation of the board state."""
        lines = [
            f"Position {position}: {[str(token) for token in tokens]}"
            for position, tokens in sorted(self.token_positions.items())
            if tokens and 0 <= position < GameConstants.MAIN_BOARD_SIZE
        ]
        board_snapshot = "\n".join(lines)
        return f"Board State:\n{board_snapshot}"
