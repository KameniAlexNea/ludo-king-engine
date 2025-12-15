"""Minimal strategy adapter layer for the simplified Ludo engine."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import List, Optional, Sequence

from ludo_engine.game import Decision, DecisionFn, Game
from ludo_engine.strategy import PlayerView, StrategicMove, StrategicValueComputer, StrategicWeights


@dataclass
class StrategyContext:
    """Lightweight container passed to selection hooks."""

    dice_value: int
    players: Sequence[PlayerView]
    current_index: int
    moves: Sequence[StrategicMove]  # Shortcut to players[current_index].moves


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
            players: Sequence[PlayerView],  # Now receives enriched PlayerView data!
            dice_value: int,
            current_index: int,
        ) -> Optional[Decision]:
            # No need to re-compute - we receive enriched data directly
            current = players[current_index]
            context = StrategyContext(
                dice_value=dice_value,
                players=players,
                current_index=current_index,
                moves=current.moves,
            )
            chosen = self.select_move(context)
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
