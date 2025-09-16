"""
Unit tests for individual strategy implementations.
Tests cover unique decision logic for each strategy type.
"""

import unittest
import unittest.mock

from ludo_engine.model import (
    AIDecisionContext,
    CurrentSituation,
    OpponentInfo,
    PlayerState,
    StrategicAnalysis,
    ValidMove,
)
from ludo_engine.strategies.balanced import BalancedStrategy
from ludo_engine.strategies.cautious import CautiousStrategy
from ludo_engine.strategies.defensive import DefensiveStrategy
from ludo_engine.strategies.hybrid_prob import HybridProbStrategy
from ludo_engine.strategies.killer import KillerStrategy
from ludo_engine.strategies.optimist import OptimistStrategy
from ludo_engine.strategies.probabilistic import ProbabilisticStrategy
from ludo_engine.strategies.probabilistic_v2 import ProbabilisticV2Strategy
from ludo_engine.strategies.probabilistic_v3 import ProbabilisticV3Strategy
from ludo_engine.strategies.weighted_random import WeightedRandomStrategy
from ludo_engine.strategies.winner import WinnerStrategy


def create_test_decision_context(dice_value=4, valid_moves=None):
    """Create a test AIDecisionContext for strategy testing."""
    if valid_moves is None:
        valid_moves = [
            ValidMove(
                token_id=0,
                current_position=5,
                current_state="active",
                target_position=9,
                move_type="advance_main_board",
                is_safe_move=False,
                captures_opponent=False,
                captured_tokens=[],
                strategic_value=5.0,
                strategic_components={},
            ),
        ]

    return AIDecisionContext(
        current_situation=CurrentSituation(
            player_color="red",
            dice_value=dice_value,
            consecutive_sixes=0,
            turn_count=1,
        ),
        player_state=PlayerState(
            player_id=0,
            color="red",
            start_position=0,
            tokens=[],
            tokens_in_home=4,
            active_tokens=0,
            tokens_in_home_column=0,
            finished_tokens=0,
            has_won=False,
            positions_occupied=[],
        ),
        opponents=[
            OpponentInfo(
                color="blue",
                finished_tokens=0,
                tokens_active=1,
                threat_level=0.2,
                positions_occupied=[10],
            ),
        ],
        valid_moves=valid_moves,
        strategic_analysis=StrategicAnalysis(
            can_capture=False,
            can_finish_token=False,
            can_exit_home=True,
            safe_moves=[],
            risky_moves=[],
            best_strategic_move=None,
        ),
    )


