"""
Token class representing individual game pieces in Ludo.

Each token has a color, position, and state. Tokens can move around
the board according to dice rolls and game rules.
"""

from enum import Enum

from .constants import LudoConstants


class TokenState(Enum):
    """Possible states of a token."""

    HOME = "home"  # Token is in the starting home area
    ACTIVE = "active"  # Token is on the main board path
    SAFE = "safe"  # Token is in a safe zone
    FINISHED = "finished"  # Token has reached the end zone


class Token:
    """
    Represents a single game token.

    Each token belongs to a player (identified by color) and tracks
    its current position and state on the board.
    """

    def __init__(self, token_id: int, color: str):
        """
        Initialize a new token.

        Args:
            token_id: Unique identifier for this token (0-3 for each player)
            color: Color of the token ('red', 'blue', 'green', 'yellow')
        """
        self.token_id = token_id
        self.color = color
        self.position = -1  # -1 means token is in home, 0-55 are board positions
        self.state = TokenState.HOME
        self.steps_taken = 0  # Total steps taken by this token

    def is_at_home(self) -> bool:
        """Check if token is still in home."""
        return self.state == TokenState.HOME

    def is_active(self) -> bool:
        """Check if token is actively moving on the board."""
        return self.state == TokenState.ACTIVE

    def is_finished(self) -> bool:
        """Check if token has reached the finish."""
        return self.state == TokenState.FINISHED

    def is_safe(self) -> bool:
        """Check if token is in a safe position."""
        return self.state == TokenState.SAFE

    def can_move(self, dice_roll: int) -> bool:
        """
        Check if this token can move with the given dice roll.

        Args:
            dice_roll: The result of the dice roll (1-6)

        Returns:
            True if token can move, False otherwise
        """
        if self.is_finished():
            return False

        if self.is_at_home():
            # Can only leave home with a 6
            return dice_roll == 6

        # Check if move would exceed the finish line
        if self.is_active():
            return self.steps_taken + dice_roll <= 57  # 57 steps to finish

        return True

    def move(self, steps: int) -> bool:
        """
        Move the token by the specified number of steps.

        Args:
            steps: Number of steps to move (usually dice roll)

        Returns:
            True if move was successful, False otherwise
        """
        if not self.can_move(steps):
            return False

        if self.is_at_home() and steps == 6:
            # Move from home to start position
            self.position = self._get_start_position()
            self.state = TokenState.ACTIVE
            self.steps_taken = 1
            return True

        if self.is_active():
            self.steps_taken += steps

            # Simple linear movement - each player needs 57 steps to finish
            # (1 step to get on board + 56 steps around)
            if self.steps_taken >= LudoConstants.BOARD_SIZE + 1:
                self.state = TokenState.FINISHED
                self.position = LudoConstants.BOARD_SIZE  # Finish position
            else:
                # Calculate position on circular track
                start_pos = self._get_start_position()
                self.position = (
                    start_pos + self.steps_taken - 1
                ) % LudoConstants.BOARD_SIZE

            return True

        return False

    def send_home(self):
        """Send the token back to home (when captured by opponent)."""
        self.position = -1
        self.state = TokenState.HOME
        self.steps_taken = 0

    def _get_start_position(self) -> int:
        """Get the starting position on the board for this token's color."""
        return LudoConstants.START_POSITIONS.get(self.color, 0)

    def __repr__(self) -> str:
        """String representation of the token."""
        return f"Token({self.color}_{self.token_id}, pos={self.position}, state={self.state.value})"

    def __eq__(self, other) -> bool:
        """Check equality with another token."""
        if not isinstance(other, Token):
            return False
        return self.token_id == other.token_id and self.color == other.color

    def to_dict(self) -> dict:
        """Convert token to dictionary representation."""
        return {
            "token_id": self.token_id,
            "color": self.color,
            "position": self.position,
            "state": self.state.value,
            "steps_taken": self.steps_taken,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Token":
        """Create token from dictionary representation."""
        token = cls(data["token_id"], data["color"])
        token.position = data["position"]
        token.state = TokenState(data["state"])
        token.steps_taken = data["steps_taken"]
        return token
