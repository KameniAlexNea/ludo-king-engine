"""Minimal constants used by the simplified Ludo engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass(frozen=True)
class LudoConfig:
    """Centralised configuration for the simplified Ludo game."""

    track_size: int = 52
    home_run: int = 6
    base_safe_positions: Tuple[int, ...] = (
        1,
        8,
        14,
        21,
        27,
        34,
        40,
        47,
    )
    start_offsets: Dict[str, int] = field(
        default_factory=lambda: {
            "red": 1,
            "green": 14,
            "yellow": 27,
            "blue": 40,
        }
    )
    colors: Tuple[str, ...] = ("red", "green", "yellow", "blue")
    tokens_per_player: int = 4
    home_columns: Dict[str, Tuple[int, ...]] = field(init=False)
    home_positions: Tuple[int, ...] = field(init=False)
    safe_positions: Tuple[int, ...] = field(init=False)
    travel_distance: int = field(init=False)
    total_steps: int = field(init=False)

    def __post_init__(self) -> None:
        home_lane = tuple(100 + offset for offset in range(self.home_run))
        columns = {color: home_lane for color in self.colors}
        home_positions = home_lane
        combined_safe = tuple(sorted(set(self.base_safe_positions + home_positions)))
        travel_distance = self.track_size - 1
        total_steps = travel_distance + self.home_run

        object.__setattr__(self, "home_columns", columns)
        object.__setattr__(self, "home_positions", home_positions)
        object.__setattr__(self, "safe_positions", combined_safe)
        object.__setattr__(self, "travel_distance", travel_distance)
        object.__setattr__(self, "total_steps", total_steps)

    def home_index(self, color: str, offset: int) -> int:
        """Resolve a home column index for the given color and offset."""

        return self.home_columns[color][offset]


CONFIG = LudoConfig()
