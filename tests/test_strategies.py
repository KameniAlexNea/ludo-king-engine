"""
Unit tests for individual strategy implementations.
Tests cover unique decision logic for each strategy type.
"""

import unittest
from unittest.mock import patch

from ludo_engine.model import AIDecisionContext, ValidMove
from ludo_engine.strategies.balanced import BalancedStrategy
from ludo_engine.strategies.cautious import CautiousStrategy
from ludo_engine.strategies.defensive import DefensiveStrategy
from ludo_engine.strategies.hybrid_prob import HybridProbStrategy
from ludo_engine.strategies.killer import KillerStrategy
from ludo_engine.strategies.optimist import OptimistStrategy
from ludo_engine.strategies.probabilistic import ProbabilisticStrategy
from ludo_engine.strategies.probabilistic_v2 import ProbabilisticV2Strategy
from ludo_engine.strategies.probabilistic_v3 import ProbabilisticV3Strategy
from ludo_engine.strategies.winner import WinnerStrategy


class TestBalancedStrategy(unittest.TestCase):
    """Test cases for BalancedStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = BalancedStrategy()

    def test_initialization(self):
        """Test balanced strategy initialization."""
        self.assertEqual(self.strategy.name, "Balanced")
        self.assertIn("balanced", self.strategy.description.lower())

    def test_decide_balanced_priorities(self):
        """Test balanced strategy decision making."""
        context = AIDecisionContext(
            dice_value=6,
            current_player_id=0,
            valid_moves=[
                ValidMove(token_id=0, current_position=-1, current_state="home",
                         target_position=0, move_type="exit_home", is_safe_move=True,
                         captures_opponent=False, captured_tokens=[], strategic_value=10.0,
                         strategic_components={}),
                ValidMove(token_id=1, current_position=5, current_state="active",
                         target_position=10, move_type="advance_main_board", is_safe_move=False,
                         captures_opponent=True, captured_tokens=[], strategic_value=15.0,
                         strategic_components={}),
                ValidMove(token_id=2, current_position=104, current_state="home_column",
                         target_position=105, move_type="finish", is_safe_move=True,
                         captures_opponent=False, captured_tokens=[], strategic_value=20.0,
                         strategic_components={})
            ],
            game_state={}
        )

        decision = self.strategy.decide(context)
        # Should choose highest strategic value move
        self.assertEqual(decision, 2)


class TestCautiousStrategy(unittest.TestCase):
    """Test cases for CautiousStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = CautiousStrategy()

    def test_initialization(self):
        """Test cautious strategy initialization."""
        self.assertEqual(self.strategy.name, "Cautious")
        self.assertIn("safe", self.strategy.description.lower())

    def test_decide_avoids_risky_moves(self):
        """Test cautious strategy avoids risky moves."""
        context = AIDecisionContext(
            dice_value=4,
            current_player_id=0,
            valid_moves=[
                ValidMove(token_id=0, current_position=5, current_state="active",
                         target_position=10, move_type="advance_main_board", is_safe_move=True,
                         captures_opponent=False, captured_tokens=[], strategic_value=8.0,
                         strategic_components={}),
                ValidMove(token_id=1, current_position=5, current_state="active",
                         target_position=15, move_type="advance_main_board", is_safe_move=False,
                         captures_opponent=False, captured_tokens=[], strategic_value=10.0,
                         strategic_components={})
            ],
            game_state={}
        )

        decision = self.strategy.decide(context)
        # Should choose safe move over risky one
        self.assertEqual(decision, 0)


class TestDefensiveStrategy(unittest.TestCase):
    """Test cases for DefensiveStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = DefensiveStrategy()

    def test_initialization(self):
        """Test defensive strategy initialization."""
        self.assertEqual(self.strategy.name, "Defensive")
        self.assertIn("defensive", self.strategy.description.lower())

    def test_decide_defensive_behavior(self):
        """Test defensive strategy behavior."""
        context = AIDecisionContext(
            dice_value=4,
            current_player_id=0,
            valid_moves=[
                ValidMove(token_id=0, current_position=5, current_state="active",
                         target_position=8, move_type="advance_main_board", is_safe_move=True,
                         captures_opponent=False, captured_tokens=[], strategic_value=8.0,
                         strategic_components={}),
                ValidMove(token_id=1, current_position=5, current_state="active",
                         target_position=10, move_type="advance_main_board", is_safe_move=False,
                         captures_opponent=True, captured_tokens=[], strategic_value=12.0,
                         strategic_components={})
            ],
            game_state={}
        )

        decision = self.strategy.decide(context)
        # Defensive strategy might prioritize safe moves
        self.assertIn(decision, [0, 1])


class TestOptimistStrategy(unittest.TestCase):
    """Test cases for OptimistStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = OptimistStrategy()

    def test_initialization(self):
        """Test optimist strategy initialization."""
        self.assertEqual(self.strategy.name, "Optimist")
        self.assertIn("optimistic", self.strategy.description.lower())

    def test_decide_optimistic_behavior(self):
        """Test optimistic strategy behavior."""
        context = AIDecisionContext(
            dice_value=6,
            current_player_id=0,
            valid_moves=[
                ValidMove(token_id=0, current_position=-1, current_state="home",
                         target_position=0, move_type="exit_home", is_safe_move=True,
                         captures_opponent=False, captured_tokens=[], strategic_value=10.0,
                         strategic_components={}),
                ValidMove(token_id=1, current_position=5, current_state="active",
                         target_position=11, move_type="advance_main_board", is_safe_move=False,
                         captures_opponent=False, captured_tokens=[], strategic_value=15.0,
                         strategic_components={})
            ],
            game_state={}
        )

        decision = self.strategy.decide(context)
        # Optimist might take more aggressive moves
        self.assertIn(decision, [0, 1])


