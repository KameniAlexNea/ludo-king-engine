"""
Strategy factory for creating strategy instances.

This module provides a factory pattern for creating different strategy
implementations, making it easy to instantiate strategies by name.
"""

from typing import Dict, List, Optional, Type

from .advanced import (
    CautiousStrategy,
    OptimistStrategy,
    ProbabilisticStrategy,
    WinnerStrategy,
)
from .base_strategy import BaseStrategy
from .heuristic import (
    BalancedStrategy,
    DefensiveStrategy,
    KillerStrategy,
    RandomStrategy,
)
from .llm import ClaudeStrategy, GPTStrategy, LLMStrategy, LocalLLMStrategy


class StrategyFactory:
    """
    Factory for creating strategy instances.

    Provides a centralized way to create strategy objects by name,
    making it easy to configure games with different AI strategies.
    """

    # Registry of available strategies
    _strategies: Dict[str, Type[BaseStrategy]] = {
        "random": RandomStrategy,
        "killer": KillerStrategy,
        "defensive": DefensiveStrategy,
        "balanced": BalancedStrategy,
        "cautious": CautiousStrategy,
        "optimist": OptimistStrategy,
        "winner": WinnerStrategy,
        "probabilistic": ProbabilisticStrategy,
        "llm": LLMStrategy,
        "gpt": GPTStrategy,
        "claude": ClaudeStrategy,
        "local_llm": LocalLLMStrategy,
    }

    @classmethod
    def create_strategy(cls, strategy_name: str) -> Optional[BaseStrategy]:
        """
        Create a strategy instance by name.

        Args:
            strategy_name: Name of the strategy to create

        Returns:
            Strategy instance, or None if strategy not found
        """
        strategy_name = strategy_name.lower()
        strategy_class = cls._strategies.get(strategy_name)

        if strategy_class:
            return strategy_class()
        return None

    @classmethod
    def get_available_strategies(cls) -> List[str]:
        """Get list of available strategy names."""
        return list(cls._strategies.keys())

    @classmethod
    def register_strategy(cls, name: str, strategy_class: Type[BaseStrategy]):
        """
        Register a new strategy class.

        Args:
            name: Name for the strategy
            strategy_class: Strategy class to register
        """
        cls._strategies[name.lower()] = strategy_class

    @classmethod
    def create_default_strategies(cls) -> Dict[str, BaseStrategy]:
        """Create instances of all default strategies."""
        strategies = {}
        for name in cls._strategies:
            strategy = cls.create_strategy(name)
            if strategy:
                strategies[name] = strategy
        return strategies

    @classmethod
    def create_player_strategies(cls, player_configs: List[Dict]) -> List[BaseStrategy]:
        """
        Create strategies for multiple players.

        Args:
            player_configs: List of player configuration dictionaries
                           Each should have 'strategy' key with strategy name

        Returns:
            List of strategy instances in order
        """
        strategies = []
        for config in player_configs:
            strategy_name = config.get("strategy", "random")
            strategy = cls.create_strategy(strategy_name)
            if strategy is None:
                # Fallback to random if strategy not found
                strategy = RandomStrategy()
            strategies.append(strategy)
        return strategies

    @classmethod
    def get_strategy_info(cls) -> Dict[str, str]:
        """Get information about available strategies."""
        info = {
            "random": "Randomly selects from available moves",
            "killer": "Prioritizes capturing opponent tokens",
            "defensive": "Prioritizes safe moves and protecting tokens",
            "balanced": "Balances offensive and defensive considerations",
            "cautious": "Very conservative strategy that minimizes risk",
            "optimist": "Aggressive strategy that takes calculated risks",
            "winner": "Focuses on getting tokens to finish quickly",
            "probabilistic": "Uses probability calculations for optimal decisions",
            "llm": "LLM-powered strategy with natural language reasoning",
            "gpt": "Strategy using OpenAI GPT models",
            "claude": "Strategy using Anthropic Claude models",
            "local_llm": "Strategy using local LLM models (Ollama, vLLM, etc.)",
        }
        return info

    @classmethod
    def create_tournament_strategies(cls) -> List[BaseStrategy]:
        """Create a diverse set of strategies for tournament play."""
        tournament_strategies = [
            "balanced",
            "killer",
            "defensive",
            "probabilistic",
            "winner",
            "optimist",
            "cautious",
            "random",
        ]

        strategies = []
        for strategy_name in tournament_strategies:
            strategy = cls.create_strategy(strategy_name)
            if strategy:
                strategies.append(strategy)

        return strategies
