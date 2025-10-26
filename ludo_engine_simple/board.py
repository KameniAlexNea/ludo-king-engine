"""Board handling for the simplified Ludo engine."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import DefaultDict, Dict, Iterable, List, Optional

from .constants import CONFIG
from .token import Token


@dataclass
class MoveResult:
    token: Token
    start: Optional[int]
    end: Optional[int]
    captured: Optional[Token] = None
    finished: bool = False
    message: str = ""
    valid: bool = True


class Board:
    """Tracks token positions on the shared board."""

    def __init__(self) -> None:
        self._positions: DefaultDict[int, List[Token]] = defaultdict(list)

    def occupants(self, index: int) -> List[Token]:
        return list(self._positions.get(index, []))

    def tokens_for_color(self, color: str) -> Iterable[Token]:
        for stack in self._positions.values():
            for token in stack:
                if token.color == color:
                    yield token

    def enter_board(self, token: Token) -> MoveResult:
        if token.finished:
            return MoveResult(token, None, None, message="Token already finished", valid=False)
        if token.board_index is not None:
            return MoveResult(token, token.board_index, token.board_index, message="Token already in play", valid=False)
        start_index = CONFIG.start_offsets[token.color]
        captured = self._pop_capture(start_index, token.color)
        token.board_index = start_index
        token.steps_taken = 0
        self._positions[start_index].append(token)
        message = "Token entered board"
        if captured:
            message += f", captured {captured.color}"
        return MoveResult(token, None, start_index, captured=captured, message=message)

    def advance_token(self, token: Token, steps: int) -> MoveResult:
        if token.finished:
            return MoveResult(token, None, None, message="Token already finished", valid=False)
        if token.board_index is None:
            return MoveResult(token, None, None, message="Token must enter board first", valid=False)
        target_steps = token.steps_taken + steps
        if target_steps > CONFIG.total_steps:
            return MoveResult(
                token,
                token.board_index,
                token.board_index,
                message="Roll too high to finish",
                valid=False,
            )

        start_index = token.board_index
        if target_steps == CONFIG.total_steps:
            self._remove_from_position(start_index, token)
            token.steps_taken = target_steps
            token.mark_finished()
            return MoveResult(token, start_index, None, finished=True, message="Token finished")

        if target_steps >= CONFIG.travel_distance:
            home_offset = target_steps - CONFIG.travel_distance
            new_index = CONFIG.home_index(token.color, home_offset)
        else:
            new_index = self._absolute_index(token.color, target_steps)

        self._remove_from_position(start_index, token)
        token.steps_taken = target_steps
        token.board_index = new_index
        captured = self._pop_capture(new_index, token.color)
        self._positions[new_index].append(token)
        message = f"Moved to {new_index}"
        if captured:
            message += f", captured {captured.color}"
        return MoveResult(token, start_index, new_index, captured=captured, message=message)

    def _remove_from_position(self, index: int, token: Token) -> None:
        stack = self._positions.get(index)
        if not stack:
            return
        stack.remove(token)
        if not stack:
            self._positions.pop(index, None)

    def _pop_capture(self, index: int, color: str) -> Optional[Token]:
        stack = self._positions.get(index)
        if not stack:
            return None
        if index in CONFIG.safe_positions:
            return None
        for candidate in list(stack):
            if candidate.color != color:
                stack.remove(candidate)
                if not stack:
                    self._positions.pop(index, None)
                candidate.send_home()
                return candidate
        return None

    def _absolute_index(self, color: str, steps_taken: int) -> int:
        start = CONFIG.start_offsets[color]
        return (start + steps_taken) % CONFIG.track_size

    def state(self) -> Dict[int, List[str]]:
        """Return a lightweight view of the board for debugging or UI."""
        return {index: [token.color for token in stack] for index, stack in self._positions.items()}
