"""Tiny prompt builder for LLM-assisted strategies."""

from __future__ import annotations

from typing import List

from ludo_engine_simple.strategy import StrategicEvaluation, StrategicMove


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
    lines = [
        f"Dice: {evaluation.dice_value}",
        f"Player: {player.color}",
        "Moves:",
    ]
    if not player.moves:
        lines.append("  (no moves)")
    else:
        for idx, move in enumerate(player.moves):
            lines.append("  " + _render_move(move, idx))
    return "\n".join(lines)


__all__ = ["build_prompt"]
