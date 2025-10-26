"""LLM-friendly strategy hook with sensible fallbacks."""

from __future__ import annotations

from typing import Callable, Optional

from ludo_engine_simple.game import DecisionFn, Game
from ludo_engine_simple.strategy import StrategicValueComputer

from .prompt import build_prompt

Responder = Callable[[str], Optional[str]]


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

        chosen_move = None
        if responder is not None:
            raw = responder(prompt)
            if raw is not None:
                parsed = raw.strip().lower()
                if parsed.startswith("choice:"):
                    value = parsed.split("choice:", 1)[1].strip()
                else:
                    value = parsed
                if value == "none":
                    chosen_move = None
                elif value.isdigit():
                    idx = int(value)
                    if 0 <= idx < len(current.moves):
                        chosen_move = current.moves[idx]

        if chosen_move is None:
            chosen_move = max(current.moves, key=lambda move: move.score)

        if chosen_move.will_finish:
            return chosen_move.decision
        finish = next((move for move in current.moves if move.will_finish), None)
        return (finish or chosen_move).decision

    return decide


__all__ = ["build", "Responder"]
