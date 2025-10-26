"""Late-game strategy that focuses on closing out tokens."""

from __future__ import annotations

from typing import Optional

from ludo_engine_simple.game import DecisionFn, Game
from ludo_engine_simple.strategy import StrategicMove, StrategicWeights

from ..base import StrategyAdapter, StrategyContext


class WinnerStrategy(StrategyAdapter):
    def __init__(self, game: Game) -> None:
        weights = StrategicWeights(
            progress=1.0,
            enter_bonus=9.0,
            capture_bonus=30.0,
            safe_bonus=10.0,
            finish_bonus=140.0,
            unsafe_penalty=6.0,
        )
        super().__init__(game, weights=weights)

    def select_move(self, context: StrategyContext) -> Optional[StrategicMove]:
        moves = list(context.moves)
        if not moves:
            return None

        finish = next((m for m in moves if m.will_finish), None)
        if finish:
            return finish

        # Prefer moves that advance along the home stretch (small distance)
        home_push = [m for m in moves if m.distance_to_finish <= 6]
        if home_push:
            return min(home_push, key=lambda m: (m.distance_to_finish, -m.score))

        safe_moves = [m for m in moves if m.is_safe]
        if safe_moves:
            return min(safe_moves, key=lambda m: (m.distance_to_finish, -m.score))

        return min(moves, key=lambda m: (m.distance_to_finish, -m.score))


def build(game: Game) -> DecisionFn:
    return WinnerStrategy(game).as_decision_fn()


__all__ = ["WinnerStrategy", "build"]
