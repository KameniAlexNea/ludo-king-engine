"""Strategy factory for the simplified engine."""

from __future__ import annotations

from typing import Callable, Dict, Iterable, List

from ludo_engine.game import DecisionFn, Game

from .aggressive import build_killer, build_optimist
from .baseline import build_random, build_weighted
from .defensive import build_cautious, build_defensive
from .hybrid import build_balanced, build_winner
from .probabilistic import (
    build_hybrid_prob,
    build_probabilistic,
    build_probabilistic_v2,
    build_probabilistic_v3,
)
from .special import build_human, build_llm

StrategyBuilder = Callable[[Game], DecisionFn]


def _with_kwargs(builder: Callable, game: Game, **kwargs) -> DecisionFn:
    return builder(game, **kwargs)


STRATEGY_BUILDERS: Dict[str, Callable[..., DecisionFn]] = {
    "random": build_random,
    "weighted_random": build_weighted,
    "killer": build_killer,
    "optimist": build_optimist,
    "cautious": build_cautious,
    "defensive": build_defensive,
    "balanced": build_balanced,
    "winner": build_winner,
    "probabilistic": build_probabilistic,
    "probabilistic_v2": build_probabilistic_v2,
    "probabilistic_v3": build_probabilistic_v3,
    "hybrid_prob": build_hybrid_prob,
    "human": build_human,
    "llm": build_llm,
}


def available_strategies(*, include_special: bool = True) -> List[str]:
    names: Iterable[str] = STRATEGY_BUILDERS.keys()
    if not include_special:
        names = [name for name in names if name not in {"human", "llm"}]
    return sorted(names)


def build_strategy(name: str, game: Game, **kwargs) -> DecisionFn:
    key = name.lower()
    if key not in STRATEGY_BUILDERS:
        available = ", ".join(sorted(STRATEGY_BUILDERS))
        raise ValueError(f"Unknown strategy '{name}'. Available: {available}")
    builder = STRATEGY_BUILDERS[key]
    return _with_kwargs(builder, game, **kwargs)


__all__ = ["available_strategies", "build_strategy", "STRATEGY_BUILDERS"]
