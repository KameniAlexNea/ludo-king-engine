"""Minimal constants used by the simplified Ludo engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass(frozen=True)
class LudoConfig:
    """Centralised configuration for the simplified Ludo game."""

    track_size: int = 52
    home_run: int = 6
    safe_positions: Tuple[int, ...] = (
        0,
        8,
        13,
        21,
        26,
        34,
        39,
        47,
    )
    start_offsets: Dict[str, int] = field(
        default_factory=lambda: {
            "red": 0,
            "green": 13,
            "yellow": 26,
            "blue": 39,
        }
    )
    colors: Tuple[str, ...] = ("red", "green", "yellow", "blue")
    tokens_per_player: int = 4


CONFIG = LudoConfig()
