"""
Data models for Ludo game engine.

This module contains data classes that represent the structured output
of the Ludo game engine, providing type safety and clear interfaces.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class GameStatus(Enum):
    """Possible states of the game."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    PAUSED = "paused"


@dataclass
class TokenInfo:
    """Information about a game token."""

    id: int
    color: str
    position: int
    steps_taken: int
    is_finished: bool
    is_at_home: bool


@dataclass
class PlayerStats:
    """Statistics for a player."""

    color: str
    name: str
    tokens_finished: int
    tokens_captured: int
    total_moves: int
    sixes_rolled: int
    games_won: int = 0
    average_turns_per_game: float = 0.0


@dataclass
class TurnResult:
    """Result of a single turn."""

    player: str
    dice_roll: Optional[int]
    move_made: bool
    token_moved: Optional[TokenInfo]
    captured_tokens: List[TokenInfo]
    finished_tokens: int
    another_turn: bool
    game_finished: bool
    winner: Optional[str]


@dataclass
class GameStateData:
    """Current state of the game."""

    board: Dict[str, Any]
    players: List[PlayerStats]
    current_player: int
    turn_count: int
    game_status: GameStatus
    sixes_in_row: int


@dataclass
class FinalPosition:
    """Final position/ranking of a player."""

    rank: int
    tokens_finished: int
    total_moves: int


@dataclass
class GameResults:
    """Final results of a completed game."""

    winner: Optional[str]
    game_status: GameStatus
    turns_played: int
    total_moves: int
    dice_rolls: int
    player_stats: List[PlayerStats]
    final_positions: Dict[str, FinalPosition]


@dataclass
class TournamentResult:
    """Result of a strategy tournament."""

    strategies: List[str]
    rounds: int
    games_per_round: int
    total_games: int
    wins: Dict[str, int]
    detailed_stats: Dict[str, Dict[str, Any]]
    win_rates: Dict[str, float]


@dataclass
class StrategyComparison:
    """Result of comparing two strategies."""

    strategy1: str
    strategy2: str
    games_played: int
    strategy1_wins: int
    strategy2_wins: int
    draws: int
    games: List[TurnResult]
    strategy1_win_rate: float
    strategy2_win_rate: float
    draw_rate: float


@dataclass
class GameAnalysis:
    """Analysis of game results."""

    game_length: int
    efficiency: float
    player_performance: Dict[str, Dict[str, Any]]
    strategy_insights: Dict[str, Any]


@dataclass
class PlayerPositionSummary:
    """Summary of a player's token positions."""

    home: int
    active: int
    finished: int
    total: int


@dataclass
class PlayerData:
    """Complete player data for serialization."""

    color: str
    name: str
    tokens: List[TokenInfo]
    stats: PlayerStats


@dataclass
class GameReplayMetadata:
    """Metadata for game replay."""

    timestamp: str
    players: List[str]
    strategies: List[str]
    total_turns: int
    winner: Optional[str]


@dataclass
class GameReplayData:
    """Complete game replay data."""

    metadata: GameReplayMetadata
    history: List[TurnResult]  # Turn results as dictionaries
    final_state: GameStateData