class TestProbabilisticStrategy(unittest.TestCase):
    """Test cases for ProbabilisticStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = ProbabilisticStrategy()

    def test_initialization(self):
        """Test probabilistic strategy initialization."""
        self.assertEqual(self.strategy.name, "Probabilistic")
        self.assertIn("probabilistic", self.strategy.description.lower())

    def test_decide_probabilistic_behavior(self):
        """Test probabilistic strategy decision making."""
        context = AIDecisionContext(
            dice_value=4,
            current_player_id=0,
            valid_moves=[
                ValidMove(token_id=0, current_position=5, current_state="active",
                         target_position=9, move_type="advance_main_board", is_safe_move=False,
                         captures_opponent=False, captured_tokens=[], strategic_value=5.0,
                         strategic_components={}),
                ValidMove(token_id=1, current_position=5, current_state="active",
                         target_position=9, move_type="advance_main_board", is_safe_move=True,
                         captures_opponent=False, captured_tokens=[], strategic_value=8.0,
                         strategic_components={})
            ],
            game_state={}
        )

        decision = self.strategy.decide(context)
        self.assertIn(decision, [0, 1])


class TestProbabilisticV2Strategy(unittest.TestCase):
    """Test cases for ProbabilisticV2Strategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = ProbabilisticV2Strategy()

    def test_initialization(self):
        """Test probabilistic v2 strategy initialization."""
        self.assertEqual(self.strategy.name, "ProbabilisticV2")
        self.assertIn("probabilistic", self.strategy.description.lower())

    def test_decide_v2_behavior(self):
        """Test probabilistic v2 strategy decision making."""
        context = AIDecisionContext(
            dice_value=6,
            current_player_id=0,
            valid_moves=[
                ValidMove(token_id=0, current_position=-1, current_state="home",
                         target_position=0, move_type="exit_home", is_safe_move=True,
                         captures_opponent=False, captured_tokens=[], strategic_value=10.0,
                         strategic_components={}),
                ValidMove(token_id=1, current_position=10, current_state="active",
                         target_position=16, move_type="advance_main_board", is_safe_move=False,
                         captures_opponent=True, captured_tokens=[], strategic_value=15.0,
                         strategic_components={})
            ],
            game_state={}
        )

        decision = self.strategy.decide(context)
        self.assertIn(decision, [0, 1])


class TestProbabilisticV3Strategy(unittest.TestCase):
    """Test cases for ProbabilisticV3Strategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = ProbabilisticV3Strategy()

    def test_initialization(self):
        """Test probabilistic v3 strategy initialization."""
        self.assertEqual(self.strategy.name, "ProbabilisticV3")
        self.assertIn("advanced", self.strategy.description.lower())

    def test_decide_v3_behavior(self):
        """Test probabilistic v3 strategy decision making."""
        context = AIDecisionContext(
            dice_value=4,
            current_player_id=0,
            valid_moves=[
                ValidMove(token_id=0, current_position=5, current_state="active",
                         target_position=9, move_type="advance_main_board", is_safe_move=True,
                         captures_opponent=False, captured_tokens=[], strategic_value=12.0,
                         strategic_components={"exit_home": 0.0, "finish": 0.0, "home_column_depth": 0.0,
                                             "forward_progress": 4.0, "acceleration": 2.0, "safety": 3.0, "vulnerability_penalty": 0.0}),
                ValidMove(token_id=1, current_position=5, current_state="active",
                         target_position=9, move_type="advance_main_board", is_safe_move=False,
                         captures_opponent=False, captured_tokens=[], strategic_value=8.0,
                         strategic_components={"exit_home": 0.0, "finish": 0.0, "home_column_depth": 0.0,
                                             "forward_progress": 4.0, "acceleration": 2.0, "safety": 0.0, "vulnerability_penalty": -2.0})
            ],
            game_state={}
        )

        decision = self.strategy.decide(context)
        self.assertIn(decision, [0, 1])


class TestHybridProbStrategy(unittest.TestCase):
    """Test cases for HybridProbStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = HybridProbStrategy()

    def test_initialization(self):
        """Test hybrid probabilistic strategy initialization."""
        self.assertEqual(self.strategy.name, "HybridProb")
        self.assertIn("hybrid", self.strategy.description.lower())

    def test_decide_hybrid_behavior(self):
        """Test hybrid probabilistic strategy decision making."""
        context = AIDecisionContext(
            dice_value=6,
            current_player_id=0,
            valid_moves=[
                ValidMove(token_id=0, current_position=-1, current_state="home",
                         target_position=0, move_type="exit_home", is_safe_move=True,
                         captures_opponent=False, captured_tokens=[], strategic_value=10.0,
                         strategic_components={}),
                ValidMove(token_id=1, current_position=15, current_state="active",
                         target_position=21, move_type="advance_main_board", is_safe_move=False,
                         captures_opponent=True, captured_tokens=[], strategic_value=18.0,
                         strategic_components={})
            ],
            game_state={}
        )

        decision = self.strategy.decide(context)
        self.assertIn(decision, [0, 1])


