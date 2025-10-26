"""Minimal strategy adapter layer for the simplified Ludo engine."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import List, Optional, Sequence

from ludo_engine_simple.game import Decision, DecisionFn, Game
from ludo_engine_simple.strategy import (
    StrategicMove,
    StrategicValueComputer,
    StrategicWeights,
)


@dataclass
class StrategyContext:
    """Lightweight container passed to selection hooks."""

    dice_value: int
    moves: Sequence[StrategicMove]


class StrategyAdapter:
    """Base helper that turns a move-selection policy into a ``DecisionFn``."""

    def __init__(
        self,
        game: Game,
        *,
        weights: Optional[StrategicWeights] = None,
        rng: Optional[Random] = None,
    ) -> None:
        self._game = game
        self._computer = StrategicValueComputer(game, weights=weights)
        self._rng = rng

    def as_decision_fn(self) -> DecisionFn:
        """Expose the strategy as a :class:`DecisionFn`."""

        def _decide(
            players: List,  # unused – kept for compatibility with DecisionFn signature
            dice_value: int,
            moves: Sequence[Decision],
            current_index: int,
        ) -> Optional[Decision]:
            _ = players, moves  # the strategic view already recomputes enriched moves
            evaluation = self._computer.evaluate(dice_value)
            current = evaluation.players[current_index]
            chosen = self.select_move(StrategyContext(dice_value, current.moves))
            return chosen.decision if chosen else None

        return _decide

    # API surface subclasses care about -------------------------------------------------
    def rng(self) -> Random:
        if self._rng is None:
            self._rng = Random()
        return self._rng

    def select_move(self, context: StrategyContext) -> Optional[StrategicMove]:
        """Pick a move. Subclasses must override."""

        raise NotImplementedError


__all__ = ["StrategyAdapter", "StrategyContext"]
