"""
Strategic decision-making system for Ludo AI.
Strategy factory and main interface.
"""

from typing import Dict, List

from ludo_engine.strategies import STRATEGIES, Strategy


# Strategy Factory
class StrategyFactory:
    """Factory class for creating strategy instances."""

    _strategies = STRATEGIES

    @classmethod
    def create_strategy(cls, strategy_name: str) -> Strategy:
        """
        Create a strategy instance by name.

        Args:
            strategy_name: Name of the strategy to create

        Returns:
            Strategy: Instance of the requested strategy

        Raises:
            ValueError: If strategy name is not recognized
        """
        strategy_name = strategy_name.lower()
        if strategy_name not in cls._strategies:
            available = list(cls._strategies.keys())
            raise ValueError(
                f"Unknown strategy '{strategy_name}'. Available: {available}"
            )

        return cls._strategies[strategy_name]()

    @classmethod
    def get_available_strategies(cls, avoid_llm=True, avoid_human=False) -> List[str]:
        """Get list of available strategy names."""
        return [
            name
            for name in cls._strategies.keys()
            if not (("llm" in name and avoid_llm) or ("human" in name and avoid_human))
        ]

    @classmethod
    def get_strategy_descriptions(
        cls, avoid_llm=True, avoid_human=False
    ) -> Dict[str, str]:
        """Get descriptions of all available strategies."""
        descriptions = {}
        for name, strategy_class in cls._strategies.items():
            if avoid_llm and "llm" in name:
                continue
            if avoid_human and "human" in name:
                continue
            strategy = strategy_class()
            descriptions[name] = strategy.description
        return descriptions
