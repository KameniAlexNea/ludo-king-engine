"""Balanced strategy blending progress and safety."""

from __future__ import annotations

from typing import Optional

from ludo_engine_simple.game import DecisionFn, Game
from ludo_engine_simple.strategy import StrategicMove, StrategicWeights

from ..base import StrategyAdapter, StrategyContext


class BalancedStrategy(StrategyAdapter):
    def __init__(self, game: Game) -> None:
        weights = StrategicWeights(
            progress=1.05,
            enter_bonus=11.0,
            capture_bonus=36.0,
            safe_bonus=12.0,
            finish_bonus=108.0,
            unsafe_penalty=7.5,
        )
        super().__init__(game, weights=weights)

    def select_move(self, context: StrategyContext) -> Optional[StrategicMove]:
        moves = list(context.moves)
        if not moves:
            return None

        finish = next((m for m in moves if m.will_finish), None)
        if finish:
            return finish

        safe_capture = next((m for m in moves if m.will_capture and m.is_safe), None)
        if safe_capture:
            return safe_capture

        # Slight bias towards safe moves but willing to take the top-rated risky move
        safe_moves = [m for m in moves if m.is_safe]
        if safe_moves:
            best_safe = max(safe_moves, key=lambda m: m.score)
            best_overall = max(moves, key=lambda m: m.score)
            if best_overall.is_safe or best_overall.score <= best_safe.score + 4:
                return best_safe
            return best_overall

        return max(moves, key=lambda m: m.score)


def build(game: Game) -> DecisionFn:
    return BalancedStrategy(game).as_decision_fn()


__all__ = ["BalancedStrategy", "build"]