class TestKillerStrategyAdvanced(unittest.TestCase):
    """Advanced test cases for KillerStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = KillerStrategy()

    def test_score_capture_move_high_value(self):
        """Test scoring of high-value capture moves."""
        # This would test the internal _score_capture_move method
        # Since it's private, we'll test through the public interface
        context = AIDecisionContext(
            dice_value=4,
            current_player_id=0,
            valid_moves=[
                ValidMove(token_id=0, current_position=5, current_state="active",
                         target_position=10, move_type="advance_main_board", is_safe_move=False,
                         captures_opponent=True, captured_tokens=[], strategic_value=15.0,
                         strategic_components={}),
                ValidMove(token_id=1, current_position=5, current_state="active",
                         target_position=15, move_type="advance_main_board", is_safe_move=False,
                         captures_opponent=False, captured_tokens=[], strategic_value=8.0,
                         strategic_components={})
            ],
            game_state={}
        )

        decision = self.strategy.decide(context)
        # Killer should prioritize captures
        self.assertEqual(decision, 0)


class TestWinnerStrategyAdvanced(unittest.TestCase):
    """Advanced test cases for WinnerStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = WinnerStrategy()

    def test_prioritize_finish_over_capture(self):
        """Test that winner strategy prioritizes finishing over capturing."""
        context = AIDecisionContext(
            dice_value=1,
            current_player_id=0,
            valid_moves=[
                ValidMove(token_id=0, current_position=104, current_state="home_column",
                         target_position=105, move_type="finish", is_safe_move=True,
                         captures_opponent=False, captured_tokens=[], strategic_value=25.0,
                         strategic_components={}),
                ValidMove(token_id=1, current_position=5, current_state="active",
                         target_position=10, move_type="advance_main_board", is_safe_move=False,
                         captures_opponent=True, captured_tokens=[], strategic_value=20.0,
                         strategic_components={}),
                ValidMove(token_id=2, current_position=-1, current_state="home",
                         target_position=0, move_type="exit_home", is_safe_move=True,
                         captures_opponent=False, captured_tokens=[], strategic_value=15.0,
                         strategic_components={})
            ],
            game_state={}
        )

        decision = self.strategy.decide(context)
        # Should choose finish move
        self.assertEqual(decision, 0)


class TestStrategyComparison(unittest.TestCase):
    """Test cases comparing different strategies."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategies = {
            'killer': KillerStrategy(),
            'winner': WinnerStrategy(),
            'balanced': BalancedStrategy(),
            'cautious': CautiousStrategy(),
            'optimist': OptimistStrategy(),
            'probabilistic': ProbabilisticStrategy(),
            'probabilistic_v2': ProbabilisticV2Strategy(),
            'probabilistic_v3': ProbabilisticV3Strategy(),
            'hybrid_prob': HybridProbStrategy(),
            'defensive': DefensiveStrategy()
        }

    def test_all_strategies_can_decide(self):
        """Test that all strategies can make decisions."""
        context = AIDecisionContext(
            dice_value=6,
            current_player_id=0,
            valid_moves=[
                ValidMove(token_id=0, current_position=-1, current_state="home",
                         target_position=0, move_type="exit_home", is_safe_move=True,
                         captures_opponent=False, captured_tokens=[], strategic_value=10.0,
                         strategic_components={}),
                ValidMove(token_id=1, current_position=5, current_state="active",
                         target_position=11, move_type="advance_main_board", is_safe_move=False,
                         captures_opponent=True, captured_tokens=[], strategic_value=15.0,
                         strategic_components={})
            ],
            game_state={}
        )

        for name, strategy in self.strategies.items():
            with self.subTest(strategy=name):
                decision = strategy.decide(context)
                self.assertIn(decision, [0, 1])

    def test_strategy_names_and_descriptions(self):
        """Test that all strategies have proper names and descriptions."""
        for name, strategy in self.strategies.items():
            with self.subTest(strategy=name):
                self.assertIsInstance(strategy.name, str)
                self.assertGreater(len(strategy.name), 0)
                self.assertIsInstance(strategy.description, str)
                self.assertGreater(len(strategy.description), 0)


if __name__ == '__main__':
    unittest.main()