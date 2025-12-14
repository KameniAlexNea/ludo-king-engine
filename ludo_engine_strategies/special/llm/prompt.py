"""Tiny prompt builder for LLM-assisted strategies."""

from __future__ import annotations

from typing import List

from ludo_engine.strategy import StrategicEvaluation, StrategicMove


def _render_move(move: StrategicMove, index: int) -> str:
    traits: List[str] = []
    if move.will_finish:
        traits.append("finish")
    if move.will_capture:
        traits.append("capture")
    if move.is_safe:
        traits.append("safe")
    traits.append(f"distance={move.distance_to_finish}")
    traits.append(f"score={move.score:.1f}")
    trait_str = ", ".join(traits)
    decision, _ = move.decision
    return f"[{index}] {decision} (token {move.token_index}) -> {trait_str}"


def build_prompt(evaluation: StrategicEvaluation) -> str:
    player = evaluation.players[evaluation.current_index]
    header = [
        "You are an assistant selecting the best Ludo move for the current player.",
        "Consider the dice roll, safety, captures, and distance to finish.",
        "Respond with a single line: `choice: <index>` using one of the listed move indices.",
        "If no move should be played, respond with `choice: none`.",
        "",
        "Game context:",
        f"- Dice roll: {evaluation.dice_value}",
        f"- Current player: {player.color}",
        "",
        "Available moves:",
    ]

    if not player.moves:
        body = ["  (no moves)"]
    else:
        body = ["  " + _render_move(move, idx) for idx, move in enumerate(player.moves)]

    footer = [
        "",
        "Return only the line with `choice: <index>` (or `choice: none`).",
    ]

    return "\n".join(header + body + footer)


__all__ = ["build_prompt"]
