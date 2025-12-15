"""Validation functions for Ludo database operations."""

import re
import uuid

from ludo_engine.constants import CONFIG


class ValidationError(Exception):
    """Raised when validation fails."""

    pass


def validate_dice(dice: int) -> None:
    """Validate dice value is between 1 and 6."""
    if not isinstance(dice, int):
        raise ValidationError(f"Dice must be an integer, got {type(dice).__name__}")
    if dice < 1 or dice > 6:
        raise ValidationError(f"Dice value must be between 1 and 6, got {dice}")


def validate_color(color: str) -> None:
    """Validate color is one of the valid player colors."""
    if not isinstance(color, str):
        raise ValidationError(f"Color must be a string, got {type(color).__name__}")
    if color not in CONFIG.colors:
        raise ValidationError(
            f"Invalid color '{color}'. Valid colors: {', '.join(CONFIG.colors)}"
        )


def validate_move_notation(notation: str) -> None:
    """Validate move notation format.

    Valid formats:
    - r0e: enter move
    - g2a5: advance move
    - b3a4x: advance with capture
    """
    if not isinstance(notation, str):
        raise ValidationError(
            f"Move notation must be a string, got {type(notation).__name__}"
        )

    if len(notation) < 3:
        raise ValidationError(
            f"Invalid move notation '{notation}': too short (minimum 3 characters)"
        )

    # Check format: <color_char><token_index><action>[<dice>][x]
    if not re.match(r"^[rgby]\d+[ea]\d*x?$", notation.lower()):
        raise ValidationError(
            f"Invalid move notation format '{notation}'. "
            f"Expected format: <color><token><action>[dice][x] (e.g., 'r0e', 'g2a5', 'b3a4x')"
        )

    # Extract parts
    token_index = int(notation[1])
    action_part = notation[2:]

    # Validate token index (0-3)
    if token_index < 0 or token_index > 3:
        raise ValidationError(
            f"Invalid token index {token_index} in '{notation}'. Must be 0-3."
        )

    # Validate action
    if action_part[0] not in ["e", "a"]:
        raise ValidationError(
            f"Invalid action '{action_part[0]}' in '{notation}'. Must be 'e' (enter) or 'a' (advance)."
        )

    # If advance, validate dice value
    if action_part[0] == "a":
        dice_str = action_part[1:].rstrip("x")
        if not dice_str:
            raise ValidationError(
                f"Advance move '{notation}' must include dice value (e.g., 'a5')"
            )
        try:
            dice = int(dice_str)
            validate_dice(dice)
        except ValueError:
            raise ValidationError(
                f"Invalid dice value in move notation '{notation}': '{dice_str}'"
            )


def validate_fen(fen: str, max_length: int = 2000) -> None:
    """Validate FEN string format and length.

    FEN format: <current_player> <token_data> <token_data> ...
    Token data: color:index:board_index:steps:finished
    """
    if not isinstance(fen, str):
        raise ValidationError(f"FEN must be a string, got {type(fen).__name__}")

    if len(fen) > max_length:
        raise ValidationError(
            f"FEN string too long: {len(fen)} characters (max {max_length})"
        )

    if not fen.strip():
        raise ValidationError("FEN string cannot be empty")

    parts = fen.split()
    if len(parts) < 2:
        raise ValidationError(
            f"Invalid FEN format: expected at least 2 parts (current_player + tokens), got {len(parts)}"
        )

    # Validate current player indicator
    current_player = parts[0]
    valid_prefixes = [color[0] for color in CONFIG.colors]
    if current_player not in valid_prefixes:
        raise ValidationError(
            f"Invalid current player indicator '{current_player}'. "
            f"Expected one of: {', '.join(valid_prefixes)}"
        )

    # Validate token data format
    for i, token_group in enumerate(parts[1:], 1):
        tokens = token_group.split(",")
        if len(tokens) != 4:  # Each player has 4 tokens
            raise ValidationError(
                f"Invalid token group {i}: expected 4 tokens, got {len(tokens)}"
            )

        for token_data in tokens:
            token_parts = token_data.split(":")
            if len(token_parts) != 5:
                raise ValidationError(
                    f"Invalid token data format '{token_data}': "
                    f"expected 5 parts (color:index:board_index:steps:finished)"
                )

            try:
                color_char, idx, board_idx, steps, finished = token_parts
                # Validate each part is numeric where expected
                int(idx)
                int(board_idx)
                int(steps)
                int(finished)
            except ValueError as e:
                raise ValidationError(f"Invalid token data '{token_data}': {str(e)}")


def validate_game_id(game_id: str) -> None:
    """Validate game ID is a valid UUID."""
    if not isinstance(game_id, str):
        raise ValidationError(f"Game ID must be a string, got {type(game_id).__name__}")

    try:
        uuid.UUID(game_id)
    except ValueError:
        raise ValidationError(f"Invalid game ID '{game_id}': must be a valid UUID")


def validate_player_name(name: str, max_length: int = 50) -> None:
    """Validate player name."""
    if not isinstance(name, str):
        raise ValidationError(
            f"Player name must be a string, got {type(name).__name__}"
        )

    if not name.strip():
        raise ValidationError("Player name cannot be empty")

    if len(name) > max_length:
        raise ValidationError(
            f"Player name too long: {len(name)} characters (max {max_length})"
        )


def validate_event_name(name: str, max_length: int = 200) -> None:
    """Validate event name."""
    if not isinstance(name, str):
        raise ValidationError(f"Event name must be a string, got {type(name).__name__}")

    if len(name) > max_length:
        raise ValidationError(
            f"Event name too long: {len(name)} characters (max {max_length})"
        )


def validate_query_limit(limit: int, max_limit: int = 100) -> None:
    """Validate query limit is within acceptable range."""
    if not isinstance(limit, int):
        raise ValidationError(f"Limit must be an integer, got {type(limit).__name__}")

    if limit < 1:
        raise ValidationError(f"Limit must be at least 1, got {limit}")

    if limit > max_limit:
        raise ValidationError(f"Limit too large: {limit} (max {max_limit})")


def validate_query_offset(offset: int) -> None:
    """Validate query offset is non-negative."""
    if not isinstance(offset, int):
        raise ValidationError(f"Offset must be an integer, got {type(offset).__name__}")

    if offset < 0:
        raise ValidationError(f"Offset cannot be negative, got {offset}")


__all__ = [
    "ValidationError",
    "validate_dice",
    "validate_color",
    "validate_move_notation",
    "validate_fen",
    "validate_game_id",
    "validate_player_name",
    "validate_event_name",
    "validate_query_limit",
    "validate_query_offset",
]
