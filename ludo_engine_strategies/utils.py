"""Small helpers shared by minimalist strategies."""

from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

from ludo_engine_simple.strategy import StrategicMove


def split_safety(
    moves: Sequence[StrategicMove],
) -> Tuple[List[StrategicMove], List[StrategicMove]]:
    safe, risky = [], []
    for move in moves:
        (safe if move.is_safe else risky).append(move)
    return safe, risky


def best_by_score(moves: Iterable[StrategicMove]) -> StrategicMove | None:
    moves = list(moves)
    if not moves:
        return None
    return max(moves, key=lambda move: move.score)


__all__ = ["split_safety", "best_by_score"]
