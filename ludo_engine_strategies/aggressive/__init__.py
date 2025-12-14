"""Aggressive strategy builders."""

from .killer import build as build_killer
from .optimist import build as build_optimist

__all__ = ["build_killer", "build_optimist"]