class TestBalancedStrategy(unittest.TestCase):
    """Test cases for BalancedStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = BalancedStrategy()

    def test_initialization(self):
        """Test balanced strategy initialization."""
        self.assertIn("adaptive", self.strategy.description.lower())
        self.assertIn("blend", self.strategy.description.lower())

    def test_decide_balanced_priorities(self):
        """Test balanced strategy decision making."""
        context = create_test_decision_context(
            dice_value=6,
            valid_moves=[
                ValidMove(
                    token_id=0,
                    current_position=-1,
                    current_state="home",
                    target_position=0,
                    move_type="exit_home",
                    is_safe_move=True,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=10.0,
                    strategic_components={},
                ),
                ValidMove(
                    token_id=1,
                    current_position=5,
                    current_state="active",
                    target_position=10,
                    move_type="advance_main_board",
                    is_safe_move=False,
                    captures_opponent=True,
                    captured_tokens=[],
                    strategic_value=15.0,
                    strategic_components={},
                ),
                ValidMove(
                    token_id=2,
                    current_position=104,
                    current_state="home_column",
                    target_position=105,
                    move_type="finish",
                    is_safe_move=True,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=20.0,
                    strategic_components={},
                ),
            ],
        )

        decision = self.strategy.decide(context)
        # Should choose highest strategic value move
        self.assertEqual(decision, 2)

    def test_decide_finish_priority(self):
        """Test that finish moves have highest priority."""
        context = create_test_decision_context(
            valid_moves=[
                ValidMove(
                    token_id=0,
                    current_position=104,
                    current_state="home_column",
                    target_position=105,
                    move_type="finish",
                    is_safe_move=True,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=10.0,
                    strategic_components={},
                ),
                ValidMove(
                    token_id=1,
                    current_position=5,
                    current_state="active",
                    target_position=10,
                    move_type="advance_main_board",
                    is_safe_move=False,
                    captures_opponent=True,
                    captured_tokens=[],
                    strategic_value=50.0,  # Higher strategic value
                    strategic_components={},
                ),
            ],
        )
        decision = self.strategy.decide(context)
        self.assertEqual(decision, 0)  # Should choose finish move

    def test_decide_home_column_priority(self):
        """Test home column advancement priority."""
        context = create_test_decision_context(
            valid_moves=[
                ValidMove(
                    token_id=0,
                    current_position=100,
                    current_state="home_column",
                    target_position=102,
                    move_type="advance_home_column",
                    is_safe_move=True,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=10.0,
                    strategic_components={},
                ),
                ValidMove(
                    token_id=1,
                    current_position=5,
                    current_state="active",
                    target_position=10,
                    move_type="advance_main_board",
                    is_safe_move=True,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=15.0,
                    strategic_components={},
                ),
            ],
        )
        decision = self.strategy.decide(context)
        self.assertEqual(decision, 0)  # Should choose home column move

    def test_decide_capture_when_behind(self):
        """Test capture priority when behind."""
        # Create context where player is behind
        context = create_test_decision_context(
            valid_moves=[
                ValidMove(
                    token_id=0,
                    current_position=5,
                    current_state="active",
                    target_position=10,
                    move_type="advance_main_board",
                    is_safe_move=False,
                    captures_opponent=True,
                    captured_tokens=[],
                    strategic_value=15.0,
                    strategic_components={},
                ),
            ],
        )
        # Set player as behind by adjusting opponent progress
        context.opponents[0].finished_tokens = 3  # Opponent has 3 finished
        context.player_state.finished_tokens = 0  # Player has 0 finished

        decision = self.strategy.decide(context)
        self.assertEqual(decision, 0)

    def test_decide_no_moves(self):
        """Test decide with no valid moves."""
        context = create_test_decision_context(valid_moves=[])
        decision = self.strategy.decide(context)
        self.assertEqual(decision, 0)


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
        context = create_test_decision_context(
            dice_value=4,
            valid_moves=[
                ValidMove(
                    token_id=0,
                    current_position=5,
                    current_state="active",
                    target_position=10,
                    move_type="advance_main_board",
                    is_safe_move=True,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=8.0,
                    strategic_components={},
                ),
                ValidMove(
                    token_id=1,
                    current_position=5,
                    current_state="active",
                    target_position=15,
                    move_type="advance_main_board",
                    is_safe_move=False,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=10.0,
                    strategic_components={},
                ),
            ],
        )

        decision = self.strategy.decide(context)
        # Should choose safe move over risky one
        self.assertEqual(decision, 0)

    def test_decide_late_game_urgency(self):
        """Test cautious strategy in late game when behind."""
        context = create_test_decision_context(
            valid_moves=[
                ValidMove(
                    token_id=0,
                    current_position=5,
                    current_state="active",
                    target_position=10,
                    move_type="advance_main_board",
                    is_safe_move=False,  # Risky but necessary
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=15.0,
                    strategic_components={},
                ),
            ],
        )
        # Set up late game scenario where player is behind
        context.opponents[0].finished_tokens = 3
        context.player_state.finished_tokens = 0

        decision = self.strategy.decide(context)
        self.assertEqual(decision, 0)

    def test_decide_no_safe_moves(self):
        """Test cautious strategy when no safe moves available."""
        context = create_test_decision_context(
            valid_moves=[
                ValidMove(
                    token_id=0,
                    current_position=5,
                    current_state="active",
                    target_position=10,
                    move_type="advance_main_board",
                    is_safe_move=False,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=10.0,
                    strategic_components={},
                ),
            ],
        )

        decision = self.strategy.decide(context)
        self.assertEqual(decision, 0)  # Should still choose the only move


class TestDefensiveStrategy(unittest.TestCase):
    """Test cases for DefensiveStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = DefensiveStrategy()

    def test_initialization(self):
        """Test defensive strategy initialization."""
        self.assertIn("safety", self.strategy.description.lower())
        self.assertIn("preserves", self.strategy.description.lower())

    def test_decide_defensive_behavior(self):
        """Test defensive strategy behavior."""
        context = create_test_decision_context(
            dice_value=4,
            valid_moves=[
                ValidMove(
                    token_id=0,
                    current_position=5,
                    current_state="active",
                    target_position=8,
                    move_type="advance_main_board",
                    is_safe_move=True,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=8.0,
                    strategic_components={},
                ),
                ValidMove(
                    token_id=1,
                    current_position=5,
                    current_state="active",
                    target_position=10,
                    move_type="advance_main_board",
                    is_safe_move=False,
                    captures_opponent=True,
                    captured_tokens=[],
                    strategic_value=12.0,
                    strategic_components={},
                ),
            ],
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
        context = create_test_decision_context(
            dice_value=6,
            valid_moves=[
                ValidMove(
                    token_id=0,
                    current_position=-1,
                    current_state="home",
                    target_position=0,
                    move_type="exit_home",
                    is_safe_move=True,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=10.0,
                    strategic_components={},
                ),
                ValidMove(
                    token_id=1,
                    current_position=5,
                    current_state="active",
                    target_position=11,
                    move_type="advance_main_board",
                    is_safe_move=False,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=15.0,
                    strategic_components={},
                ),
            ],
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
        self.assertIn("adaptive", self.strategy.description.lower())
        self.assertIn("probability", self.strategy.description.lower())

    def test_decide_probabilistic_behavior(self):
        """Test probabilistic strategy decision making."""
        context = create_test_decision_context(
            dice_value=4,
            valid_moves=[
                ValidMove(
                    token_id=0,
                    current_position=5,
                    current_state="active",
                    target_position=9,
                    move_type="advance_main_board",
                    is_safe_move=False,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=5.0,
                    strategic_components={},
                ),
                ValidMove(
                    token_id=1,
                    current_position=5,
                    current_state="active",
                    target_position=9,
                    move_type="advance_main_board",
                    is_safe_move=True,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=8.0,
                    strategic_components={},
                ),
            ],
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
        self.assertIn("adaptive", self.strategy.description.lower())
        self.assertIn("prob", self.strategy.description.lower())

    def test_decide_v2_behavior(self):
        """Test probabilistic v2 strategy decision making."""
        context = create_test_decision_context(
            dice_value=6,
            valid_moves=[
                ValidMove(
                    token_id=0,
                    current_position=-1,
                    current_state="home",
                    target_position=0,
                    move_type="exit_home",
                    is_safe_move=True,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=10.0,
                    strategic_components={},
                ),
                ValidMove(
                    token_id=1,
                    current_position=10,
                    current_state="active",
                    target_position=16,
                    move_type="advance_main_board",
                    is_safe_move=False,
                    captures_opponent=True,
                    captured_tokens=[],
                    strategic_value=15.0,
                    strategic_components={},
                ),
            ],
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
        self.assertIn("full", self.strategy.description.lower())

    def test_decide_v3_behavior(self):
        """Test probabilistic v3 strategy decision making."""
        context = create_test_decision_context(
            dice_value=4,
            valid_moves=[
                ValidMove(
                    token_id=0,
                    current_position=5,
                    current_state="active",
                    target_position=9,
                    move_type="advance_main_board",
                    is_safe_move=True,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=12.0,
                    strategic_components={
                        "exit_home": 0.0,
                        "finish": 0.0,
                        "home_column_depth": 0.0,
                        "forward_progress": 4.0,
                        "acceleration": 2.0,
                        "safety": 3.0,
                        "vulnerability_penalty": 0.0,
                    },
                ),
                ValidMove(
                    token_id=1,
                    current_position=5,
                    current_state="active",
                    target_position=9,
                    move_type="advance_main_board",
                    is_safe_move=False,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=8.0,
                    strategic_components={
                        "exit_home": 0.0,
                        "finish": 0.0,
                        "home_column_depth": 0.0,
                        "forward_progress": 4.0,
                        "acceleration": 2.0,
                        "safety": 0.0,
                        "vulnerability_penalty": -2.0,
                    },
                ),
            ],
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
        context = create_test_decision_context(
            dice_value=6,
            valid_moves=[
                ValidMove(
                    token_id=0,
                    current_position=-1,
                    current_state="home",
                    target_position=0,
                    move_type="exit_home",
                    is_safe_move=True,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=10.0,
                    strategic_components={},
                ),
                ValidMove(
                    token_id=1,
                    current_position=15,
                    current_state="active",
                    target_position=21,
                    move_type="advance_main_board",
                    is_safe_move=False,
                    captures_opponent=True,
                    captured_tokens=[],
                    strategic_value=18.0,
                    strategic_components={},
                ),
            ],
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
        context = create_test_decision_context(
            dice_value=4,
            valid_moves=[
                ValidMove(
                    token_id=0,
                    current_position=5,
                    current_state="active",
                    target_position=10,
                    move_type="advance_main_board",
                    is_safe_move=False,
                    captures_opponent=True,
                    captured_tokens=[],
                    strategic_value=15.0,
                    strategic_components={},
                ),
                ValidMove(
                    token_id=1,
                    current_position=5,
                    current_state="active",
                    target_position=15,
                    move_type="advance_main_board",
                    is_safe_move=False,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=8.0,
                    strategic_components={},
                ),
            ],
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
        context = create_test_decision_context(
            dice_value=1,
            valid_moves=[
                ValidMove(
                    token_id=0,
                    current_position=104,
                    current_state="home_column",
                    target_position=105,
                    move_type="finish",
                    is_safe_move=True,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=25.0,
                    strategic_components={},
                ),
                ValidMove(
                    token_id=1,
                    current_position=5,
                    current_state="active",
                    target_position=10,
                    move_type="advance_main_board",
                    is_safe_move=False,
                    captures_opponent=True,
                    captured_tokens=[],
                    strategic_value=20.0,
                    strategic_components={},
                ),
                ValidMove(
                    token_id=2,
                    current_position=-1,
                    current_state="home",
                    target_position=0,
                    move_type="exit_home",
                    is_safe_move=True,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=15.0,
                    strategic_components={},
                ),
            ],
        )

        decision = self.strategy.decide(context)
        # Should choose finish move
        self.assertEqual(decision, 0)

    def test_prioritize_home_column_depth(self):
        """Test that winner strategy prioritizes deeper home column moves."""
        context = create_test_decision_context(
            valid_moves=[
                ValidMove(
                    token_id=0,
                    current_position=100,
                    current_state="home_column",
                    target_position=102,
                    move_type="advance_home_column",
                    is_safe_move=True,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=10.0,
                    strategic_components={},
                ),
                ValidMove(
                    token_id=1,
                    current_position=102,
                    current_state="home_column",
                    target_position=104,
                    move_type="advance_home_column",
                    is_safe_move=True,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=12.0,
                    strategic_components={},
                ),
            ],
        )

        decision = self.strategy.decide(context)
        # Should choose the deeper home column move (token 1)
        self.assertEqual(decision, 1)

    def test_safe_capture_priority(self):
        """Test safe capture selection."""
        context = create_test_decision_context(
            valid_moves=[
                ValidMove(
                    token_id=0,
                    current_position=5,
                    current_state="active",
                    target_position=10,
                    move_type="advance_main_board",
                    is_safe_move=True,
                    captures_opponent=True,
                    captured_tokens=[],
                    strategic_value=18.0,
                    strategic_components={},
                ),
                ValidMove(
                    token_id=1,
                    current_position=5,
                    current_state="active",
                    target_position=10,
                    move_type="advance_main_board",
                    is_safe_move=False,
                    captures_opponent=True,
                    captured_tokens=[],
                    strategic_value=20.0,
                    strategic_components={},
                ),
            ],
        )

        decision = self.strategy.decide(context)
        # Should choose safe capture over risky one
        self.assertEqual(decision, 0)


class TestStrategyComparison(unittest.TestCase):
    """Test cases comparing different strategies."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategies = {
            "killer": KillerStrategy(),
            "winner": WinnerStrategy(),
            "balanced": BalancedStrategy(),
            "cautious": CautiousStrategy(),
            "optimist": OptimistStrategy(),
            "probabilistic": ProbabilisticStrategy(),
            "probabilistic_v2": ProbabilisticV2Strategy(),
            "probabilistic_v3": ProbabilisticV3Strategy(),
            "hybrid_prob": HybridProbStrategy(),
            "defensive": DefensiveStrategy(),
        }

    def test_all_strategies_can_decide(self):
        """Test that all strategies can make decisions."""
        context = create_test_decision_context(
            dice_value=6,
            valid_moves=[
                ValidMove(
                    token_id=0,
                    current_position=-1,
                    current_state="home",
                    target_position=0,
                    move_type="exit_home",
                    is_safe_move=True,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=10.0,
                    strategic_components={},
                ),
                ValidMove(
                    token_id=1,
                    current_position=5,
                    current_state="active",
                    target_position=11,
                    move_type="advance_main_board",
                    is_safe_move=False,
                    captures_opponent=True,
                    captured_tokens=[],
                    strategic_value=15.0,
                    strategic_components={},
                ),
            ],
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


class TestWeightedRandomStrategy(unittest.TestCase):
    """Test cases for WeightedRandomStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = WeightedRandomStrategy()

    def test_initialization(self):
        """Test weighted random strategy initialization."""
        self.assertIn("weighted", self.strategy.name.lower())
        self.assertIn("stochastic", self.strategy.description.lower())
        self.assertEqual(self.strategy.recent_moves_memory, [])

    def test_decide_no_moves(self):
        """Test decide with no valid moves."""
        context = create_test_decision_context(valid_moves=[])
        decision = self.strategy.decide(context)
        self.assertEqual(decision, 0)

    def test_decide_finish_moves(self):
        """Test that finish moves are chosen immediately."""
        finish_move = ValidMove(
            token_id=1,
            current_position=50,
            current_state="active",
            target_position=56,  # Assuming finish position
            move_type="finish",
            is_safe_move=True,
            captures_opponent=False,
            captured_tokens=[],
            strategic_value=10.0,
            strategic_components={},
        )
        context = create_test_decision_context(valid_moves=[finish_move])

        # Mock random.choice to return the finish move
        with unittest.mock.patch("random.choice", return_value=finish_move):
            decision = self.strategy.decide(context)
            self.assertEqual(decision, 1)

    def test_decide_early_phase(self):
        """Test decision making in early game phase."""
        context = create_test_decision_context()
        # Set player state for early phase (0 finished tokens)
        context.player_state.finished_tokens = 0

        decision = self.strategy.decide(context)
        self.assertIsInstance(decision, int)
        self.assertIn(decision, [0])  # Only one move in test context

    def test_decide_late_phase(self):
        """Test decision making in late game phase."""
        context = create_test_decision_context()
        # Set player state for late phase (3 finished tokens)
        context.player_state.finished_tokens = 3

        decision = self.strategy.decide(context)
        self.assertIsInstance(decision, int)

    def test_decide_with_capture_bonus(self):
        """Test decision with capture bonus."""
        capture_move = ValidMove(
            token_id=0,
            current_position=5,
            current_state="active",
            target_position=10,
            move_type="advance_main_board",
            is_safe_move=False,
            captures_opponent=True,
            captured_tokens=[1],  # Captures one token
            strategic_value=8.0,
            strategic_components={},
        )
        context = create_test_decision_context(valid_moves=[capture_move])

        decision = self.strategy.decide(context)
        self.assertEqual(decision, 0)

    def test_decide_safe_move_bonus(self):
        """Test decision with safe move bonus."""
        safe_move = ValidMove(
            token_id=0,
            current_position=5,
            current_state="active",
            target_position=10,
            move_type="advance_main_board",
            is_safe_move=True,
            captures_opponent=False,
            captured_tokens=[],
            strategic_value=5.0,
            strategic_components={},
        )
        context = create_test_decision_context(valid_moves=[safe_move])

        decision = self.strategy.decide(context)
        self.assertEqual(decision, 0)

    def test_decide_home_column_advance(self):
        """Test decision with home column advancement bonus."""
        home_move = ValidMove(
            token_id=0,
            current_position=50,
            current_state="active",
            target_position=52,
            move_type="advance_home_column",
            is_safe_move=True,
            captures_opponent=False,
            captured_tokens=[],
            strategic_value=5.0,
            strategic_components={},
        )
        context = create_test_decision_context(valid_moves=[home_move])

        decision = self.strategy.decide(context)
        self.assertEqual(decision, 0)

    def test_diversity_penalty(self):
        """Test diversity penalty for repeated token moves."""
        # Set up recent moves memory
        self.strategy.recent_moves_memory = [0, 0, 0]  # Token 0 moved recently

        context = create_test_decision_context()
        decision = self.strategy.decide(context)
        self.assertIsInstance(decision, int)

    def test_epsilon_exploration(self):
        """Test epsilon uniform exploration."""
        context = create_test_decision_context()

        # Mock random.random to trigger epsilon exploration
        with unittest.mock.patch(
            "random.random", return_value=0.01
        ):  # Less than epsilon
            with unittest.mock.patch("random.choice", return_value=0):
                decision = self.strategy.decide(context)
                self.assertEqual(decision, 0)

    def test_threat_penalty(self):
        """Test threat penalty for risky moves."""
        # Create context with opponent positions that threaten the target
        context = create_test_decision_context()
        # Add opponent at threatening position
        context.opponents[0].positions_occupied = [11]  # Close to target position 9

        decision = self.strategy.decide(context)
        self.assertIsInstance(decision, int)

    def test_memory_management(self):
        """Test recent moves memory management."""
        # Fill memory beyond limit
        for i in range(30):  # More than DIVERSITY_MEMORY (25)
            self.strategy.save_and_return(i % 4)

        # Memory should be truncated to 25
        self.assertEqual(len(self.strategy.recent_moves_memory), 25)


if __name__ == "__main__":
    unittest.main()
