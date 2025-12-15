"""Ludo Database Notation (LDN) - PGN-style format for Ludo games.

Format similar to chess PGN:
- FEN-like notation for board state
- Move notation: <color><token><action>[<capture>]
  Examples: r1e (red token 1 enter), g2a5 (green token 2 advance 5), b3a4x (blue token 3 advance 4 and capture)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from ludo_engine.constants import CONFIG
from ludo_engine.game import Decision, Game
from ludo_engine.token import Token

if TYPE_CHECKING:
    pass


@dataclass
class LudoNotation:
    """Container for a Ludo game in LDN format."""

    event: str = "Casual Game"
    site: str = "Ludo Engine"
    date: str = ""
    round: str = "1"
    players: Dict[str, str] = None  # color -> player name
    result: str = "*"  # *, 1-0 (red wins), 0-1 (green wins), etc.

    # Game metadata
    time_control: str = "-"
    eco: str = "-"  # Opening classification (future)

    # Initial position (FEN-like)
    fen: str = ""

    # Move list with dice rolls
    moves: List[Tuple[int, str]] = None  # [(dice, move_notation), ...]

    def __post_init__(self):
        if self.players is None:
            self.players = {color: "?" for color in CONFIG.colors}
        if self.moves is None:
            self.moves = []

    def to_ldn_string(self) -> str:
        """Convert to LDN string format (PGN-style)."""
        lines = []

        # Headers
        lines.append(f'[Event "{self.event}"]')
        lines.append(f'[Site "{self.site}"]')
        lines.append(f'[Date "{self.date}"]')
        lines.append(f'[Round "{self.round}"]')

        for color in CONFIG.colors:
            player_name = self.players.get(color, "?")
            lines.append(f'[{color.title()} "{player_name}"]')

        lines.append(f'[Result "{self.result}"]')
        lines.append(f'[TimeControl "{self.time_control}"]')

        if self.fen:
            lines.append(f'[FEN "{self.fen}"]')

        lines.append("")  # Blank line before moves

        # Moves - format: turn_number. dice:move dice:move ...
        if self.moves:
            move_text = []
            for i, (dice, move) in enumerate(self.moves, 1):
                move_text.append(f"{dice}:{move}")
                if i % 4 == 0:  # New line every 4 moves for readability
                    lines.append(" ".join(move_text))
                    move_text = []
            if move_text:
                lines.append(" ".join(move_text))

        lines.append(f" {self.result}")

        return "\n".join(lines)

    @classmethod
    def from_ldn_string(cls, ldn_string: str) -> LudoNotation:
        """Parse LDN string into LudoNotation object."""
        lines = ldn_string.strip().split("\n")

        notation = cls()
        moves = []
        in_moves = False

        for line in lines:
            line = line.strip()
            if not line:
                in_moves = True
                continue

            if line.startswith("[") and line.endswith("]"):
                # Parse header
                tag, value = line[1:-1].split('"', 1)
                tag = tag.strip()
                value = value.rstrip('"')

                if tag == "Event":
                    notation.event = value
                elif tag == "Site":
                    notation.site = value
                elif tag == "Date":
                    notation.date = value
                elif tag == "Round":
                    notation.round = value
                elif tag == "Result":
                    notation.result = value
                elif tag == "TimeControl":
                    notation.time_control = value
                elif tag == "FEN":
                    notation.fen = value
                elif tag.lower() in [c.lower() for c in CONFIG.colors]:
                    notation.players[tag.lower()] = value

            elif in_moves and not line.startswith("["):
                # Parse moves
                tokens = line.split()
                for token in tokens:
                    if token == "*" or "-" in token:  # Result marker
                        continue
                    if ":" in token:
                        dice_str, move_str = token.split(":", 1)
                        try:
                            dice = int(dice_str)
                            moves.append((dice, move_str))
                        except ValueError:
                            continue

        notation.moves = moves
        return notation


def state_to_fen(game: Game) -> str:
    """Convert game state to FEN-like notation.

    Format: <current_player> <token_positions>
    Token positions: color:index:board_index:steps_taken:finished
    Example: r r:0:-1:0:0,r:1:12:12:0,r:2:-1:0:0,r:3:-1:0:0 g:0:...
    """
    parts = []

    # Current player indicator (first letter of color)
    parts.append(game.current_player.color[0])

    # Token positions for each player
    for player in game.players:
        tokens_data = []
        for token in player.tokens:
            # Convert None to -1 for serialization
            board_idx = -1 if token.board_index is None else token.board_index
            token_str = f"{token.color[0]}:{token.index}:{board_idx}:{token.steps_taken}:{int(token.finished)}"
            tokens_data.append(token_str)
        parts.append(",".join(tokens_data))

    return " ".join(parts)


def fen_to_state(fen: str) -> Tuple[str, List[List[Token]]]:
    """Parse FEN-like notation back to game state.

    Returns: (current_player_color, list of token lists per player)
    """
    parts = fen.split()

    # Current player from first character
    current_player_map = {color[0]: color for color in CONFIG.colors}
    current_player = current_player_map.get(parts[0], CONFIG.colors[0])

    # Parse tokens
    all_tokens = []
    for token_group in parts[1:]:
        player_tokens = []
        for token_data in token_group.split(","):
            color_char, idx, board_idx, steps, finished = token_data.split(":")
            color_map = {color[0]: color for color in CONFIG.colors}
            color = color_map[color_char]

            # Convert -1 back to None for board_index
            board_index_value = int(board_idx)
            if board_index_value == -1:
                board_index_value = None

            token = Token(
                color=color,
                index=int(idx),
                board_index=board_index_value,
                steps_taken=int(steps),
                finished=bool(int(finished)),
            )
            player_tokens.append(token)
        all_tokens.append(player_tokens)

    return current_player, all_tokens


def decision_to_notation(decision: Decision, dice: int, captured: bool = False) -> str:
    """Convert a decision to move notation.

    Format: <color_initial><token_index><action><dice>[x]
    Examples:
      - r1e: red token 1 enter
      - g2a5: green token 2 advance 5
      - b3a4x: blue token 3 advance 4 and capture
    """
    action, token_index = decision
    color = action[0] if len(action) == 1 else "?"

    if action == "enter":
        notation = f"{color}{token_index}e"
    else:  # advance
        notation = f"{color}{token_index}a{dice}"

    if captured:
        notation += "x"

    return notation


def notation_to_decision(notation: str) -> Tuple[Decision, int, bool]:
    """Parse move notation to decision.

    Returns: (decision, dice_value, was_capture)
    """
    captured = notation.endswith("x")
    if captured:
        notation = notation[:-1]

    # Parse: <color><index><action>[<dice>]
    # color_char = notation[0]
    token_index = int(notation[1])
    action_part = notation[2:]

    if action_part == "e":
        return ("enter", token_index), 6, captured
    elif action_part[0] == "a":
        dice = int(action_part[1:])
        return ("advance", token_index), dice, captured

    raise ValueError(f"Invalid move notation: {notation}")


def to_ldn(game: Game, metadata: Optional[Dict] = None) -> LudoNotation:
    """Convert a Game object to LDN format."""
    notation = LudoNotation()

    if metadata:
        notation.event = metadata.get("event", notation.event)
        notation.site = metadata.get("site", notation.site)
        notation.date = metadata.get("date", notation.date)
        notation.players = metadata.get("players", notation.players)
    else:
        notation.players = {p.color: p.color.title() for p in game.players}

    # Initial position
    notation.fen = state_to_fen(game)

    # Result
    winner = game.winner()
    if winner:
        notation.result = f"{winner.color} wins"
    elif game.is_finished():
        notation.result = "Draw"
    else:
        notation.result = "*"

    # Moves (from history)
    # Note: We'd need to track dice rolls in history to fully reconstruct this
    # For now, this is a placeholder
    notation.moves = []

    return notation


def from_ldn(ldn_string: str):
    """Parse LDN string and create a DatabaseGame object in that state."""
    from ludo_database.extensions import DatabaseGame

    notation = LudoNotation.from_ldn_string(ldn_string)

    # Create game from FEN if available
    if notation.fen:
        game = DatabaseGame.from_fen(notation.fen)
    else:
        game = DatabaseGame()

    return game, notation


__all__ = [
    "LudoNotation",
    "state_to_fen",
    "fen_to_state",
    "decision_to_notation",
    "notation_to_decision",
    "to_ldn",
    "from_ldn",
]
