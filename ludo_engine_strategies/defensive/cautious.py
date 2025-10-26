"""Cautious defensive strategy that prefers safe incremental progress."""

from __future__ import annotations

from typing import Optional

from ludo_engine_simple.game import DecisionFn, Game
from ludo_engine_simple.strategy import StrategicMove, StrategicWeights

from ..base import StrategyAdapter, StrategyContext


class CautiousStrategy(StrategyAdapter):
    def __init__(self, game: Game) -> None:
        weights = StrategicWeights(
            progress=0.9,
            enter_bonus=14.0,
            capture_bonus=28.0,
            safe_bonus=14.0,
            finish_bonus=110.0,
            unsafe_penalty=12.0,
        )
        super().__init__(game, weights=weights)

    def select_move(self, context: StrategyContext) -> Optional[StrategicMove]:
        moves = list(context.moves)
        if not moves:
            return None

        finish = next((m for m in moves if m.will_finish), None)
        if finish:
            return finish

        safe_moves = [m for m in moves if m.is_safe]
        if safe_moves:
            return max(safe_moves, key=lambda m: (m.score, -m.distance_to_finish))

        # No safe options: fall back to the move that keeps the token furthest from danger
        # by preferring larger distance to finish (less exposed) with score as tiebreaker.
        return max(moves, key=lambda m: (-m.distance_to_finish, m.score))


def build(game: Game) -> DecisionFn:
    return CautiousStrategy(game).as_decision_fn()


__all__ = ["CautiousStrategy", "build"]
