"""Aggressive capture-first strategy tuned for the simplified engine."""

from __future__ import annotations

from typing import Optional

from ludo_engine.game import DecisionFn, Game
from ludo_engine.strategy import StrategicMove, StrategicWeights

from ..base import StrategyAdapter, StrategyContext


class KillerStrategy(StrategyAdapter):
    def __init__(self, game: Game) -> None:
        weights = StrategicWeights(
            progress=1.0,
            enter_bonus=8.0,
            capture_bonus=60.0,
            safe_bonus=6.0,
            finish_bonus=110.0,
            unsafe_penalty=2.5,
        )
        super().__init__(game, weights=weights)

    def select_move(self, context: StrategyContext) -> Optional[StrategicMove]:
        moves = list(context.moves)
        if not moves:
            return None

        finish = next((m for m in moves if m.will_finish), None)
        if finish:
            return finish

        capture_moves = [m for m in moves if m.will_capture]
        if capture_moves:
            return max(
                capture_moves,
                key=lambda m: (m.score, -m.distance_to_finish),
            )

        risky = [m for m in moves if not m.is_safe]
        safe = [m for m in moves if m.is_safe]
        if risky and safe:
            best_safe = max(safe, key=lambda m: m.score)
            best_risky = max(risky, key=lambda m: m.score)
            if best_risky.score >= best_safe.score + 5:
                return best_risky
            return best_safe

        return max(moves, key=lambda m: m.score)


def build(game: Game) -> DecisionFn:
    return KillerStrategy(game).as_decision_fn()


__all__ = ["KillerStrategy", "build"]
