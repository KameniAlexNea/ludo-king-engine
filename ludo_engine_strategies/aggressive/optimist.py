"""High-variance aggressive strategy favouring rapid progress."""

from __future__ import annotations

from typing import Optional

from ludo_engine.game import DecisionFn, Game

from ..base import StrategyAdapter, StrategyContext
from ..strategic_computer import StrategicMove, StrategicWeights


class OptimistStrategy(StrategyAdapter):
    def __init__(self) -> None:
        weights = StrategicWeights(
            progress=1.25,
            enter_bonus=10.0,
            capture_bonus=45.0,
            safe_bonus=4.0,
            finish_bonus=105.0,
            unsafe_penalty=1.5,
        )
        super().__init__(weights=weights)

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


def build(game: Game = None) -> DecisionFn:
    return OptimistStrategy().as_decision_fn()


__all__ = ["OptimistStrategy", "build"]
