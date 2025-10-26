"""Structured defensive strategy with light block awareness."""

from __future__ import annotations

from typing import Optional

from ludo_engine_simple.game import DecisionFn, Game
from ludo_engine_simple.strategy import StrategicMove, StrategicWeights

from ..base import StrategyAdapter, StrategyContext


class DefensiveStrategy(StrategyAdapter):
    def __init__(self, game: Game) -> None:
        weights = StrategicWeights(
            progress=1.0,
            enter_bonus=10.0,
            capture_bonus=32.0,
            safe_bonus=16.0,
            finish_bonus=108.0,
            unsafe_penalty=9.0,
        )
        super().__init__(game, weights=weights)

    def select_move(self, context: StrategyContext) -> Optional[StrategicMove]:
        moves = list(context.moves)
        if not moves:
            return None

        finish = next((m for m in moves if m.will_finish), None)
        if finish:
            return finish

        safe_captures = [m for m in moves if m.will_capture and m.is_safe]
        if safe_captures:
            return max(safe_captures, key=lambda m: m.score)

        safe_moves = [m for m in moves if m.is_safe]
        if safe_moves:
            return max(safe_moves, key=lambda m: (m.score, -m.distance_to_finish))

        # Last resort: pick the move with the mildest exposure (furthest distance)
        return max(moves, key=lambda m: (-m.distance_to_finish, m.score))


def build(game: Game) -> DecisionFn:
    return DefensiveStrategy(game).as_decision_fn()


__all__ = ["DefensiveStrategy", "build"]
