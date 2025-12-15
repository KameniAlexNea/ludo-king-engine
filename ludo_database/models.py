"""Database models for storing Ludo games."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class MoveRecord:
    """Single move/decision in a game."""

    move_number: int
    player_color: str
    dice_value: int
    action: str  # "enter" or "advance"
    token_index: int
    captured: bool
    finished: bool
    fen_after: str  # Board state after this move
    timestamp: Optional[datetime] = None


@dataclass
class GameRecord:
    """Complete game record for database storage."""

    # Game identification
    game_id: str
    event: str = "Casual Game"
    site: str = "Ludo Engine"
    date: str = ""

    # Players
    players: Dict[str, str] = field(default_factory=dict)  # color -> name/id
    player_ratings: Dict[str, int] = field(default_factory=dict)  # color -> rating

    # Game outcome
    result: str = "*"  # *, red wins, green wins, etc.
    winner_color: Optional[str] = None
    termination: str = "normal"  # normal, timeout, abandoned

    # Initial position
    starting_fen: str = ""

    # Moves
    moves: List[MoveRecord] = field(default_factory=list)

    # Game metadata
    time_control: str = "-"
    total_moves: int = 0
    duration_seconds: Optional[int] = None

    # Statistics
    captures: Dict[str, int] = field(default_factory=dict)  # color -> capture count
    tokens_finished: Dict[str, int] = field(
        default_factory=dict
    )  # color -> finished count

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "game_id": self.game_id,
            "event": self.event,
            "site": self.site,
            "date": self.date,
            "players": self.players,
            "player_ratings": self.player_ratings,
            "result": self.result,
            "winner_color": self.winner_color,
            "termination": self.termination,
            "starting_fen": self.starting_fen,
            "moves": [
                {
                    "move_number": m.move_number,
                    "player_color": m.player_color,
                    "dice_value": m.dice_value,
                    "action": m.action,
                    "token_index": m.token_index,
                    "captured": m.captured,
                    "finished": m.finished,
                    "fen_after": m.fen_after,
                }
                for m in self.moves
            ],
            "time_control": self.time_control,
            "total_moves": self.total_moves,
            "duration_seconds": self.duration_seconds,
            "captures": self.captures,
            "tokens_finished": self.tokens_finished,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class PositionStats:
    """Statistics for a specific board position."""

    fen: str
    position_hash: str  # Hash of the position for indexing

    # Occurrence statistics
    times_reached: int = 0

    # Outcomes from this position (by next player to move)
    wins: Dict[str, int] = field(default_factory=dict)  # color -> win count
    draws: int = 0
    losses: Dict[str, int] = field(default_factory=dict)  # color -> loss count

    # Move statistics from this position
    moves_played: Dict[str, int] = field(default_factory=dict)  # move_notation -> count
    move_wins: Dict[str, int] = field(default_factory=dict)  # move_notation -> wins

    # First seen / last seen
    first_game_id: Optional[str] = None
    last_game_id: Optional[str] = None
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None

    def winrate(self, color: str) -> float:
        """Calculate win rate for a color from this position."""
        total = self.wins.get(color, 0) + self.losses.get(color, 0) + self.draws
        if total == 0:
            return 0.0
        return (self.wins.get(color, 0) / total) * 100

    def move_winrate(self, move_notation: str) -> float:
        """Calculate win rate for a specific move."""
        played = self.moves_played.get(move_notation, 0)
        if played == 0:
            return 0.0
        wins = self.move_wins.get(move_notation, 0)
        return (wins / played) * 100

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "fen": self.fen,
            "position_hash": self.position_hash,
            "times_reached": self.times_reached,
            "wins": self.wins,
            "draws": self.draws,
            "losses": self.losses,
            "moves_played": self.moves_played,
            "move_wins": self.move_wins,
            "first_game_id": self.first_game_id,
            "last_game_id": self.last_game_id,
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
        }


__all__ = ["MoveRecord", "GameRecord", "PositionStats"]
