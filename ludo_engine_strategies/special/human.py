"""Interactive human-in-the-loop strategy for the simplified engine."""

from __future__ import annotations

from typing import Optional, Sequence

from ludo_engine.game import Decision, DecisionFn, Game

from ..strategic_computer import StrategicMove, StrategicValueComputer


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


def build(game: Game = None) -> DecisionFn:
    def decide(game: Game, dice_value: int) -> Optional[Decision]:
        # Compute strategic values by observing game state
        computer = StrategicValueComputer(game)
        evaluation = computer.evaluate(dice_value)

        player_view = evaluation.players[game.current_player_index]
        enriched = player_view.moves

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
