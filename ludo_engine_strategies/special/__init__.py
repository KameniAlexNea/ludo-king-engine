"""Special strategy helpers."""

from .human import build as build_human
from .llm.strategy import build as build_llm

__all__ = ["build_human", "build_llm"]
