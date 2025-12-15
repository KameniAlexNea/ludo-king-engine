"""Pydantic schemas for API requests and responses."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class BoardStateRequest(BaseModel):
    """Request for board state information."""

    fen: Optional[str] = Field(
        None, description="FEN notation of board state (optional for new game)"
    )


class BoardStateResponse(BaseModel):
    """Response with board state and available moves."""

    fen: str = Field(..., description="Current board state in FEN notation")
    current_player: str = Field(..., description="Color of current player")
    legal_moves: List[str] = Field(..., description="List of legal moves in notation")
    is_finished: bool = Field(..., description="Whether the game is finished")
    winner: Optional[str] = Field(None, description="Winner color if game is finished")


class ApplyMoveRequest(BaseModel):
    """Request to apply a move to a board state."""

    fen: str = Field(..., description="Current board state in FEN notation")
    dice: int = Field(..., ge=1, le=6, description="Dice value rolled")
    move: str = Field(..., description="Move in notation format (e.g., 'r1e', 'g2a5')")


class ApplyMoveResponse(BaseModel):
    """Response after applying a move."""

    valid: bool = Field(..., description="Whether the move was valid")
    fen_after: str = Field(..., description="Board state after move in FEN notation")
    captured: bool = Field(..., description="Whether a token was captured")
    finished: bool = Field(..., description="Whether a token finished")
    message: str = Field(..., description="Status message")
    next_player: Optional[str] = Field(None, description="Next player color")
    game_finished: bool = Field(False, description="Whether the game ended")
    winner: Optional[str] = Field(None, description="Winner if game finished")


class EmptyBoardResponse(BaseModel):
    """Response with empty board image."""

    image_base64: str = Field(
        ..., description="Base64 encoded PNG image of empty board"
    )
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")


class BoardImageRequest(BaseModel):
    """Request for board image with current state."""

    fen: str = Field(..., description="Board state in FEN notation")


class BoardImageResponse(BaseModel):
    """Response with board image showing current state."""

    image_base64: str = Field(..., description="Base64 encoded PNG image")
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")


class MoveData(BaseModel):
    """Single move in a game."""

    move_number: int
    player_color: str
    dice_value: int
    move_notation: str
    captured: bool = False
    finished: bool = False


class GameCreateRequest(BaseModel):
    """Request to create a new game record."""

    players: Dict[str, str] = Field(..., description="Player names by color")
    event: str = Field("Casual Game", description="Event name")
    site: str = Field("Ludo Engine", description="Site identifier")


class GameUpdateRequest(BaseModel):
    """Request to add moves to an existing game."""

    game_id: str = Field(..., description="Game identifier")
    moves: List[MoveData] = Field(..., description="Moves to add")


class GameResponse(BaseModel):
    """Response with game information."""

    game_id: str
    event: str
    site: str
    date: str
    players: Dict[str, str]
    result: str
    winner_color: Optional[str]
    total_moves: int
    starting_fen: str
    moves: List[MoveData]


class GameQueryRequest(BaseModel):
    """Request to query games."""

    player_name: Optional[str] = Field(None, description="Filter by player name")
    player_color: Optional[str] = Field(None, description="Filter by player color")
    result: Optional[str] = Field(None, description="Filter by result")
    min_moves: Optional[int] = Field(None, description="Minimum number of moves")
    max_moves: Optional[int] = Field(None, description="Maximum number of moves")
    limit: int = Field(10, ge=1, le=100, description="Maximum results to return")
    offset: int = Field(0, ge=0, description="Result offset for pagination")


class GameQueryResponse(BaseModel):
    """Response with list of games matching query."""

    games: List[GameResponse]
    total_count: int
    offset: int
    limit: int


class PositionStatsRequest(BaseModel):
    """Request for position statistics."""

    fen: str = Field(..., description="Board position in FEN notation")


class MoveStatsData(BaseModel):
    """Statistics for a specific move from a position."""

    move_notation: str
    times_played: int
    wins: int
    draws: int
    losses: int
    winrate: float


class PositionStatsResponse(BaseModel):
    """Response with statistics for a position."""

    fen: str
    times_reached: int
    move_stats: List[MoveStatsData]
    winrates: Dict[str, float]  # by color


__all__ = [
    "BoardStateRequest",
    "BoardStateResponse",
    "ApplyMoveRequest",
    "ApplyMoveResponse",
    "EmptyBoardResponse",
    "BoardImageRequest",
    "BoardImageResponse",
    "MoveData",
    "GameCreateRequest",
    "GameUpdateRequest",
    "GameResponse",
    "GameQueryRequest",
    "GameQueryResponse",
    "PositionStatsRequest",
    "MoveStatsData",
    "PositionStatsResponse",
]
