"""Hybrid probabilistic strategy mixing deterministic priorities with sampling."""

from __future__ import annotations

import math
from random import Random
from typing import Optional

from ludo_engine_simple.game import DecisionFn, Game
from ludo_engine_simple.strategy import StrategicMove, StrategicWeights

from ..base import StrategyAdapter, StrategyContext


class HybridProbStrategy(StrategyAdapter):
    def __init__(
        self,
        game: Game,
        *,
        temperature: float = 0.9,
        rng: Optional[Random] = None,
    ) -> None:
        weights = StrategicWeights(
            progress=1.05,
            enter_bonus=12.0,
            capture_bonus=44.0,
            safe_bonus=13.0,
            finish_bonus=115.0,
            unsafe_penalty=6.5,
        )
        super().__init__(game, weights=weights, rng=rng)
        self._temperature = max(0.1, temperature)

    def select_move(self, context: StrategyContext) -> Optional[StrategicMove]:
        moves = list(context.moves)
        if not moves:
            return None

        finish = next((m for m in moves if m.will_finish), None)
        if finish:
            return finish

        # Always respect a strong safe capture to keep behaviour sharp.
        safe_capture = next((m for m in moves if m.will_capture and m.is_safe), None)
        if safe_capture:
            return safe_capture

        scores = [max(move.score, 0.0) for move in moves]
        max_score = max(scores)
        if max_score <= 0:
            return self.rng().choice(moves)

        exp_scores = [math.exp((score - max_score) / self._temperature) for score in scores]
        total = sum(exp_scores)
        threshold = self.rng().random() * total
        cumulative = 0.0
        for move, weight in zip(moves, exp_scores):
            cumulative += weight
            if cumulative >= threshold:
                return move
        return moves[-1]


def build(game: Game, *, temperature: float = 0.9, seed: Optional[int] = None) -> DecisionFn:
    rng = Random(seed) if seed is not None else None
    strategy = HybridProbStrategy(game, temperature=temperature, rng=rng)
    return strategy.as_decision_fn()


__all__ = ["HybridProbStrategy", "build"]
