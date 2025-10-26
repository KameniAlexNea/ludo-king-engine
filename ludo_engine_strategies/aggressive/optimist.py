"""High-variance aggressive strategy favouring rapid progress."""

from __future__ import annotations

from typing import Optional

from ludo_engine_simple.game import DecisionFn, Game
from ludo_engine_simple.strategy import StrategicMove, StrategicWeights

from ..base import StrategyAdapter, StrategyContext


class OptimistStrategy(StrategyAdapter):
    def __init__(self, game: Game) -> None:
        weights = StrategicWeights(
            progress=1.25,
            enter_bonus=10.0,
            capture_bonus=45.0,
            safe_bonus=4.0,
            finish_bonus=105.0,
            unsafe_penalty=1.5,
        )
        super().__init__(game, weights=weights)

    def select_move(self, context: StrategyContext) -> Optional[StrategicMove]:
        moves = list(context.moves)
        if not moves:
            return None

        finish = next((m for m in moves if m.will_finish), None)
        if finish:
            return finish

        capture = next(
            (m for m in moves if m.will_capture and not m.is_safe),
            None,
        )
        if capture:
            return capture

        # Prefer the move that pushes the closest token toward finishing,
        # breaking ties by highest score (which already reflects captures/safety).
        best_progress = min(moves, key=lambda m: (m.distance_to_finish, -m.score))
        return best_progress


def build(game: Game) -> DecisionFn:
    return OptimistStrategy(game).as_decision_fn()


__all__ = ["OptimistStrategy", "build"]
