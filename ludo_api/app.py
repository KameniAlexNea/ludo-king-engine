"""FastAPI application for Ludo database service."""

import base64
import io

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ludo_database.extensions import DatabaseGame
from ludo_database.storage import get_database
from ludo_engine.constants import CONFIG
from ludo_interface.board_viz import draw_board

from .schemas import (
    ApplyMoveRequest,
    ApplyMoveResponse,
    BoardImageRequest,
    BoardImageResponse,
    BoardStateRequest,
    BoardStateResponse,
    EmptyBoardResponse,
    GameCreateRequest,
    GameQueryRequest,
    GameQueryResponse,
    GameResponse,
    MoveData,
    MoveStatsData,
    PositionStatsRequest,
    PositionStatsResponse,
)

app = FastAPI(
    title="Ludo Database API",
    description="Lichess-style open database API for Ludo games",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "Ludo Database API",
        "version": "1.0.0",
        "endpoints": {
            "board": "/api/board - Get board state and legal moves",
            "apply_move": "/api/move - Apply a move to a board state",
            "empty_board": "/api/board/empty - Get empty board image",
            "board_image": "/api/board/image - Get board image with state",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/api/board", response_model=BoardStateResponse)
async def get_board_state(request: BoardStateRequest):
    """Get board state with available moves.

    If FEN is provided, loads that state.
    Otherwise returns a new game state.
    """
    try:
        if request.fen:
            game = DatabaseGame.from_fen(request.fen)
        else:
            game = DatabaseGame()

        fen = game.to_fen()
        current_player = game.current_player.color
        is_finished = game.is_finished()
        winner = game.winner().color if game.winner() else None

        # Get legal moves for a dice value of 1-6 (for display purposes)
        # In practice, you'd compute this after a specific dice roll
        legal_moves = []
        for dice in range(1, 7):
            moves = game.get_legal_moves_notation(dice)
            for move in moves:
                if move not in legal_moves:
                    legal_moves.append(move)

        return BoardStateResponse(
            fen=fen,
            current_player=current_player,
            legal_moves=legal_moves,
            is_finished=is_finished,
            winner=winner,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/move", response_model=ApplyMoveResponse)
async def apply_move(request: ApplyMoveRequest):
    """Apply a move to a board state and return the resulting state.

    This is the core endpoint for the database - given a position,
    dice roll, and move, returns the next position.
    """
    try:
        game = DatabaseGame.from_fen(request.fen)

        result = game.apply_move_from_notation(request.dice, request.move)
        # Get next player and check if game finished
        next_player = game.current_player.color if not game.is_finished() else None
        game_finished = game.is_finished()
        winner = game.winner().color if game.winner() else None

        return ApplyMoveResponse(
            valid=result["valid"],
            fen_after=result["fen_after"],
            captured=result["captured"],
            finished=result["finished"],
            message=result["message"],
            next_player=next_player,
            game_finished=game_finished,
            winner=winner,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/board/empty", response_model=EmptyBoardResponse)
async def get_empty_board():
    """Get an empty board image (PNG encoded as base64).

    Returns the same visual board as used in the interface,
    but without any tokens on it.
    """
    try:
        # Draw board with no tokens (pass empty token lists)
        from ludo_engine.player import Player

        empty_players = [Player(color) for color in CONFIG.colors]
        # Clear all tokens to base positions
        for player in empty_players:
            for token in player.tokens:
                token.board_index = None
                token.steps_taken = 0
                token.finished = False

        img = draw_board(empty_players)

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        return EmptyBoardResponse(
            image_base64=img_base64,
            width=img.width,
            height=img.height,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/board/image", response_model=BoardImageResponse)
async def get_board_image(request: BoardImageRequest):
    """Get a board image showing the current state (PNG encoded as base64)."""
    try:
        game = DatabaseGame.from_fen(request.fen)
        # Draw board with current token positions
        img = draw_board(game.players)

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        return BoardImageResponse(
            image_base64=img_base64,
            width=img.width,
            height=img.height,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/colors")
async def get_colors():
    """Get available player colors."""
    return {"colors": list(CONFIG.colors)}


@app.get("/api/config")
async def get_config():
    """Get game configuration."""
    return {
        "colors": list(CONFIG.colors),
        "tokens_per_player": 4,
        "track_size": CONFIG.track_size,
        "home_run": CONFIG.home_run,
        "total_steps": CONFIG.total_steps,
        "safe_positions": list(CONFIG.base_safe_positions),
    }


# ============================================================================
# Game Database Endpoints
# ============================================================================


@app.post("/api/games", response_model=GameResponse)
async def create_game(request: GameCreateRequest):
    """Create a new game record in the database."""
    try:
        db = get_database()

        # Create initial board state
        game = DatabaseGame()
        starting_fen = game.to_fen()

        game_record = db.create_game(
            players=request.players,
            starting_fen=starting_fen,
            event=request.event,
            site=request.site,
        )

        return GameResponse(
            game_id=game_record.game_id,
            event=game_record.event,
            site=game_record.site,
            date=game_record.date,
            players=game_record.players,
            result=game_record.result,
            winner_color=game_record.winner_color,
            total_moves=game_record.total_moves,
            starting_fen=game_record.starting_fen,
            moves=[],
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/games/{game_id}", response_model=GameResponse)
async def get_game(game_id: str):
    """Get a specific game by ID."""
    db = get_database()
    game_record = db.get_game(game_id)

    if not game_record:
        raise HTTPException(status_code=404, detail="Game not found")

    moves = [
        MoveData(
            move_number=m.move_number,
            player_color=m.player_color,
            dice_value=m.dice_value,
            move_notation=f"{m.player_color[0]}{m.token_index}{m.action[0]}",
            captured=m.captured,
            finished=m.finished,
        )
        for m in game_record.moves
    ]

    return GameResponse(
        game_id=game_record.game_id,
        event=game_record.event,
        site=game_record.site,
        date=game_record.date,
        players=game_record.players,
        result=game_record.result,
        winner_color=game_record.winner_color,
        total_moves=game_record.total_moves,
        starting_fen=game_record.starting_fen,
        moves=moves,
    )


@app.post("/api/games/query", response_model=GameQueryResponse)
async def query_games(request: GameQueryRequest):
    """Query games with filters."""
    db = get_database()

    games = db.query_games(
        player_name=request.player_name,
        result=request.result,
        min_moves=request.min_moves,
        max_moves=request.max_moves,
        limit=request.limit,
        offset=request.offset,
    )

    game_responses = []
    for game_record in games:
        moves = [
            MoveData(
                move_number=m.move_number,
                player_color=m.player_color,
                dice_value=m.dice_value,
                move_notation=f"{m.player_color[0]}{m.token_index}{m.action[0]}",
                captured=m.captured,
                finished=m.finished,
            )
            for m in game_record.moves[:10]  # Limit moves in list response
        ]

        game_responses.append(
            GameResponse(
                game_id=game_record.game_id,
                event=game_record.event,
                site=game_record.site,
                date=game_record.date,
                players=game_record.players,
                result=game_record.result,
                winner_color=game_record.winner_color,
                total_moves=game_record.total_moves,
                starting_fen=game_record.starting_fen,
                moves=moves,
            )
        )

    return GameQueryResponse(
        games=game_responses,
        total_count=len(games),
        offset=request.offset,
        limit=request.limit,
    )


@app.post("/api/positions/stats", response_model=PositionStatsResponse)
async def get_position_stats(request: PositionStatsRequest):
    """Get statistics for a board position."""
    db = get_database()

    stats = db.get_position_stats(request.fen)

    if not stats:
        # Return empty stats if position hasn't been seen
        return PositionStatsResponse(
            fen=request.fen,
            times_reached=0,
            move_stats=[],
            winrates={},
        )

    # Calculate move statistics
    move_stats = []
    for move_notation, times_played in stats.moves_played.items():
        wins = stats.move_wins.get(move_notation, 0)
        winrate = (wins / times_played * 100) if times_played > 0 else 0.0

        move_stats.append(
            MoveStatsData(
                move_notation=move_notation,
                times_played=times_played,
                wins=wins,
                draws=0,  # TODO: track separately
                losses=times_played - wins,
                winrate=winrate,
            )
        )

    # Sort by times played
    move_stats.sort(key=lambda m: m.times_played, reverse=True)

    # Calculate winrates by color
    winrates = {}
    for color in CONFIG.colors:
        winrates[color] = stats.winrate(color)

    return PositionStatsResponse(
        fen=stats.fen,
        times_reached=stats.times_reached,
        move_stats=move_stats,
        winrates=winrates,
    )


@app.get("/api/stats")
async def get_database_stats():
    """Get overall database statistics."""
    db = get_database()
    return db.get_stats_summary()


@app.get("/api/games/recent")
async def get_recent_games(days: int = 30, limit: int = 100):
    """Get games from the last N days (default 30)."""
    from datetime import datetime, timedelta

    db = get_database()
    cutoff = datetime.now() - timedelta(days=days)

    recent = [
        game
        for game in db.games.values()
        if game.created_at and game.created_at >= cutoff
    ]

    # Sort by date, most recent first
    recent.sort(key=lambda g: g.created_at or datetime.min, reverse=True)
    recent = recent[:limit]

    return {
        "games": [game.to_dict() for game in recent],
        "count": len(recent),
        "days": days,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
