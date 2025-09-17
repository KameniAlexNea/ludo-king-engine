"""
Strategies module - Collection of all available Ludo AI strategies.
"""

from ludo_engine.strategies.aggressive import KillerStrategy, OptimistStrategy
from ludo_engine.strategies.base import Strategy
from ludo_engine.strategies.baseline import RandomStrategy
from ludo_engine.strategies.defensive import CautiousStrategy, DefensiveStrategy
from ludo_engine.strategies.hybrid import BalancedStrategy, WinnerStrategy
from ludo_engine.strategies.probabilistic import (
    HybridConfig,
    HybridProbStrategy,
    ProbabilisticStrategy,
    ProbabilisticV2Strategy,
    ProbabilisticV3Strategy,
    V3Config,
    WeightedRandomStrategy,
)
from ludo_engine.strategies.special import HumanStrategy, LLMStrategy

# Strategy Mapping - Centralized mapping of strategy names to classes
STRATEGIES: dict[str, Strategy] = {
    "human": HumanStrategy,
    "killer": KillerStrategy,
    "winner": WinnerStrategy,
    "optimist": OptimistStrategy,
    "defensive": DefensiveStrategy,
    "balanced": BalancedStrategy,
    "probabilistic": ProbabilisticStrategy,
    "probabilistic_v3": ProbabilisticV3Strategy,
    "probabilistic_v2": ProbabilisticV2Strategy,
    "hybrid_prob": HybridProbStrategy,
    "random": RandomStrategy,
    "weighted_random": WeightedRandomStrategy,
    "cautious": CautiousStrategy,
    "llm": LLMStrategy,
}

__all__ = [
    "Strategy",
    "HumanStrategy",
    "KillerStrategy",
    "WinnerStrategy",
    "OptimistStrategy",
    "DefensiveStrategy",
    "BalancedStrategy",
    "ProbabilisticStrategy",
    "ProbabilisticV2Strategy",
    "ProbabilisticV3Strategy",
    "WeightedRandomStrategy",
    "HybridProbStrategy",
    "RandomStrategy",
    "CautiousStrategy",
    "LLMStrategy",
    "STRATEGIES",
    "V3Config",
    "HybridConfig",
]
