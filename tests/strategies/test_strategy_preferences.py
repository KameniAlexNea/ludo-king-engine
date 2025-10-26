"""Unit tests for specific strategy selection preferences."""

from __future__ import annotations

import unittest

from ludo_engine_simple import Game
from ludo_engine_simple.strategy import StrategicMove
from ludo_engine_strategies.aggressive.killer import KillerStrategy
from ludo_engine_strategies.aggressive.optimist import OptimistStrategy
from ludo_engine_strategies.base import StrategyContext
from ludo_engine_strategies.defensive.cautious import CautiousStrategy
from ludo_engine_strategies.defensive.defensive import DefensiveStrategy
from ludo_engine_strategies.hybrid.balanced import BalancedStrategy
from ludo_engine_strategies.hybrid.winner import WinnerStrategy
from ludo_engine_strategies.probabilistic.hybrid_prob import HybridProbStrategy
from ludo_engine_strategies.probabilistic.probabilistic import ProbabilisticStrategy
from ludo_engine_strategies.probabilistic.probabilistic_v2 import (
    ProbabilisticV2Strategy,
)
from ludo_engine_strategies.probabilistic.probabilistic_v3 import (
    ProbabilisticV3Strategy,
)


def make_move(
    *,
    decision=("advance", 0),
    action="advance",
    token_index=0,
    target_index=None,
    will_capture=False,
    will_finish=False,
    is_safe=False,
    distance_to_finish=20,
    score=10.0,
) -> StrategicMove:
    return StrategicMove(
        decision=decision,
        action=action,
        token_index=token_index,
        target_index=target_index,
        will_capture=will_capture,
        will_finish=will_finish,
        is_safe=is_safe,
        distance_to_finish=distance_to_finish,
        score=score,
    )


class FixedRandom:
    def __init__(self, value: float = 0.0):
        self._value = value

    def random(self) -> float:
        return self._value

    def choice(self, sequence):
        return sequence[0]


class StrategyPreferenceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.game = Game(seed=42)

    def test_balanced_prefers_safe_capture_over_risky(self) -> None:
        strategy = BalancedStrategy(self.game)
        safe_capture = make_move(will_capture=True, is_safe=True, score=32.0)
        risky_progress = make_move(score=35.0, decision=("advance", 1), token_index=1)
        context = StrategyContext(dice_value=5, moves=[risky_progress, safe_capture])
        self.assertIs(strategy.select_move(context), safe_capture)

    def test_killer_prefers_capture(self) -> None:
        killer = KillerStrategy(self.game)
        capture_move = make_move(will_capture=True, score=50.0)
        safe_move = make_move(
            is_safe=True, score=40.0, decision=("advance", 1), token_index=1
        )
        context = StrategyContext(dice_value=4, moves=[safe_move, capture_move])
        self.assertIs(killer.select_move(context), capture_move)

    def test_optimist_prefers_risky_capture(self) -> None:
        optimist = OptimistStrategy(self.game)
        capture_move = make_move(will_capture=True, is_safe=False, score=25.0)
        progress_move = make_move(
            distance_to_finish=8, score=30.0, decision=("advance", 1), token_index=1
        )
        context = StrategyContext(dice_value=5, moves=[capture_move, progress_move])
        self.assertIs(optimist.select_move(context), capture_move)

    def test_cautious_prefers_safe_move(self) -> None:
        cautious = CautiousStrategy(self.game)
        safe_move = make_move(is_safe=True, score=20.0)
        risky_move = make_move(score=30.0, decision=("advance", 1), token_index=1)
        context = StrategyContext(dice_value=2, moves=[risky_move, safe_move])
        self.assertIs(cautious.select_move(context), safe_move)

    def test_defensive_prefers_safe_capture(self) -> None:
        defensive = DefensiveStrategy(self.game)
        safe_capture = make_move(will_capture=True, is_safe=True, score=40.0)
        risky_move = make_move(score=45.0, decision=("advance", 1), token_index=1)
        context = StrategyContext(dice_value=3, moves=[risky_move, safe_capture])
        self.assertIs(defensive.select_move(context), safe_capture)

    def test_winner_prefers_home_stretch(self) -> None:
        winner = WinnerStrategy(self.game)
        home_move = make_move(is_safe=True, distance_to_finish=3, score=25.0)
        far_move = make_move(
            distance_to_finish=12, score=40.0, decision=("advance", 1), token_index=1
        )
        context = StrategyContext(dice_value=2, moves=[far_move, home_move])
        self.assertIs(winner.select_move(context), home_move)

    def test_hybrid_prob_respects_finish_priority(self) -> None:
        strategy = HybridProbStrategy(self.game, temperature=0.5)
        finish_move = make_move(will_finish=True, score=15.0)
        capture_move = make_move(
            will_capture=True, score=60.0, decision=("advance", 1), token_index=1
        )
        context = StrategyContext(dice_value=6, moves=[capture_move, finish_move])
        self.assertIs(strategy.select_move(context), finish_move)

    def test_probabilistic_strategy_biases_high_score(self) -> None:
        strategy = ProbabilisticStrategy(
            self.game,
            temperature=0.2,
            rng=FixedRandom(0.0),
        )
        high = make_move(score=80.0)
        low = make_move(score=10.0, decision=("advance", 1), token_index=1)
        context = StrategyContext(dice_value=4, moves=[high, low])
        self.assertIs(strategy.select_move(context), high)

    def test_probabilistic_v2_prefers_safe_bias(self) -> None:
        strategy = ProbabilisticV2Strategy(
            self.game,
            base_temperature=0.3,
            rng=FixedRandom(0.0),
        )
        safe = make_move(is_safe=True, score=25.0)
        risky = make_move(score=30.0, decision=("advance", 1), token_index=1)
        context = StrategyContext(dice_value=2, moves=[safe, risky])
        self.assertIs(strategy.select_move(context), safe)

    def test_probabilistic_v3_focuses_top_rank(self) -> None:
        strategy = ProbabilisticV3Strategy(
            self.game,
            top_k=1,
            rng=FixedRandom(0.0),
        )
        best = make_move(score=55.0)
        other = make_move(score=30.0, decision=("advance", 1), token_index=1)
        context = StrategyContext(dice_value=3, moves=[best, other])
        self.assertIs(strategy.select_move(context), best)


if __name__ == "__main__":
    unittest.main()
