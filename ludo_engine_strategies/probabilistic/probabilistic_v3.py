"""Third iteration probabilistic strategy favouring top candidates with recency bias."""

from __future__ import annotations

from random import Random
from typing import Optional

from ludo_engine_simple.game import DecisionFn, Game
from ludo_engine_simple.strategy import StrategicMove, StrategicWeights

from ..base import StrategyAdapter, StrategyContext


class ProbabilisticV3Strategy(StrategyAdapter):
    def __init__(
        self,
        game: Game,
        *,
        top_k: int = 3,
        rng: Optional[Random] = None,
    ) -> None:
        weights = StrategicWeights(
            progress=1.1,
            enter_bonus=11.0,
            capture_bonus=42.0,
            safe_bonus=12.0,
            finish_bonus=115.0,
            unsafe_penalty=6.5,
        )
        super().__init__(game, weights=weights, rng=rng)
        self._top_k = max(1, top_k)

    def select_move(self, context: StrategyContext) -> Optional[StrategicMove]:
        moves = list(context.moves)
        if not moves:
            return None

        top = moves[: self._top_k]
        weights = []
        for index, move in enumerate(top, start=1):
            safety = 1.2 if move.is_safe else 1.0
            capture = 1.3 if move.will_capture else 1.0
            finish = 1.6 if move.will_finish else 1.0
            weight = safety * capture * finish / index
            weights.append(weight)

        total = sum(weights)
        if total <= 0:
            return self.rng().choice(top)
        threshold = self.rng().random() * total
        cumulative = 0.0
        for move, weight in zip(top, weights):
            cumulative += weight
            if cumulative >= threshold:
                return move
        return top[-1]


def build(
    game: Game,
    *,
    top_k: int = 3,
    seed: Optional[int] = None,
) -> DecisionFn:
    rng = Random(seed) if seed is not None else None
    strategy = ProbabilisticV3Strategy(game, top_k=top_k, rng=rng)
    return strategy.as_decision_fn()


__all__ = ["ProbabilisticV3Strategy", "build"]
