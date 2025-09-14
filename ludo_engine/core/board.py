"""
Board class representing the Ludo game board.

The board manages the layout, safe zones, and provides utilities
for token movement and position calculations.
"""

from typing import List, Optional, Tuple

from .token import Token


class Board:
    """
    Represents the Ludo game board.

    The board is a circular path with 56 positions (0-55), where each
    player has their own starting position and home stretch.
    """

    # Standard Ludo board has 56 positions in the main track
    BOARD_SIZE = 56

    # Safe positions where tokens cannot be captured
    SAFE_POSITIONS = {1, 9, 14, 22, 28, 35, 42, 48}

    # Starting positions for each color
    START_POSITIONS = {"red": 0, "blue": 14, "green": 28, "yellow": 42}

    # Home stretch positions for each color (last 6 positions before finish)
    HOME_STRETCH_START = {"red": 50, "blue": 8, "green": 22, "yellow": 36}

    def __init__(self):
        """Initialize the game board."""
        # Track which tokens are at each position
        self.positions: List[List[Token]] = [
            [] for _ in range(self.BOARD_SIZE + 1)
        ]  # +1 for finish
        self.safe_positions = self.SAFE_POSITIONS.copy()

    def is_safe_position(self, position: int) -> bool:
        """Check if a position is safe from capture."""
        return position in self.safe_positions

    def get_tokens_at_position(self, position: int) -> List[Token]:
        """Get all tokens at a specific position."""
        if 0 <= position <= self.BOARD_SIZE:
            return self.positions[position].copy()
        return []

    def place_token(self, token: Token, position: int) -> bool:
        """
        Place a token at a specific position.

        Args:
            token: The token to place
            position: Board position (0-56, where 56 is finish)

        Returns:
            True if placement was successful
        """
        if not (0 <= position <= self.BOARD_SIZE):
            return False

        # Remove token from its current position if it's on the board
        self.remove_token(token)

        # Add token to new position
        self.positions[position].append(token)
        token.position = position

        return True

    def remove_token(self, token: Token):
        """Remove a token from the board."""
        for position_tokens in self.positions:
            if token in position_tokens:
                position_tokens.remove(token)
                break

    def move_token(self, token: Token, steps: int) -> Tuple[bool, List[Token]]:
        """
        Move a token by the specified number of steps.

        Args:
            token: The token to move
            steps: Number of steps to move

        Returns:
            Tuple of (success, captured_tokens)
        """
        if not token.can_move(steps):
            return False, []

        # Calculate new position
        if token.is_at_home():
            if steps == 6:
                new_position = self.START_POSITIONS[token.color]
            else:
                return False, []  # Can't leave home without a 6
        else:
            new_position = self._calculate_new_position(token, steps)

        # Check if move is valid
        if new_position == -1:
            return False, []  # Invalid move

        # Move the token
        token.move(steps)
        captured_tokens = []

        # Handle captures if not on safe position
        if not self.is_safe_position(new_position) and new_position < self.BOARD_SIZE:
            captured_tokens = self._handle_captures(token, new_position)

        # Place token at new position
        self.place_token(token, new_position)

        return True, captured_tokens

    def _calculate_new_position(self, token: Token, steps: int) -> int:
        """Calculate the new position after moving steps."""
        if token.is_at_home():
            if steps == 6:
                return token._get_start_position()
            else:
                return -1

        # For active tokens, calculate new position
        new_steps_taken = token.steps_taken + steps
        if new_steps_taken >= 57:
            return 56  # Finish position
        else:
            start_pos = token._get_start_position()
            return (start_pos + new_steps_taken - 1) % 56

    def _handle_captures(self, moving_token: Token, position: int) -> List[Token]:
        """
        Handle token captures at the given position.

        Args:
            moving_token: The token that just moved
            position: The position to check for captures

        Returns:
            List of captured tokens
        """
        captured = []
        tokens_at_position = self.get_tokens_at_position(position)

        for token in tokens_at_position:
            # Can only capture opponent tokens
            if token.color != moving_token.color:
                token.send_home()
                self.remove_token(token)
                captured.append(token)

        return captured

    def get_possible_moves(self, color: str, dice_roll: int) -> List[Tuple[Token, int]]:
        """
        Get all possible moves for a player given a dice roll.

        Args:
            color: Player color
            dice_roll: Result of dice roll

        Returns:
            List of (token, new_position) tuples for valid moves
        """
        moves = []

        # Find all tokens of this color
        for position_tokens in self.positions:
            for token in position_tokens:
                if token.color == color and token.can_move(dice_roll):
                    new_pos = self._calculate_new_position(token, dice_roll)
                    if new_pos != -1:
                        moves.append((token, new_pos))

        return moves

    def is_blocked(self, token: Token, position: int) -> bool:
        """Check if a position is blocked by opponent tokens."""
        tokens_at_position = self.get_tokens_at_position(position)

        # Position is blocked if there are 2 or more opponent tokens
        opponent_count = sum(1 for t in tokens_at_position if t.color != token.color)
        return opponent_count >= 2

    def get_board_state(self) -> dict:
        """Get the current state of the board."""
        state = {}
        for position, tokens in enumerate(self.positions):
            if tokens:
                state[position] = [token.to_dict() for token in tokens]
        return state

    def get_color_positions(self, color: str) -> List[int]:
        """Get all positions occupied by tokens of a specific color."""
        positions = []
        for position, tokens in enumerate(self.positions):
            for token in tokens:
                if token.color == color:
                    positions.append(position)
        return positions

    def count_tokens_at_finish(self, color: str) -> int:
        """Count how many tokens of a color have finished."""
        return len(
            [token for token in self.positions[self.BOARD_SIZE] if token.color == color]
        )

    def is_game_finished(self) -> bool:
        """Check if the game is finished (any player has all 4 tokens finished)."""
        for color in self.START_POSITIONS.keys():
            if self.count_tokens_at_finish(color) == 4:
                return True
        return False

    def get_winner(self) -> Optional[str]:
        """Get the winner of the game, if any."""
        for color in self.START_POSITIONS.keys():
            if self.count_tokens_at_finish(color) == 4:
                return color
        return None

    def __repr__(self) -> str:
        """String representation of the board."""
        occupied_positions = []
        for position, tokens in enumerate(self.positions):
            if tokens:
                token_colors = [f"{token.color}_{token.token_id}" for token in tokens]
                occupied_positions.append(f"pos{position}: {token_colors}")
        return f"Board({', '.join(occupied_positions)})"
