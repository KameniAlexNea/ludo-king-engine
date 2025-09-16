"""
Data models for Ludo game engine.
Contains all dataclasses used throughout the game system.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class TokenInfo:
    """Information about a token."""

    token_id: int
    player_color: str
    state: str
    position: int
    is_in_home: bool
    is_active: bool
    is_in_home_column: bool
    is_finished: bool


@dataclass
class CapturedToken:
    """Information about a captured token."""

    player_color: str
    token_id: int


@dataclass
class MoveResult:
    """Result of executing a move."""

    success: bool
    player_color: str
    token_id: int
    dice_value: int
    old_position: int
    new_position: int
    captured_tokens: List[CapturedToken]
    finished_token: bool
    extra_turn: bool
    error: Optional[str] = None
    game_won: Optional[bool] = None


@dataclass
class ValidMove:
    """A valid move that can be made."""

    token_id: int
    current_position: int
    current_state: str
    target_position: int
    move_type: str
    is_safe_move: bool
    captures_opponent: bool
    captured_tokens: List[CapturedToken]
    strategic_value: float
    strategic_components: Dict[str, float]


@dataclass
class TurnResult:
    """Result of playing a complete turn."""

    player_color: str
    dice_value: int
    consecutive_sixes: int
    moves: List[MoveResult]
    extra_turn: bool
    turn_ended: bool
    reason: Optional[str] = None
    error: Optional[str] = None


@dataclass
class PlayerState:
    """Current state of a player."""

    player_id: int
    color: str
    start_position: int
    tokens: List[TokenInfo]
    tokens_in_home: int
    active_tokens: int
    tokens_in_home_column: int
    finished_tokens: int
    has_won: bool
    positions_occupied: List[int]


@dataclass
class OpponentInfo:
    """Information about an opponent player."""

    color: str
    finished_tokens: int
    tokens_active: int
    threat_level: float
    positions_occupied: List[int]


@dataclass
class StrategicAnalysis:
    """Strategic analysis of the current situation."""

    can_capture: bool
    can_finish_token: bool
    can_exit_home: bool
    safe_moves: List[ValidMove]
    risky_moves: List[ValidMove]
    best_strategic_move: Optional[ValidMove]


@dataclass
class CurrentSituation:
    """Current game situation."""

    player_color: str
    dice_value: int
    consecutive_sixes: int
    turn_count: int


@dataclass
class AIDecisionContext:
    """Context provided to AI for decision making."""

    current_situation: CurrentSituation
    player_state: PlayerState
    opponents: List[OpponentInfo]
    valid_moves: List[ValidMove]
    strategic_analysis: StrategicAnalysis


@dataclass
class PlayerConfiguration:
    """Configuration information for a player."""

    color: str
    player_id: int
    strategy_name: str
    strategy_description: str
    has_strategy: bool
    finished_tokens: int
    tokens_active: int
    tokens_in_home: int


@dataclass
class BoardPositionInfo:
    """Information about tokens at a board position."""

    player_color: str
    token_id: int
    state: str


@dataclass
class BoardState:
    """Complete board state for AI analysis."""

    current_player: str
    board_positions: Dict[int, List[BoardPositionInfo]]
    safe_positions: List[int]
    star_positions: List[int]
    player_start_positions: Dict[str, int]
    home_column_entries: Dict[str, int]


@dataclass
class PositionInfo:
    """Detailed information about a specific position."""

    type: str
    position: int
    is_safe: bool
    is_star: Optional[bool] = None
    color: Optional[str] = None
    tokens: List[TokenInfo] = None


@dataclass
class StrategicComponents:
    """Breakdown of strategic value components."""

    exit_home: float
    finish: float
    home_column_depth: float
    forward_progress: float
    acceleration: float
    safety: float
    vulnerability_penalty: float
