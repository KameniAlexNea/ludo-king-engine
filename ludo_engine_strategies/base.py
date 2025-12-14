"""Minimal strategy adapter layer for the simplified Ludo engine."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import List, Optional, Sequence

from ludo_engine.game import Decision, DecisionFn, Game
from ludo_engine.strategy import StrategicMove, StrategicValueComputer, StrategicWeights


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

        def _no_recommendation(
            players: List,
            dice_value: int,
            moves: Sequence[Decision],
            current_index: int,
        ) -> Optional[Decision]:
            _ = players, dice_value, moves, current_index
            return None

        def _decide(
            players: List,  # unused – kept for compatibility with DecisionFn signature
            dice_value: int,
            moves: Sequence[Decision],
            current_index: int,
        ) -> Optional[Decision]:
            _ = players, moves  # the strategic view already recomputes enriched moves
            # Important: pass an explicit decision_fn so StrategicValueComputer does not
            # fall back to game.strategies (which would call back into this DecisionFn).
            evaluation = self._computer.evaluate(
                dice_value, decision_fn=_no_recommendation
            )
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
