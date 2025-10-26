"""Player representation for the simplified Ludo engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List

from .constants import CONFIG
from .token import Token


@dataclass
class Player:
    """Encapsulates player state and provides helpers for tokens."""

    color: str
    tokens: List[Token] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.tokens:
            self.tokens = [
                Token(self.color, i) for i in range(CONFIG.tokens_per_player)
            ]

    def ready_tokens(self) -> Iterable[Token]:
        return (token for token in self.tokens if token.is_ready())

    def home_tokens(self) -> Iterable[Token]:
        return (
            token
            for token in self.tokens
            if token.board_index is None and not token.finished
        )

    def finished_count(self) -> int:
        return sum(1 for token in self.tokens if token.finished)

    def has_won(self) -> bool:
        return self.finished_count() == CONFIG.tokens_per_player
