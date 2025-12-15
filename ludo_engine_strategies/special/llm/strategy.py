"""LLM-friendly strategy hook with sensible fallbacks."""

from __future__ import annotations

from typing import Callable, Optional

from ludo_engine.game import Decision, DecisionFn, Game

from ...strategic_computer import StrategicValueComputer
from .prompt import build_prompt_from_view

Responder = Callable[[str], Optional[str]]


def build(
    game: Game = None,
    responder: Optional[Responder] = None,
    *,
    echo_prompt: bool = False,
) -> DecisionFn:
    """Create a decision function that can defer to an external responder."""

    def decide(game: Game, dice_value: int) -> Optional[Decision]:
        # Compute strategic values by observing game state
        computer = StrategicValueComputer(game)
        evaluation = computer.evaluate(dice_value)

        player_view = evaluation.players[game.current_player_index]

        if not player_view.moves:
            return None

        prompt = build_prompt_from_view(
            evaluation.players, dice_value, game.current_player_index
        )
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
                    if 0 <= idx < len(player_view.moves):
                        chosen_move = player_view.moves[idx]

        if chosen_move is None:
            chosen_move = max(player_view.moves, key=lambda move: move.score)

        if chosen_move.will_finish:
            return chosen_move.decision
        finish = next((move for move in player_view.moves if move.will_finish), None)
        return (finish or chosen_move).decision

    return decide


__all__ = ["build", "Responder"]
