"""
Configuration management for Ludo tournament system.

This module handles loading configuration from environment variables
and .env files for flexible tournament setup.
"""

import os
from typing import List, Optional


class TournamentConfig:
    """Configuration class for tournament settings."""

    def __init__(self):
        # Load .env file if it exists
        self._load_env_file()

        # Tournament settings
        self.max_turns = self._get_int_env("TOURNAMENT_MAX_TURNS", 200)
        self.games_per_match = self._get_int_env("TOURNAMENT_GAMES_PER_MATCH", 1)
        self.seed = self._get_int_env("TOURNAMENT_SEED", None)

        # Strategy settings
        self.default_strategies = self._get_list_env(
            "DEFAULT_STRATEGIES",
            [
                "random",
                "killer",
                "defensive",
                "balanced",
                "cautious",
                "optimist",
                "winner",
                "probabilistic",
            ],
        )

        # Game settings
        self.max_consecutive_sixes = self._get_int_env("GAME_MAX_CONSECUTIVE_SIXES", 3)

        # Debug settings
        self.verbose_logging = self._get_bool_env("VERBOSE_LOGGING", True)
        self.enable_profiling = self._get_bool_env("ENABLE_PROFILING", False)

    def _load_env_file(self):
        """Load environment variables from .env file if it exists."""
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip()
                            # Only set if not already set in environment
                            if key not in os.environ:
                                os.environ[key] = value

    def _get_int_env(self, key: str, default: Optional[int]) -> Optional[int]:
        """Get integer environment variable with default."""
        value = os.getenv(key)
        if value is None:
            return default
        if value.lower() in ("none", "null", ""):
            return None
        try:
            return int(value)
        except ValueError:
            print(f"Warning: Invalid integer value for {key}: {value}")
            return default

    def _get_bool_env(self, key: str, default: bool) -> bool:
        """Get boolean environment variable with default."""
        value = os.getenv(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")

    def _get_list_env(self, key: str, default: List[str]) -> List[str]:
        """Get list environment variable with default."""
        value = os.getenv(key)
        if value is None:
            return default
        if value.lower() in ("none", "null", ""):
            return default
        return [item.strip() for item in value.split(",") if item.strip()]

    def get_tournament_kwargs(self) -> dict:
        """Get tournament constructor arguments from config."""
        kwargs = {
            "games_per_match": self.games_per_match,
            "max_turns": self.max_turns,
        }
        if self.seed is not None:
            kwargs["seed"] = self.seed
        return kwargs

    def __repr__(self) -> str:
        """String representation of configuration."""
        return (
            f"TournamentConfig("
            f"max_turns={self.max_turns}, "
            f"games_per_match={self.games_per_match}, "
            f"seed={self.seed}, "
            f"default_strategies={self.default_strategies}, "
            f"verbose_logging={self.verbose_logging})"
        )


# Global configuration instance
config = TournamentConfig()
