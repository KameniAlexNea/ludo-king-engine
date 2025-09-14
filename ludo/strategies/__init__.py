"""
Strategies module - Collection of all available Ludo AI strategies.
"""

from .balanced import BalancedStrategy
from .base import Strategy
from .cautious import CautiousStrategy
from .defensive import DefensiveStrategy
from .killer import KillerStrategy
from .llm import LLMStrategy
from .optimist import OptimistStrategy
from .probabilistic import ProbabilisticStrategy
from .random_strategy import RandomStrategy
from .weighted_random import WeightedRandomStrategy
from .winner import WinnerStrategy
from .gpt_strategy import GPTStrategy
from .claude_strategy import ClaudeStrategy
from .local_llm_strategy import LocalLLMStrategy

# Strategy Mapping - Centralized mapping of strategy names to classes
STRATEGIES: dict[str, Strategy] = {
    "killer": KillerStrategy,
    "winner": WinnerStrategy,
    "optimist": OptimistStrategy,
    "defensive": DefensiveStrategy,
    "balanced": BalancedStrategy,
    "probabilistic": ProbabilisticStrategy,
    "random": RandomStrategy,
    "weighted_random": WeightedRandomStrategy,
    "cautious": CautiousStrategy,
    "llm": LLMStrategy,
    "gpt": GPTStrategy,
    "claude": ClaudeStrategy,
    "local_llm": LocalLLMStrategy,
}

__all__ = [
    "Strategy",
    "KillerStrategy",
    "WinnerStrategy",
    "OptimistStrategy",
    "DefensiveStrategy",
    "BalancedStrategy",
    "ProbabilisticStrategy",
    "RandomStrategy",
    "WeightedRandomStrategy",
    "CautiousStrategy",
    "LLMStrategy",
    "GPTStrategy",
    "ClaudeStrategy",
    "LocalLLMStrategy",
    "STRATEGIES",
]
