"""Softmax-weighted random strategy for the simplified engine."""

from __future__ import annotations

import math
from random import Random
from typing import Optional

from ludo_engine_simple.game import DecisionFn, Game

from ..base import StrategyAdapter, StrategyContext


class WeightedRandomStrategy(StrategyAdapter):
    def __init__(
        self,
        game: Game,
        *,
        temperature: float = 1.0,
        epsilon: float = 0.0,
        rng: Optional[Random] = None,
    ) -> None:
        super().__init__(game, rng=rng)
        self._temperature = max(0.05, temperature)
        self._epsilon = max(0.0, min(1.0, epsilon))

    def select_move(self, context: StrategyContext):
        moves = list(context.moves)
        if not moves:
            return None
        rng = self.rng()
        if rng.random() < self._epsilon:
            return rng.choice(moves)

        scores = [max(move.score, 0.0) for move in moves]
        if max(scores) == 0:
            return rng.choice(moves)
        exp_scores = [math.exp(score / self._temperature) for score in scores]
        total = sum(exp_scores)
        threshold = rng.random() * total
        cumulative = 0.0
        for move, weight in zip(moves, exp_scores):
            cumulative += weight
            if cumulative >= threshold:
                return move
        return moves[-1]


def build(
    game: Game,
    *,
    temperature: float = 1.0,
    epsilon: float = 0.0,
    seed: Optional[int] = None,
) -> DecisionFn:
    rng = Random(seed) if seed is not None else None
    strategy = WeightedRandomStrategy(
        game,
        temperature=temperature,
        epsilon=epsilon,
        rng=rng,
    )
    return strategy.as_decision_fn()


__all__ = ["WeightedRandomStrategy", "build"]
