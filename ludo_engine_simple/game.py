"""Game loop for the simplified Ludo engine."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from .board import Board, MoveResult
from .constants import CONFIG
from .player import Player

Decision = Tuple[str, int]  # (action, token_index)
DecisionFn = Callable[[List[Player], int, Sequence[Decision], int], Optional[Decision]]


@dataclass
class Game:
    seed: Optional[int] = None
    board: Board = field(default_factory=Board)
    players: List[Player] = field(default_factory=lambda: [Player(color) for color in CONFIG.colors])
    current_player_index: int = 0
    history: List[MoveResult] = field(default_factory=list)
    strategies: Dict[str, DecisionFn] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]

    def roll(self) -> int:
        return self._rng.randint(1, 6)

    def available_moves(self, player: Player, dice_value: int) -> List[Decision]:
        moves: List[Decision] = []
        if dice_value == 6:
            moves.extend(("enter", token.index) for token in player.home_tokens())
        for token in player.ready_tokens():
            if token.steps_taken + dice_value <= CONFIG.total_steps:
                moves.append(("advance", token.index))
        return moves

    def execute(self, player: Player, decision: Decision, roll: int) -> MoveResult:
        action, token_index = decision
        token = player.tokens[token_index]
        if action == "enter":
            result = self.board.enter_board(token)
        elif action == "advance":
            result = self.board.advance_token(token, roll)
        else:
            raise ValueError(f"Unknown action: {action}")
        if result.valid:
            self.history.append(result)
        return result

    def play_turn(self, dice_value: int) -> MoveResult:
        player = self.current_player
        moves = self.available_moves(player, dice_value)
        decision: Optional[Decision] = None
        active_decider = self.strategies.get(player.color)
        if moves and active_decider is not None:
            decision = active_decider(self.players, dice_value, moves, self.current_player_index)
        if decision is None and moves:
            decision = moves[0]
        result = MoveResult(player.tokens[moves[0][1]] if moves else player.tokens[0], None, None, message="No move", valid=False)
        if decision:
            result = self.execute(player, decision, dice_value)
        self._advance_turn(dice_value, result)
        return result

    def _advance_turn(self, dice_value: int, result: MoveResult) -> None:
        if not result.valid:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            return

        earned_extra_turn = dice_value == 6 or result.captured is not None or result.finished
        if earned_extra_turn:
            return
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def winner(self) -> Optional[Player]:
        for player in self.players:
            if player.has_won():
                return player
        return None

    def is_finished(self) -> bool:
        return self.winner() is not None
