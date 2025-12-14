"""Baseline strategies built for the simplified engine."""

from .random_strategy import build as build_random
from .weighted_random import build as build_weighted

__all__ = ["build_random", "build_weighted"]
