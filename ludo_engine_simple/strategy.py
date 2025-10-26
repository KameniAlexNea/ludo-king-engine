"""Strategic value computations for the simplified Ludo engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from .constants import CONFIG
from .game import Decision, DecisionFn, Game
from .player import Player
from .token import Token


@dataclass
class StrategicWeights:
    """Configurable weights applied when scoring moves."""

    progress: float = 1.0
    enter_bonus: float = 12.0
    capture_bonus: float = 35.0
    safe_bonus: float = 8.0
    finish_bonus: float = 100.0
    unsafe_penalty: float = 6.0


@dataclass
class TokenView:
    """Minimal snapshot of a token's state."""

    color: str
    index: int
    board_index: Optional[int]
    steps_taken: int
    finished: bool
    distance_to_finish: int


@dataclass
class StrategicMove:
    """Heuristic-enriched description of a possible move."""

    decision: Decision
    action: str
    token_index: int
    target_index: Optional[int]
    will_capture: bool
    will_finish: bool
    is_safe: bool
    distance_to_finish: int
    score: float


@dataclass
class PlayerView:
    """Aggregated view of a player's tokens and options."""

    index: int
    color: str
    finished_tokens: int
    active_tokens: int
    home_tokens: int
    tokens: List[TokenView]
    moves: List[StrategicMove]


@dataclass
class StrategicEvaluation:
    """Strategic insights for the whole table on a single dice value."""

    dice_value: int
    current_index: int
    players: List[PlayerView]
    recommended: Optional[StrategicMove]


class StrategicValueComputer:
    """Compute lightweight strategic values using the simplified engine state."""

    def __init__(self, game: Game, weights: Optional[StrategicWeights] = None) -> None:
        self._game = game
        self._weights = weights or StrategicWeights()

    def evaluate(
        self, dice_value: int, decision_fn: Optional[DecisionFn] = None
    ) -> StrategicEvaluation:
        current_index = self._game.current_player_index
        players = [
            self._build_player_view(i, dice_value)
            for i in range(len(self._game.players))
        ]

        chooser = decision_fn or self._game.strategies.get(
            self._game.players[current_index].color
        )
        recommended = self._determine_recommendation(
            chooser, dice_value, players, current_index
        )

        return StrategicEvaluation(
            dice_value=dice_value,
            current_index=current_index,
            players=players,
            recommended=recommended,
        )

    def _build_player_view(self, player_index: int, dice_value: int) -> PlayerView:
        player = self._game.players[player_index]
        moves, _ = self._analyse_moves(player, dice_value)
        finished = sum(1 for token in player.tokens if token.finished)
        home = sum(
            1
            for token in player.tokens
            if token.board_index is None and not token.finished
        )
        active = len(player.tokens) - finished - home
        tokens = [self._token_view(token) for token in player.tokens]
        return PlayerView(
            index=player_index,
            color=player.color,
            finished_tokens=finished,
            active_tokens=active,
            home_tokens=home,
            tokens=tokens,
            moves=moves,
        )

    def _token_view(self, token: Token) -> TokenView:
        distance = CONFIG.total_steps - token.steps_taken
        if token.board_index is None and not token.finished:
            distance = CONFIG.total_steps
        if token.finished:
            distance = 0
        return TokenView(
            color=token.color,
            index=token.index,
            board_index=token.board_index,
            steps_taken=token.steps_taken,
            finished=token.finished,
            distance_to_finish=distance,
        )

    def _analyse_moves(
        self, player: Player, dice_value: int
    ) -> Tuple[List[StrategicMove], Dict[Decision, StrategicMove]]:
        decisions = self._game.available_moves(player, dice_value)
        mapping: Dict[Decision, StrategicMove] = {}
        moves: List[StrategicMove] = []

        for decision in decisions:
            action, token_index = decision
            token = player.tokens[token_index]
            target_index, will_finish, steps_after = self._predict_target(
                player, token, action, dice_value
            )
            will_capture = self._predict_capture(player.color, target_index)
            is_safe = will_finish or self._is_safe_square(target_index)
            distance_after = CONFIG.total_steps - steps_after
            distance_before = self._distance_before(token)
            progress = max(0, distance_before - distance_after)
            score = self._score_move(
                action=action,
                progress=progress,
                will_finish=will_finish,
                will_capture=will_capture,
                is_safe=is_safe,
            )
            move = StrategicMove(
                decision=decision,
                action=action,
                token_index=token_index,
                target_index=target_index,
                will_capture=will_capture,
                will_finish=will_finish,
                is_safe=is_safe,
                distance_to_finish=distance_after,
                score=score,
            )
            moves.append(move)
            mapping[decision] = move

        moves.sort(key=lambda move: move.score, reverse=True)
        return moves, mapping

    def _predict_target(
        self,
        player: Player,
        token: Token,
        action: str,
        dice_value: int,
    ) -> Tuple[Optional[int], bool, int]:
        if action == "enter":
            start_index = CONFIG.start_offsets[player.color]
            # Entering does not yet increase steps_taken; treat as zero progress.
            return start_index, False, token.steps_taken

        target_steps = token.steps_taken + dice_value
        if target_steps >= CONFIG.total_steps:
            return None, True, CONFIG.total_steps
        if target_steps >= CONFIG.track_size:
            home_offset = target_steps - CONFIG.track_size
            return CONFIG.home_index(player.color, home_offset), False, target_steps
        start_offset = CONFIG.start_offsets[player.color]
        target_index = (start_offset + target_steps) % CONFIG.track_size
        return target_index, False, target_steps

    def _predict_capture(self, color: str, target_index: Optional[int]) -> bool:
        if target_index is None:
            return False
        if self._is_safe_square(target_index):
            return False
        occupants = self._game.board.occupants(target_index)
        return any(token.color != color for token in occupants)

    def _is_safe_square(self, index: Optional[int]) -> bool:
        if index is None:
            return True
        return index in CONFIG.safe_positions

    def _distance_before(self, token: Token) -> int:
        if token.finished:
            return 0
        if token.board_index is None:
            return CONFIG.total_steps
        return CONFIG.total_steps - token.steps_taken

    def _score_move(
        self,
        *,
        action: str,
        progress: int,
        will_finish: bool,
        will_capture: bool,
        is_safe: bool,
    ) -> float:
        weights = self._weights
        score = float(progress) * weights.progress
        if action == "enter":
            score += weights.enter_bonus
        if will_capture:
            score += weights.capture_bonus
        if is_safe and not will_finish:
            score += weights.safe_bonus
        if will_finish:
            score += weights.finish_bonus
        if not is_safe and not will_finish:
            score -= weights.unsafe_penalty
        return score

    def _determine_recommendation(
        self,
        chooser: Optional[DecisionFn],
        dice_value: int,
        players: Sequence[PlayerView],
        current_index: int,
    ) -> Optional[StrategicMove]:
        if chooser is None:
            return None

        current_player = self._game.players[current_index]
        decisions = [move.decision for move in players[current_index].moves]
        if not decisions:
            return None

        choice = chooser(self._game.players, dice_value, decisions, current_index)
        if choice is None:
            return None

        lookup = {move.decision: move for move in players[current_index].moves}
        return lookup.get(choice)


__all__ = [
    "StrategicWeights",
    "TokenView",
    "StrategicMove",
    "PlayerView",
    "StrategicEvaluation",
    "StrategicValueComputer",
]
