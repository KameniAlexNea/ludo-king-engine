"""
Configuration management for Ludo tournament system.

This module handles loading configuration from environment variables
and .env files for flexible tournament setup.
"""

from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from ludo_engine_strategies import available_strategies


class TournamentConfig(BaseSettings):
    """Configuration class for tournament settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Tournament settings
    tournament_max_turns: int = Field(default=200, alias="TOURNAMENT_MAX_TURNS")
    tournament_games_per_match: int = Field(
        default=10, alias="TOURNAMENT_GAMES_PER_MATCH"
    )
    tournament_seed: Optional[int] = Field(default=None, alias="TOURNAMENT_SEED")

    # Strategy settings
    default_strategies: List[str] = Field(
        default_factory=lambda: available_strategies(include_special=False),
        alias="DEFAULT_STRATEGIES",
    )

    # Game settings
    game_max_consecutive_sixes: int = Field(
        default=3, alias="GAME_MAX_CONSECUTIVE_SIXES"
    )

    # Debug settings
    verbose_logging: bool = Field(default=True, alias="VERBOSE_LOGGING")
    enable_profiling: bool = Field(default=False, alias="ENABLE_PROFILING")

    # Backward compatibility properties
    @property
    def max_turns(self) -> int:
        return self.tournament_max_turns

    @property
    def games_per_match(self) -> int:
        return self.tournament_games_per_match

    @property
    def seed(self) -> Optional[int]:
        return self.tournament_seed

    @property
    def max_consecutive_sixes(self) -> int:
        return self.game_max_consecutive_sixes


# Global configuration instance
config = TournamentConfig()
