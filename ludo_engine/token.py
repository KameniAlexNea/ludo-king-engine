"""Token model for the simplified Ludo engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Token:
    """Represents a single Ludo token belonging to a player."""

    color: str
    index: int
    board_index: Optional[int] = None  # None means the token is still at home
    steps_taken: int = 0
    finished: bool = False

    def is_ready(self) -> bool:
        return self.board_index is not None and not self.finished

    def send_home(self) -> None:
        self.board_index = None
        self.steps_taken = 0
        self.finished = False

    def mark_finished(self) -> None:
        self.finished = True
        self.board_index = None

    def advance(self, steps: int, track_size: int) -> int:
        if self.board_index is None:
            raise ValueError("Cannot advance a token that is still at home.")
        self.steps_taken += steps
        self.board_index = (self.board_index + steps) % track_size
        return self.board_index
