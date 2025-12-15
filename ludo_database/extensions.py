"""Extended Game API methods for database/web service support."""

from __future__ import annotations

from typing import Dict

from ludo_database.notation import decision_to_notation, fen_to_state, state_to_fen
from ludo_engine.game import Game


def game_to_fen(game: Game) -> str:
    """Export game state as FEN string."""
    return state_to_fen(game)


def game_from_fen(fen: str) -> Game:
    """Create game from FEN string."""
    from ludo_engine.constants import CONFIG
    from ludo_engine.player import Player

    current_player_color, token_lists = fen_to_state(fen)

    players = []
    for i, color in enumerate(CONFIG.colors):
        player = Player(color)
        if i < len(token_lists):
            player.tokens = token_lists[i]
        players.append(player)

    game = Game(players=players)

    # Set current player
    for i, player in enumerate(game.players):
        if player.color == current_player_color:
            game.current_player_index = i
            break

    # Update board state from tokens
    for player in game.players:
        for token in player.tokens:
            if (
                token.board_index is not None
                and token.board_index >= 0
                and not token.finished
            ):
                game.board._positions[token.board_index] = token

    return game


def apply_move_from_notation(
    game: Game, dice: int, move_notation: str
) -> Dict[str, any]:
    """Apply a move from notation and return the result.

    Returns dict with:
      - valid: bool
      - fen_after: str
      - captured: bool
      - finished: bool
      - message: str
    """
    from ludo_database.notation import notation_to_decision

    try:
        decision, expected_dice, _ = notation_to_decision(move_notation)

        # Validate dice matches
        if dice != expected_dice and decision[0] == "advance":
            return {
                "valid": False,
                "fen_after": game_to_fen(game),
                "captured": False,
                "finished": False,
                "message": f"Dice mismatch: expected {expected_dice}, got {dice}",
            }

        # Get current player
        player = game.current_player

        # Execute move
        result = game.execute(player, decision, dice)

        if result.valid:
            # Advance turn
            game._advance_turn(dice, result)

        return {
            "valid": result.valid,
            "fen_after": game_to_fen(game),
            "captured": result.captured is not None,
            "finished": result.finished,
            "message": result.message,
        }

    except Exception as e:
        return {
            "valid": False,
            "fen_after": game_to_fen(game),
            "captured": False,
            "finished": False,
            "message": str(e),
        }


def get_legal_moves_notation(game: Game, dice: int) -> list[str]:
    """Get all legal moves in notation format."""
    player = game.current_player
    decisions = game.available_moves(player, dice)

    return [decision_to_notation(decision, dice) for decision in decisions]


# Extend Game class with convenience methods
Game.to_fen = game_to_fen
Game.from_fen = staticmethod(game_from_fen)
Game.apply_move_from_notation = apply_move_from_notation
Game.get_legal_moves_notation = get_legal_moves_notation


__all__ = [
    "game_to_fen",
    "game_from_fen",
    "apply_move_from_notation",
    "get_legal_moves_notation",
]
