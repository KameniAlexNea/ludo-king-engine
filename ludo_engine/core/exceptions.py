"""
Custom exception hierarchy for Ludo Engine.

This module defines all custom exceptions used throughout the Ludo Engine
to provide clear, specific error messages and proper error handling.
"""

from typing import Any, Dict, Optional


class LudoEngineError(Exception):
    """Base exception for all Ludo Engine errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class GameConfigurationError(LudoEngineError):
    """Raised when game configuration is invalid."""
    pass


class InvalidPlayerCountError(GameConfigurationError):
    """Raised when number of players is not between 2-4."""

    def __init__(self, player_count: int):
        message = f"Invalid number of players: {player_count}. Ludo requires 2-4 players."
        super().__init__(message, {"player_count": player_count})


class InvalidPlayerColorError(GameConfigurationError):
    """Raised when an invalid player color is provided."""

    def __init__(self, color: Any):
        message = f"Invalid player color: {color}. Must be one of: RED, GREEN, BLUE, YELLOW."
        super().__init__(message, {"color": color})


class GameStateError(LudoEngineError):
    """Raised when game state is invalid or inconsistent."""
    pass


class GameAlreadyOverError(GameStateError):
    """Raised when trying to perform actions on a finished game."""

    def __init__(self, winner_color: Optional[str] = None):
        if winner_color:
            message = f"Game is already over. Winner: {winner_color}"
        else:
            message = "Game is already over."
        super().__init__(message, {"winner": winner_color})


class InvalidMoveError(LudoEngineError):
    """Raised when an invalid move is attempted."""
    pass


class NoValidMovesError(InvalidMoveError):
    """Raised when no valid moves are available for current dice roll."""

    def __init__(self, dice_value: int, player_color: str):
        message = f"No valid moves available for player {player_color} with dice roll {dice_value}."
        super().__init__(message, {"dice_value": dice_value, "player_color": player_color})


class InvalidTokenSelectionError(InvalidMoveError):
    """Raised when trying to move an invalid token."""

    def __init__(self, token_id: int, reason: str):
        message = f"Invalid token selection (ID: {token_id}): {reason}"
        super().__init__(message, {"token_id": token_id, "reason": reason})


class BlockedPathError(InvalidMoveError):
    """Raised when token path is blocked by opponent tokens."""

    def __init__(self, position: int, blocking_player: str):
        message = f"Path blocked at position {position} by {blocking_player}."
        super().__init__(message, {"position": position, "blocking_player": blocking_player})


class InvalidDiceRollError(LudoEngineError):
    """Raised when dice roll is invalid."""

    def __init__(self, dice_value: Any):
        message = f"Invalid dice roll: {dice_value}. Must be integer between 1-6."
        super().__init__(message, {"dice_value": dice_value})


class StrategyError(LudoEngineError):
    """Raised when strategy-related errors occur."""
    pass


class InvalidStrategyError(StrategyError):
    """Raised when an invalid strategy is provided."""

    def __init__(self, strategy_name: str, available_strategies: list):
        message = f"Invalid strategy '{strategy_name}'. Available: {available_strategies}"
        super().__init__(message, {
            "strategy_name": strategy_name,
            "available_strategies": available_strategies
        })


class StrategyExecutionError(StrategyError):
    """Raised when strategy execution fails."""

    def __init__(self, strategy_name: str, error: str):
        message = f"Strategy '{strategy_name}' execution failed: {error}"
        super().__init__(message, {"strategy_name": strategy_name, "error": error})


class ValidationError(LudoEngineError):
    """Raised when input validation fails."""
    pass


class TokenValidationError(ValidationError):
    """Raised when token validation fails."""

    def __init__(self, token_id: int, validation_error: str):
        message = f"Token validation failed (ID: {token_id}): {validation_error}"
        super().__init__(message, {"token_id": token_id, "validation_error": validation_error})


class BoardValidationError(ValidationError):
    """Raised when board state validation fails."""

    def __init__(self, position: int, validation_error: str):
        message = f"Board validation failed at position {position}: {validation_error}"
        super().__init__(message, {"position": position, "validation_error": validation_error})


class ConfigurationError(LudoEngineError):
    """Raised when configuration is invalid."""
    pass


class MissingConfigurationError(ConfigurationError):
    """Raised when required configuration is missing."""

    def __init__(self, config_key: str):
        message = f"Missing required configuration: {config_key}"
        super().__init__(message, {"config_key": config_key})


class InvalidConfigurationError(ConfigurationError):
    """Raised when configuration value is invalid."""

    def __init__(self, config_key: str, value: Any, expected: str):
        message = f"Invalid configuration for '{config_key}': {value}. Expected: {expected}"
        super().__init__(message, {
            "config_key": config_key,
            "value": value,
            "expected": expected
        })


class ResourceError(LudoEngineError):
    """Raised when resource-related errors occur."""
    pass


class MemoryLimitExceededError(ResourceError):
    """Raised when memory usage exceeds configured limits."""

    def __init__(self, current_usage: int, limit: int):
        message = f"Memory limit exceeded: {current_usage} > {limit}"
        super().__init__(message, {"current_usage": current_usage, "limit": limit})


class TimeoutError(LudoEngineError):
    """Raised when operations timeout."""

    def __init__(self, operation: str, timeout_seconds: float):
        message = f"Operation '{operation}' timed out after {timeout_seconds} seconds"
        super().__init__(message, {"operation": operation, "timeout_seconds": timeout_seconds})


class SerializationError(LudoEngineError):
    """Raised when serialization/deserialization fails."""
    pass


class GameSerializationError(SerializationError):
    """Raised when game state serialization fails."""

    def __init__(self, error: str):
        message = f"Game serialization failed: {error}"
        super().__init__(message, {"error": error})


class PluginError(LudoEngineError):
    """Raised when plugin-related errors occur."""
    pass


class PluginLoadError(PluginError):
    """Raised when plugin loading fails."""

    def __init__(self, plugin_name: str, error: str):
        message = f"Failed to load plugin '{plugin_name}': {error}"
        super().__init__(message, {"plugin_name": plugin_name, "error": error})


class PluginExecutionError(PluginError):
    """Raised when plugin execution fails."""

    def __init__(self, plugin_name: str, error: str):
        message = f"Plugin '{plugin_name}' execution failed: {error}"
        super().__init__(message, {"plugin_name": plugin_name, "error": error})


class TournamentError(LudoEngineError):
    """Raised when tournament-related errors occur."""
    pass


class InvalidTournamentConfigurationError(TournamentError):
    """Raised when tournament configuration is invalid."""

    def __init__(self, message: str):
        super().__init__(message)


class TournamentStrategyError(TournamentError):
    """Raised when tournament strategy validation fails."""

    def __init__(self, strategy_name: str, available_strategies: list):
        message = f"Tournament strategy '{strategy_name}' not found. Available: {available_strategies}"
        super().__init__(message, {"strategy_name": strategy_name, "available_strategies": available_strategies})