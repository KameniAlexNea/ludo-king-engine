"""Winner Strategy.

Goal-centric: aggressively converts progress into finished tokens while
maintaining safety. Prefers finishing > deep home advancement > safe captures
> safe progression > exits (only when necessary) > fallback.
"""

from typing import List, Optional, Tuple

from ludo_engine.models.constants import (
    BoardConstants,
    GameConstants,
    StrategyConstants,
)
from ludo_engine.models.model import AIDecisionContext, MoveType, ValidMove
from ludo_engine.strategies.base import Strategy


class WinnerStrategy(Strategy):
    """Victory-focused, safety-aware finishing strategy."""

    def __init__(self):
        super().__init__(
            "Winner",
            "Prioritizes finishing tokens, deep home advancement and safe progression",
        )

    def decide(self, game_context: AIDecisionContext) -> int:
        moves = self._get_valid_moves(game_context)
        if not moves:
            return 0

        player_state = game_context.player_state
        active_tokens = player_state.active_tokens

        # 1. Finish immediately if possible
        finish_move = self._get_move_by_type(moves, MoveType.FINISH)
        if finish_move:
            return finish_move.token_id

        # 2. Home column depth advancement (closest to finish first)
        home_moves = self._get_moves_by_type(moves, MoveType.ADVANCE_HOME_COLUMN)
        if home_moves:
            best_home = max(
                home_moves,
                key=lambda m: (
                    m.target_position,  # deeper is closer
                    m.strategic_value,
                ),
            )
            return best_home.token_id

        # 3. Safe capture of meaningful progress (avoid jeopardizing tokens)
        capture = self._choose_best_capture(moves, game_context)
        if capture is not None:
            return capture

        # 4. Safe forward progression
        safe_moves = self._get_safe_moves(moves)
        if safe_moves:
            # Prefer moves improving proximity to finish (higher strategic value already encodes)
            best_safe = self._get_highest_value_move(safe_moves)
            if best_safe:
                return best_safe.token_id

        # 5. Exit home (only to maintain board presence)
        if active_tokens < StrategyConstants.WINNER_EXIT_MIN_ACTIVE:
            exit_move = self._get_move_by_type(moves, MoveType.EXIT_HOME)
            if exit_move:
                return exit_move.token_id

        # 6. Fallback: highest strategic value overall
        best_move = self._get_highest_value_move(moves)
        return best_move.token_id if best_move else 0

    # --- Helpers ---
    def _choose_best_capture(self, moves: List[ValidMove], game_context: AIDecisionContext) -> Optional[int]:
        """Choose best capture considering both safety and progress value."""
        capture_moves = self._get_capture_moves(moves)
        if not capture_moves:
            return None

        entries = BoardConstants.HOME_COLUMN_ENTRIES
        scored: List[Tuple[float, ValidMove]] = []

        for mv in capture_moves:
            # Calculate progress value from captured tokens
            progress_value = 0.0
            max_progress = 0.0
            for ct in mv.captured_tokens:
                remaining = self._distance_to_finish_proxy(
                    mv.target_position, entries[ct.player_color]
                )
                token_progress = (60 - remaining) * 0.01
                progress_value += token_progress
                max_progress = max(max_progress, token_progress)

            # Base score from progress
            base_score = progress_value * StrategyConstants.WINNER_SAFE_CAPTURE_PROGRESS_WEIGHT

            # Risk assessment for non-safe moves
            risk_penalty = 0.0
            if not mv.is_safe_move:
                # Estimate risk based on opponent proximity
                opponent_positions = []
                for opp in game_context.opponents:
                    opponent_positions.extend(opp.positions_occupied)

                threatening_opponents = 0
                target_pos = mv.target_position
                if isinstance(target_pos, int):
                    for opp_pos in opponent_positions:
                        if isinstance(opp_pos, int) and 0 <= opp_pos < GameConstants.MAIN_BOARD_SIZE:
                            # Distance backward from target to opponent
                            if opp_pos < target_pos:
                                dist = target_pos - opp_pos
                            else:
                                dist = (GameConstants.MAIN_BOARD_SIZE - opp_pos) + target_pos

                            if 1 <= dist <= 6:  # Opponent can reach in 1-6 rolls
                                threatening_opponents += 1

                # Risk penalty based on threat count
                if threatening_opponents > 0:
                    risk_penalty = threatening_opponents * 8.0  # Significant penalty per threat

                # Only accept risky captures if progress value is very high
                if max_progress < 0.4:  # Less than 40% progress toward finish
                    risk_penalty += 100.0  # Effectively disqualify low-value risky captures

            final_score = base_score - risk_penalty
            scored.append((final_score, mv))

        if not scored:
            return None

        # Return the highest scoring capture
        best = max(scored, key=lambda x: x[0])[1]
        return best.token_id

    @staticmethod
    def _distance_to_finish_proxy(position: int, entry: int) -> int:
        if BoardConstants.is_home_column_position(position):
            return GameConstants.FINISH_POSITION - position
        if position <= entry:
            to_entry = entry - position
        else:
            to_entry = (GameConstants.MAIN_BOARD_SIZE - position) + entry
        return to_entry + GameConstants.HOME_COLUMN_SIZE
