"""Probabilistic strategy using softmax over strategic scores."""

from __future__ import annotations

import math
from random import Random
from typing import Optional

from ludo_engine.game import DecisionFn, Game
from ludo_engine.strategy import StrategicMove, StrategicWeights

from ..base import StrategyAdapter, StrategyContext


class ProbabilisticStrategy(StrategyAdapter):
    def __init__(
        self,
        game: Game,
        *,
        temperature: float = 1.1,
        rng: Optional[Random] = None,
    ) -> None:
        weights = StrategicWeights(
            progress=1.05,
            enter_bonus=11.0,
            capture_bonus=38.0,
            safe_bonus=11.0,
            finish_bonus=110.0,
            unsafe_penalty=7.5,
        )
        super().__init__(game, weights=weights, rng=rng)
        self._temperature = max(0.1, temperature)

    def select_move(self, context: StrategyContext) -> Optional[StrategicMove]:
        moves = list(context.moves)
        if not moves:
            return None
        scores = [move.score for move in moves]
        max_score = max(scores)
        if max_score <= 0:
            return self.rng().choice(moves)
        exp_scores = [
            math.exp((score - max_score) / self._temperature) for score in scores
        ]
        total = sum(exp_scores)
        threshold = self.rng().random() * total
        cumulative = 0.0
        for move, weight in zip(moves, exp_scores):
            cumulative += weight
            if cumulative >= threshold:
                return move
        return moves[-1]


def build(
    game: Game, *, temperature: float = 1.1, seed: Optional[int] = None
) -> DecisionFn:
    rng = Random(seed) if seed is not None else None
    strategy = ProbabilisticStrategy(game, temperature=temperature, rng=rng)
    return strategy.as_decision_fn()


__all__ = ["ProbabilisticStrategy", "build"]
