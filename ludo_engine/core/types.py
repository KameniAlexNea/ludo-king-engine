"""
Type definitions and protocols for Ludo Engine.

This module provides comprehensive type hints, protocols, and type guards
to ensure type safety throughout the Ludo Engine codebase.
"""

from abc import ABC, abstractmethod
from typing import (
    Any,
    Dict,
    List,
    Literal,
    NamedTuple,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    Union,
)

from ludo_engine.core.player import PlayerColor
from ludo_engine.models.model import TokenState

# Type variables
T = TypeVar('T')
PlayerId = int
TokenId = int
BoardPosition = int
DiceValue = Literal[1, 2, 3, 4, 5, 6]

# Game state types
GamePhase = Literal['setup', 'playing', 'finished']
TurnPhase = Literal['roll_dice', 'select_move', 'execute_move', 'end_turn']

# Strategy types
StrategyName = str
StrategyWeight = float
DecisionScore = float

# Board types
BoardPosition = int
SafePosition = bool
HomeColumnPosition = int

# Validation types
ValidationResult = Tuple[bool, Optional[str]]
ErrorMessage = str

class GameConfig(NamedTuple):
    """Configuration for game initialization."""
    player_colors: List[PlayerColor]
    random_seed: Optional[int] = None
    max_turns: Optional[int] = None
    enable_logging: bool = False

class TokenPosition(NamedTuple):
    """Represents a token's position with metadata."""
    position: int
    state: TokenState
    is_safe: bool
    can_be_captured: bool

class MoveValidation(NamedTuple):
    """Result of move validation."""
    is_valid: bool
    error_message: Optional[str]
    blocking_tokens: List[Tuple[PlayerColor, TokenId]]
    captured_tokens: List[Tuple[PlayerColor, TokenId]]

class GameState(NamedTuple):
    """Complete game state snapshot."""
    current_player_index: int
    consecutive_sixes: int
    game_over: bool
    winner: Optional[PlayerColor]
    turn_count: int
    last_dice_value: DiceValue

# Protocols for type safety
class HasPosition(Protocol):
    """Protocol for objects that have a position."""
    position: int

class HasColor(Protocol):
    """Protocol for objects that have a color."""
    color: PlayerColor

class Movable(Protocol):
    """Protocol for objects that can move."""

    def can_move(self, dice_value: DiceValue) -> bool:
        """Check if the object can move with given dice value."""
        ...

    def get_target_position(self, dice_value: DiceValue, start_position: int) -> int:
        """Get target position after moving with dice value."""
        ...

class Serializable(Protocol):
    """Protocol for objects that can be serialized."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert object to dictionary representation."""
        ...

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Serializable':
        """Create object from dictionary representation."""
        ...

class Strategy(Protocol):
    """Protocol for AI strategies."""

    @property
    def name(self) -> StrategyName:
        """Strategy name."""
        ...

    @property
    def description(self) -> str:
        """Strategy description."""
        ...

    def decide_move(
        self,
        valid_moves: List['ValidMove'],
        game_context: 'AIDecisionContext'
    ) -> Optional[Tuple[TokenId, int]]:
        """Decide which move to make."""
        ...

class GameObserver(Protocol):
    """Protocol for game observers."""

    def on_game_start(self, game: 'LudoGame') -> None:
        """Called when game starts."""
        ...

    def on_turn_start(self, game: 'LudoGame', player: 'Player') -> None:
        """Called when a player's turn starts."""
        ...

    def on_move_executed(self, game: 'LudoGame', move_result: 'MoveResult') -> None:
        """Called when a move is executed."""
        ...

    def on_game_end(self, game: 'LudoGame', winner: Optional['Player']) -> None:
        """Called when game ends."""
        ...

class Validator(Protocol):
    """Protocol for validation objects."""

    def validate(self, obj: Any) -> ValidationResult:
        """Validate an object and return result."""
        ...

    def get_validation_errors(self, obj: Any) -> List[ErrorMessage]:
        """Get detailed validation errors."""
        ...

# Type guards
def is_valid_dice_value(value: int) -> bool:
    """Check if value is a valid dice roll (1-6)."""
    return isinstance(value, int) and 1 <= value <= 6

def is_valid_token_id(token_id: int) -> bool:
    """Check if token_id is valid (0-3)."""
    return isinstance(token_id, int) and 0 <= token_id <= 3

def is_valid_position(position: int) -> bool:
    """Check if position is valid (0-51 for main board, negative for special positions)."""
    return isinstance(position, int) and (position < 0 or 0 <= position <= 51)

def is_valid_player_count(count: int) -> bool:
    """Check if player count is valid (2-4)."""
    return isinstance(count, int) and 2 <= count <= 4

# Generic types for collections
PlayerList = List['Player']
TokenList = List['Token']
PositionList = List[int]
MoveList = List['ValidMove']
StrategyList = List[Strategy]

# Result types
MoveExecutionResult = Union['MoveResult', Exception]
GameCreationResult = Union['LudoGame', Exception]
StrategyCreationResult = Union[Strategy, Exception]

# Configuration types
StrategyConfig = Dict[str, Any]
GameRulesConfig = Dict[str, Any]
LoggingConfig = Dict[str, Any]

# Forward references (to be resolved at runtime)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ludo_engine.core.game import LudoGame
    from ludo_engine.core.player import Player
    from ludo_engine.core.token import Token
    from ludo_engine.models.model import ValidMove, MoveResult, AIDecisionContext