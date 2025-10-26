"""Interactive human-in-the-loop strategy for the simplified engine."""

from __future__ import annotations

from typing import Sequence

from ludo_engine_simple.game import DecisionFn, Game
from ludo_engine_simple.strategy import StrategicMove, StrategicValueComputer


def _render_choices(moves: Sequence[StrategicMove]) -> str:
    lines = ["Available moves:"]
    for idx, move in enumerate(moves):
        decision, target = move.decision, move.target_index
        details = []
        if move.will_finish:
            details.append("finish")
        if move.will_capture:
            details.append("capture")
        if move.is_safe:
            details.append("safe")
        lines.append(
            f"  [{idx}] {decision} -> {target if target is not None else 'home'} | score={move.score:.1f} | "
            + ", ".join(details)
        )
    return "\n".join(lines)


def build(game: Game) -> DecisionFn:
    computer = StrategicValueComputer(game)

    def decide(players, dice_value, moves, current_index):
        _ = players, moves
        evaluation = computer.evaluate(dice_value)
        current = evaluation.players[current_index]
        enriched = current.moves
        if not enriched:
            print("No moves available.")
            return None

        print(_render_choices(enriched))
        while True:
            raw = input("Select move index (empty to cancel): ").strip()
            if not raw:
                return None
            if raw.isdigit():
                idx = int(raw)
                if 0 <= idx < len(enriched):
                    return enriched[idx].decision
            print("Invalid choice. Try again.")

    return decide


__all__ = ["build"]
