"""Database storage backend for Ludo games using SQLite."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select

from ludo_database.models import GameRecord as GameRecordModel
from ludo_database.models import MoveRecord as MoveRecordModel
from ludo_database.models import PositionStats as PositionStatsModel
from ludo_database.validation import (
    validate_fen,
    validate_game_id,
    validate_query_limit,
    validate_query_offset,
)


class GameRecord(SQLModel, table=True):
    """SQLModel for game records."""

    game_id: str = Field(primary_key=True)
    event: str = "Casual Game"
    site: str = "Ludo Engine"
    date: str = ""
    players: str = Field(default="{}")
    player_ratings: str = Field(default="{}")
    result: str = "*"
    winner_color: Optional[str] = None
    termination: str = "normal"
    starting_fen: str = ""
    time_control: str = "-"
    total_moves: int = 0
    duration_seconds: Optional[int] = None
    captures: str = Field(default="{}")
    tokens_finished: str = Field(default="{}")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MoveRecord(SQLModel, table=True):
    """SQLModel for move records."""

    id: Optional[int] = Field(default=None, primary_key=True)
    game_id: str = Field(foreign_key="gamerecord.game_id")
    move_number: int
    player_color: str
    dice_value: int
    action: str
    token_index: int
    captured: bool
    finished: bool
    fen_after: str
    timestamp: Optional[datetime] = None


class PositionStats(SQLModel, table=True):
    """SQLModel for position statistics."""

    position_hash: str = Field(primary_key=True)
    fen: str
    times_reached: int = 0
    wins: str = Field(default="{}")
    draws: int = 0
    losses: str = Field(default="{}")
    moves_played: str = Field(default="{}")
    move_wins: str = Field(default="{}")
    first_game_id: Optional[str] = None
    last_game_id: Optional[str] = None
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None


class GameDatabase:
    """SQLite database for Ludo games."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or "data/ludo_games.db"
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        SQLModel.metadata.create_all(self.engine)

    def _position_hash(self, fen: str) -> str:
        """Generate a hash for a FEN position."""
        return hashlib.sha256(fen.encode()).hexdigest()[:16]

    def create_game(
        self,
        players: Dict[str, str],
        starting_fen: str,
        event: str = "Casual Game",
        site: str = "Ludo Engine",
    ) -> GameRecordModel:
        """Create a new game record."""
        game_id = str(uuid.uuid4())
        now = datetime.now()

        game = GameRecord(
            game_id=game_id,
            event=event,
            site=site,
            date=now.strftime("%Y.%m.%d"),
            players=json.dumps(players),
            starting_fen=starting_fen,
            created_at=now,
            updated_at=now,
        )

        with Session(self.engine) as session:
            session.add(game)
            session.commit()
            session.refresh(game)

        return self._to_model(game)

    def add_move(
        self,
        game_id: str,
        move: MoveRecordModel,
    ) -> GameRecordModel:
        """Add a move to a game."""
        validate_game_id(game_id)
        validate_fen(move.fen_after)

        with Session(self.engine) as session:
            game = session.get(GameRecord, game_id)
            if not game:
                raise ValueError(f"Game {game_id} not found")

            db_move = MoveRecord(
                game_id=game_id,
                move_number=move.move_number,
                player_color=move.player_color,
                dice_value=move.dice_value,
                action=move.action,
                token_index=move.token_index,
                captured=move.captured,
                finished=move.finished,
                fen_after=move.fen_after,
                timestamp=move.timestamp,
            )

            game.total_moves += 1
            game.updated_at = datetime.now()

            session.add(db_move)
            session.add(game)
            session.commit()
            session.refresh(game)

            self._update_position_stats(game_id, move)

            return self._to_model(game)

    def finish_game(
        self,
        game_id: str,
        winner_color: Optional[str],
        termination: str = "normal",
    ) -> GameRecordModel:
        """Mark a game as finished."""
        validate_game_id(game_id)

        with Session(self.engine) as session:
            game = session.get(GameRecord, game_id)
            if not game:
                raise ValueError(f"Game {game_id} not found")

            game.winner_color = winner_color
            game.termination = termination
            game.result = f"{winner_color} wins" if winner_color else "Draw"
            game.updated_at = datetime.now()

            session.add(game)
            session.commit()
            session.refresh(game)

            return self._to_model(game)

    def get_game(self, game_id: str) -> Optional[GameRecordModel]:
        """Get a game by ID."""
        validate_game_id(game_id)

        with Session(self.engine) as session:
            game = session.get(GameRecord, game_id)
            return self._to_model(game) if game else None

    def query_games(
        self,
        player_name: Optional[str] = None,
        result: Optional[str] = None,
        min_moves: Optional[int] = None,
        max_moves: Optional[int] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[GameRecordModel]:
        """Query games with filters."""
        validate_query_limit(limit)
        validate_query_offset(offset)

        with Session(self.engine) as session:
            statement = select(GameRecord)

            if player_name:
                statement = statement.where(GameRecord.players.contains(player_name))
            if result:
                statement = statement.where(GameRecord.result == result)
            if min_moves is not None:
                statement = statement.where(GameRecord.total_moves >= min_moves)
            if max_moves is not None:
                statement = statement.where(GameRecord.total_moves <= max_moves)

            statement = statement.order_by(GameRecord.created_at.desc())
            statement = statement.offset(offset).limit(limit)

            games = session.exec(statement).all()
            return [self._to_model(g) for g in games]

    def _update_position_stats(self, game_id: str, move: MoveRecordModel):
        """Update statistics for a position."""
        pos_hash = self._position_hash(move.fen_after)
        now = datetime.now()

        with Session(self.engine) as session:
            stats = session.get(PositionStats, pos_hash)

            if not stats:
                stats = PositionStats(
                    position_hash=pos_hash,
                    fen=move.fen_after,
                    first_game_id=game_id,
                    first_seen=now,
                )

            stats.times_reached += 1
            stats.last_game_id = game_id
            stats.last_seen = now

            session.add(stats)
            session.commit()

    def get_position_stats(self, fen: str) -> Optional[PositionStatsModel]:
        """Get statistics for a position."""
        validate_fen(fen)
        pos_hash = self._position_hash(fen)
        with Session(self.engine) as session:
            stats = session.get(PositionStats, pos_hash)
            if not stats:
                return None

            return PositionStatsModel(
                fen=stats.fen,
                position_hash=stats.position_hash,
                times_reached=stats.times_reached,
                wins=json.loads(stats.wins),
                draws=stats.draws,
                losses=json.loads(stats.losses),
                moves_played=json.loads(stats.moves_played),
                move_wins=json.loads(stats.move_wins),
                first_game_id=stats.first_game_id,
                last_game_id=stats.last_game_id,
                first_seen=stats.first_seen,
                last_seen=stats.last_seen,
            )

    def get_stats_summary(self) -> Dict:
        """Get database statistics."""
        with Session(self.engine) as session:
            total_games = len(session.exec(select(GameRecord)).all())
            total_positions = len(session.exec(select(PositionStats)).all())
            games = session.exec(select(GameRecord)).all()
            total_moves = sum(g.total_moves for g in games)

            return {
                "total_games": total_games,
                "total_positions": total_positions,
                "total_moves": total_moves,
            }

    def _to_model(self, game: GameRecord) -> GameRecordModel:
        """Convert SQLModel to dataclass model."""
        with Session(self.engine) as session:
            moves = session.exec(
                select(MoveRecord).where(MoveRecord.game_id == game.game_id)
            ).all()

            move_models = [
                MoveRecordModel(
                    move_number=m.move_number,
                    player_color=m.player_color,
                    dice_value=m.dice_value,
                    action=m.action,
                    token_index=m.token_index,
                    captured=m.captured,
                    finished=m.finished,
                    fen_after=m.fen_after,
                    timestamp=m.timestamp,
                )
                for m in moves
            ]

            return GameRecordModel(
                game_id=game.game_id,
                event=game.event,
                site=game.site,
                date=game.date,
                players=json.loads(game.players),
                player_ratings=json.loads(game.player_ratings),
                result=game.result,
                winner_color=game.winner_color,
                termination=game.termination,
                starting_fen=game.starting_fen,
                moves=move_models,
                time_control=game.time_control,
                total_moves=game.total_moves,
                duration_seconds=game.duration_seconds,
                captures=json.loads(game.captures),
                tokens_finished=json.loads(game.tokens_finished),
                created_at=game.created_at,
                updated_at=game.updated_at,
            )


# Global database instance
_db: Optional[GameDatabase] = None


def get_database() -> GameDatabase:
    """Get or create the global database instance."""
    global _db
    if _db is None:
        _db = GameDatabase()
    return _db


__all__ = ["GameDatabase", "get_database"]
