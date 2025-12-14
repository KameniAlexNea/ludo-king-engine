"""Second iteration probabilistic strategy with safety-aware weights."""

from __future__ import annotations

import math
from random import Random
from typing import Optional

from ludo_engine.game import DecisionFn, Game
from ludo_engine.strategy import StrategicMove, StrategicWeights

from ..base import StrategyAdapter, StrategyContext


class ProbabilisticV2Strategy(StrategyAdapter):
    def __init__(
        self,
        game: Game,
        *,
        base_temperature: float = 1.0,
        rng: Optional[Random] = None,
    ) -> None:
        weights = StrategicWeights(
            progress=1.0,
            enter_bonus=12.0,
            capture_bonus=40.0,
            safe_bonus=13.0,
            finish_bonus=112.0,
            unsafe_penalty=8.0,
        )
        super().__init__(game, weights=weights, rng=rng)
        self._base_temperature = max(0.1, base_temperature)

    def select_move(self, context: StrategyContext) -> Optional[StrategicMove]:
        moves = list(context.moves)
        if not moves:
            return None

        # Adjust temperature based on dice: high rolls encourage boldness.
        temperature = self._base_temperature * (0.8 if context.dice_value <= 3 else 1.1)
        adjustments = []
        for move in moves:
            safety_bias = 4.0 if move.is_safe else -2.0
            capture_bias = 3.0 if move.will_capture else 0.0
            finish_bias = 6.0 if move.will_finish else 0.0
            adjustments.append(move.score + safety_bias + capture_bias + finish_bias)

        max_adj = max(adjustments)
        if max_adj <= 0:
            return self.rng().choice(moves)

        exp_scores = [math.exp((adj - max_adj) / temperature) for adj in adjustments]
        total = sum(exp_scores)
        threshold = self.rng().random() * total
        cumulative = 0.0
        for move, weight in zip(moves, exp_scores):
            cumulative += weight
            if cumulative >= threshold:
                return move
        return moves[-1]


def build(
    game: Game,
    *,
    base_temperature: float = 1.0,
    seed: Optional[int] = None,
) -> DecisionFn:
    rng = Random(seed) if seed is not None else None
    strategy = ProbabilisticV2Strategy(
        game,
        base_temperature=base_temperature,
        rng=rng,
    )
    return strategy.as_decision_fn()


__all__ = ["ProbabilisticV2Strategy", "build"]
