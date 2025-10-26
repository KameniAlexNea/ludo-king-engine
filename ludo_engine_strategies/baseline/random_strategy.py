"""Baseline random strategy adapted for the simplified engine."""

from __future__ import annotations

from random import Random
from typing import Optional

from ludo_engine.game import DecisionFn, Game

from ..base import StrategyAdapter, StrategyContext


class RandomStrategy(StrategyAdapter):
    def select_move(self, context: StrategyContext):
        moves = list(context.moves)
        if not moves:
            return None
        return self.rng().choice(moves)


def build(game: Game, seed: Optional[int] = None) -> DecisionFn:
    rng = Random(seed) if seed is not None else None
    return RandomStrategy(game, rng=rng).as_decision_fn()


__all__ = ["RandomStrategy", "build"]
