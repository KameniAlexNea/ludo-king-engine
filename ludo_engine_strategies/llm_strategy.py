"""Convenience wrappers around the minimalist LLM strategy hook."""

from __future__ import annotations

import os
from typing import Optional

from ludo_engine_simple.game import DecisionFn, Game

from .special.llm import Responder
from .special.llm import build as build_llm


def build_ollama_strategy(
    game: Game,
    *,
    responder: Optional[Responder] = None,
    model_name: Optional[str] = None,
    echo_prompt: bool = False,
) -> DecisionFn:
    _ = model_name or os.getenv("LLM_MODEL", "gpt-oss")
    return build_llm(game, responder=responder, echo_prompt=echo_prompt)


def build_groq_strategy(
    game: Game,
    *,
    responder: Optional[Responder] = None,
    model_name: Optional[str] = None,
    echo_prompt: bool = False,
) -> DecisionFn:
    _ = model_name or os.getenv("LLM_MODEL", "gpt-oss")
    return build_llm(game, responder=responder, echo_prompt=echo_prompt)


__all__ = ["build_ollama_strategy", "build_groq_strategy"]
