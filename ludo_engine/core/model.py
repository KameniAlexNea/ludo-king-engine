"""
Data models for Ludo game engine.

This module contains data classes that represent the structured output
of the Ludo game engine, providing type safety and clear interfaces.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TokenInfo':
        """Create TokenInfo from dictionary data."""
        return cls(
            id=data.get('id', 0),
            color=data.get('color', ''),
            position=data.get('position', -1),
            steps_taken=data.get('steps_taken', 0),
            is_finished=data.get('is_finished', False),
            is_at_home=data.get('is_at_home', False)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'color': self.color,
            'position': self.position,
            'steps_taken': self.steps_taken,
            'is_finished': self.is_finished,
            'is_at_home': self.is_at_home
        }


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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerStats':
        """Create PlayerStats from dictionary data."""
        return cls(
            color=data.get('color', ''),
            name=data.get('name', ''),
            tokens_finished=data.get('tokens_finished', 0),
            tokens_captured=data.get('tokens_captured', 0),
            total_moves=data.get('total_moves', 0),
            sixes_rolled=data.get('sixes_rolled', 0),
            games_won=data.get('games_won', 0),
            average_turns_per_game=data.get('average_turns_per_game', 0.0)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'color': self.color,
            'name': self.name,
            'tokens_finished': self.tokens_finished,
            'tokens_captured': self.tokens_captured,
            'total_moves': self.total_moves,
            'sixes_rolled': self.sixes_rolled,
            'games_won': self.games_won,
            'average_turns_per_game': self.average_turns_per_game
        }


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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TurnResult':
        """Create TurnResult from dictionary data."""
        return cls(
            player=data.get('player', ''),
            dice_roll=data.get('dice_roll'),
            move_made=data.get('move_made', False),
            token_moved=TokenInfo.from_dict(data['token_moved']) if data.get('token_moved') else None,
            captured_tokens=[TokenInfo.from_dict(t) for t in data.get('captured_tokens', [])],
            finished_tokens=data.get('finished_tokens', 0),
            another_turn=data.get('another_turn', False),
            game_finished=data.get('game_finished', False),
            winner=data.get('winner')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'player': self.player,
            'dice_roll': self.dice_roll,
            'move_made': self.move_made,
            'token_moved': self.token_moved.to_dict() if self.token_moved else None,
            'captured_tokens': [t.to_dict() for t in self.captured_tokens],
            'finished_tokens': self.finished_tokens,
            'another_turn': self.another_turn,
            'game_finished': self.game_finished,
            'winner': self.winner
        }


@dataclass
class GameStateData:
    """Current state of the game."""
    board: Dict[str, Any]
    players: List[PlayerStats]
    current_player: int
    turn_count: int
    game_status: GameStatus
    sixes_in_row: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameStateData':
        """Create GameStateData from dictionary data."""
        return cls(
            board=data.get('board', {}),
            players=[PlayerStats.from_dict(p) for p in data.get('players', [])],
            current_player=data.get('current_player', 0),
            turn_count=data.get('turn_count', 0),
            game_status=GameStatus(data.get('game_state', 'not_started')),
            sixes_in_row=data.get('sixes_in_row', 0)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'board': self.board,
            'players': [p.to_dict() for p in self.players],
            'current_player': self.current_player,
            'turn_count': self.turn_count,
            'game_state': self.game_status.value,
            'sixes_in_row': self.sixes_in_row
        }


@dataclass
class FinalPosition:
    """Final position/ranking of a player."""
    rank: int
    tokens_finished: int
    total_moves: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FinalPosition':
        """Create FinalPosition from dictionary data."""
        return cls(
            rank=data.get('rank', 0),
            tokens_finished=data.get('tokens_finished', 0),
            total_moves=data.get('total_moves', 0)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'rank': self.rank,
            'tokens_finished': self.tokens_finished,
            'total_moves': self.total_moves
        }


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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameResults':
        """Create GameResults from dictionary data."""
        return cls(
            winner=data.get('winner'),
            game_status=GameStatus(data.get('game_state', 'finished')),
            turns_played=data.get('turns_played', 0),
            total_moves=data.get('total_moves', 0),
            dice_rolls=data.get('dice_rolls', 0),
            player_stats=[PlayerStats.from_dict(p) for p in data.get('player_stats', [])],
            final_positions={
                color: FinalPosition.from_dict(pos_data)
                for color, pos_data in data.get('final_positions', {}).items()
            }
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'winner': self.winner,
            'game_state': self.game_status.value,
            'turns_played': self.turns_played,
            'total_moves': self.total_moves,
            'dice_rolls': self.dice_rolls,
            'player_stats': [p.to_dict() for p in self.player_stats],
            'final_positions': {
                color: pos.to_dict() for color, pos in self.final_positions.items()
            }
        }


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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TournamentResult':
        """Create TournamentResult from dictionary data."""
        return cls(
            strategies=data.get('strategies', []),
            rounds=data.get('rounds', 0),
            games_per_round=data.get('games_per_round', 0),
            total_games=data.get('total_games', 0),
            wins=data.get('wins', {}),
            detailed_stats=data.get('detailed_stats', {}),
            win_rates=data.get('win_rates', {})
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'strategies': self.strategies,
            'rounds': self.rounds,
            'games_per_round': self.games_per_round,
            'total_games': self.total_games,
            'wins': self.wins,
            'detailed_stats': self.detailed_stats,
            'win_rates': self.win_rates
        }


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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StrategyComparison':
        """Create StrategyComparison from dictionary data."""
        return cls(
            strategy1=data.get('strategy1', ''),
            strategy2=data.get('strategy2', ''),
            games_played=data.get('games_played', 0),
            strategy1_wins=data.get('strategy1_wins', 0),
            strategy2_wins=data.get('strategy2_wins', 0),
            draws=data.get('draws', 0),
            games=[TurnResult.from_dict(g) for g in data.get('games', [])],
            strategy1_win_rate=data.get('strategy1_win_rate', 0.0),
            strategy2_win_rate=data.get('strategy2_win_rate', 0.0),
            draw_rate=data.get('draw_rate', 0.0)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'strategy1': self.strategy1,
            'strategy2': self.strategy2,
            'games_played': self.games_played,
            'strategy1_wins': self.strategy1_wins,
            'strategy2_wins': self.strategy2_wins,
            'draws': self.draws,
            'games': [g.to_dict() for g in self.games],
            'strategy1_win_rate': self.strategy1_win_rate,
            'strategy2_win_rate': self.strategy2_win_rate,
            'draw_rate': self.draw_rate
        }


@dataclass
class GameAnalysis:
    """Analysis of game results."""
    game_length: int
    efficiency: float
    player_performance: Dict[str, Dict[str, Any]]
    strategy_insights: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameAnalysis':
        """Create GameAnalysis from dictionary data."""
        return cls(
            game_length=data.get('game_length', 0),
            efficiency=data.get('efficiency', 0.0),
            player_performance=data.get('player_performance', {}),
            strategy_insights=data.get('strategy_insights', {})
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'game_length': self.game_length,
            'efficiency': self.efficiency,
            'player_performance': self.player_performance,
            'strategy_insights': self.strategy_insights
        }


@dataclass
class PlayerPositionSummary:
    """Summary of a player's token positions."""
    home: int
    active: int
    finished: int
    total: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerPositionSummary':
        """Create PlayerPositionSummary from dictionary data."""
        return cls(
            home=data.get('home', 0),
            active=data.get('active', 0),
            finished=data.get('finished', 0),
            total=data.get('total', 4)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'home': self.home,
            'active': self.active,
            'finished': self.finished,
            'total': self.total
        }


@dataclass
class PlayerData:
    """Complete player data for serialization."""
    color: str
    name: str
    tokens: List[TokenInfo]
    stats: PlayerStats

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerData':
        """Create PlayerData from dictionary data."""
        return cls(
            color=data.get('color', ''),
            name=data.get('name', ''),
            tokens=[TokenInfo.from_dict(t) for t in data.get('tokens', [])],
            stats=PlayerStats.from_dict(data.get('stats', {}))
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'color': self.color,
            'name': self.name,
            'tokens': [t.to_dict() for t in self.tokens],
            'stats': self.stats.to_dict()
        }