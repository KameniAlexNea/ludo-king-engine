"""LLM-friendly strategy hook with sensible fallbacks."""

from __future__ import annotations

from typing import Callable, Optional

from ludo_engine_simple.game import DecisionFn, Game
from ludo_engine_simple.strategy import StrategicValueComputer

from .prompt import build_prompt

Responder = Callable[[str], Optional[int]]


def build(
    game: Game,
    responder: Optional[Responder] = None,
    *,
    echo_prompt: bool = False,
) -> DecisionFn:
    """Create a decision function that can defer to an external responder."""

    computer = StrategicValueComputer(game)

    def decide(players, dice_value, moves, current_index):
        _ = players, moves
        evaluation = computer.evaluate(dice_value)
        current = evaluation.players[current_index]
        if not current.moves:
            return None

        prompt = build_prompt(evaluation)
        if echo_prompt:
            print(prompt)

        if responder is not None:
            choice = responder(prompt)
            if choice is not None and 0 <= choice < len(current.moves):
                return current.moves[choice].decision

        # Fallbacks: prefer finish, otherwise top-scoring move
        finish = next((move for move in current.moves if move.will_finish), None)
        return (finish or current.moves[0]).decision

    return decide


__all__ = ["build", "Responder"]
