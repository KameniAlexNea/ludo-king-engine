"""Minimal strategy adapter layer for the simplified Ludo engine."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import TYPE_CHECKING, Optional

from ludo_engine.game import Decision, DecisionFn

if TYPE_CHECKING:
    from ludo_engine.game import Game

from .strategic_computer import StrategicMove, StrategicValueComputer, StrategicWeights


@dataclass
class StrategyContext:
    """Lightweight container passed to selection hooks."""

    dice_value: int
    current_index: int
    moves: list[StrategicMove]


class StrategyAdapter:
    """Base helper that turns a move-selection policy into a ``DecisionFn``."""

    def __init__(
        self,
        *,
        weights: Optional[StrategicWeights] = None,
        rng: Optional[Random] = None,
    ) -> None:
        self._weights = weights or StrategicWeights()
        self._rng = rng

    @property
    def weights(self) -> StrategicWeights:
        """Expose the strategy's scoring weights."""
        return self._weights

    def as_decision_fn(self) -> DecisionFn:
        """Expose the strategy as a :class:`DecisionFn`."""

        def _decide(
            game: "Game",  # Observe game state
            dice_value: int,
        ) -> Optional[Decision]:
            # Compute strategic values by observing game state
            computer = StrategicValueComputer(game, weights=self._weights)
            evaluation = computer.evaluate(dice_value)

            player_view = evaluation.players[game.current_player_index]

            if not player_view.moves:
                return None

            context = StrategyContext(
                dice_value=dice_value,
                current_index=game.current_player_index,
                moves=player_view.moves,
            )
            chosen = self.select_move(context)
            return chosen.decision if chosen else None

        # Attach strategy instance for introspection
        _decide.strategy = self  # type: ignore
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
