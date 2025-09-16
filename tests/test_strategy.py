"""
Unit tests for Strategy classes and StrategyFactory.
Tests cover strategy creation, available strategies, and basic decision making.
"""

import unittest
from unittest.mock import patch

from ludo_engine.model import (
    AIDecisionContext,
    CurrentSituation,
    OpponentInfo,
    PlayerState,
    StrategicAnalysis,
    ValidMove,
)
from ludo_engine.strategies.killer import KillerStrategy
from ludo_engine.strategies.random_strategy import RandomStrategy
from ludo_engine.strategies.winner import WinnerStrategy
from ludo_engine.strategy import StrategyFactory


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


class TestStrategyBase(unittest.TestCase):
    """Test cases for Strategy base class."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = RandomStrategy()

    def test_initialization(self):
        """Test strategy initialization."""
        self.assertEqual(self.strategy.name, "Random")
        self.assertIn("random", self.strategy.description.lower())

    def test_get_valid_moves(self):
        """Test getting valid moves from context."""
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
                    strategic_value=5.0,
                    strategic_components={},
                ),
                ValidMove(
                    token_id=1,
                    current_position=-1,
                    current_state="home",
                    target_position=0,
                    move_type="exit_home",
                    is_safe_move=True,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=3.0,
                    strategic_components={},
                ),
            ],
        )

        valid_moves = self.strategy._get_valid_moves(context)
        self.assertEqual(len(valid_moves), 2)

    def test_get_move_by_type(self):
        """Test getting move by type."""
        moves = [
            ValidMove(
                token_id=0,
                current_position=-1,
                current_state="home",
                target_position=0,
                move_type="exit_home",
                is_safe_move=True,
                captures_opponent=False,
                captured_tokens=[],
                strategic_value=5.0,
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
                strategic_value=8.0,
                strategic_components={},
            ),
        ]

        exit_move = self.strategy._get_move_by_type(moves, "exit_home")
        self.assertIsNotNone(exit_move)
        self.assertEqual(exit_move.move_type, "exit_home")

        capture_move = self.strategy._get_move_by_type(moves, "capture")
        self.assertIsNone(capture_move)  # No capture moves

    def test_get_moves_by_type(self):
        """Test getting all moves by type."""
        moves = [
            ValidMove(
                token_id=0,
                current_position=-1,
                current_state="home",
                target_position=0,
                move_type="exit_home",
                is_safe_move=True,
                captures_opponent=False,
                captured_tokens=[],
                strategic_value=5.0,
                strategic_components={},
            ),
            ValidMove(
                token_id=1,
                current_position=-1,
                current_state="home",
                target_position=0,
                move_type="exit_home",
                is_safe_move=True,
                captures_opponent=False,
                captured_tokens=[],
                strategic_value=3.0,
                strategic_components={},
            ),
            ValidMove(
                token_id=2,
                current_position=5,
                current_state="active",
                target_position=10,
                move_type="advance_main_board",
                is_safe_move=False,
                captures_opponent=False,
                captured_tokens=[],
                strategic_value=2.0,
                strategic_components={},
            ),
        ]

        exit_moves = self.strategy._get_moves_by_type(moves, "exit_home")
        self.assertEqual(len(exit_moves), 2)

        advance_moves = self.strategy._get_moves_by_type(moves, "advance_main_board")
        self.assertEqual(len(advance_moves), 1)

    def test_get_capture_moves(self):
        """Test getting capture moves."""
        moves = [
            ValidMove(
                token_id=0,
                current_position=5,
                current_state="active",
                target_position=10,
                move_type="advance_main_board",
                is_safe_move=False,
                captures_opponent=True,
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
                strategic_value=2.0,
                strategic_components={},
            ),
        ]

        capture_moves = self.strategy._get_capture_moves(moves)
        self.assertEqual(len(capture_moves), 1)
        self.assertTrue(capture_moves[0].captures_opponent)

    def test_get_safe_moves(self):
        """Test getting safe moves."""
        moves = [
            ValidMove(
                token_id=0,
                current_position=-1,
                current_state="home",
                target_position=0,
                move_type="exit_home",
                is_safe_move=True,
                captures_opponent=False,
                captured_tokens=[],
                strategic_value=5.0,
                strategic_components={},
            ),
            ValidMove(
                token_id=1,
                current_position=5,
                current_state="active",
                target_position=10,
                move_type="advance_main_board",
                is_safe_move=False,
                captures_opponent=False,
                captured_tokens=[],
                strategic_value=2.0,
                strategic_components={},
            ),
        ]

        safe_moves = self.strategy._get_safe_moves(moves)
        self.assertEqual(len(safe_moves), 1)
        self.assertTrue(safe_moves[0].is_safe_move)

    def test_get_risky_moves(self):
        """Test getting risky moves."""
        moves = [
            ValidMove(
                token_id=0,
                current_position=-1,
                current_state="home",
                target_position=0,
                move_type="exit_home",
                is_safe_move=True,
                captures_opponent=False,
                captured_tokens=[],
                strategic_value=5.0,
                strategic_components={},
            ),
            ValidMove(
                token_id=1,
                current_position=5,
                current_state="active",
                target_position=10,
                move_type="advance_main_board",
                is_safe_move=False,
                captures_opponent=False,
                captured_tokens=[],
                strategic_value=2.0,
                strategic_components={},
            ),
        ]

        risky_moves = self.strategy._get_risky_moves(moves)
        self.assertEqual(len(risky_moves), 1)
        self.assertFalse(risky_moves[0].is_safe_move)

    def test_get_highest_value_move(self):
        """Test getting highest value move."""
        moves = [
            ValidMove(
                token_id=0,
                current_position=-1,
                current_state="home",
                target_position=0,
                move_type="exit_home",
                is_safe_move=True,
                captures_opponent=False,
                captured_tokens=[],
                strategic_value=5.0,
                strategic_components={},
            ),
            ValidMove(
                token_id=1,
                current_position=5,
                current_state="active",
                target_position=10,
                move_type="advance_main_board",
                is_safe_move=False,
                captures_opponent=False,
                captured_tokens=[],
                strategic_value=8.0,
                strategic_components={},
            ),
        ]

        highest = self.strategy._get_highest_value_move(moves)
        self.assertIsNotNone(highest)
        self.assertEqual(highest.strategic_value, 8.0)

    def test_get_lowest_value_move(self):
        """Test getting lowest value move."""
        moves = [
            ValidMove(
                token_id=0,
                current_position=-1,
                current_state="home",
                target_position=0,
                move_type="exit_home",
                is_safe_move=True,
                captures_opponent=False,
                captured_tokens=[],
                strategic_value=5.0,
                strategic_components={},
            ),
            ValidMove(
                token_id=1,
                current_position=5,
                current_state="active",
                target_position=10,
                move_type="advance_main_board",
                is_safe_move=False,
                captures_opponent=False,
                captured_tokens=[],
                strategic_value=2.0,
                strategic_components={},
            ),
        ]

        lowest = self.strategy._get_lowest_value_move(moves)
        self.assertIsNotNone(lowest)
        self.assertEqual(lowest.strategic_value, 2.0)

    def test_string_representation(self):
        """Test string representation."""
        str_repr = str(self.strategy)
        self.assertIn("Strategy", str_repr)
        self.assertIn("Random", str_repr)


class TestStrategyFactory(unittest.TestCase):
    """Test cases for StrategyFactory class."""

    def test_create_strategy_valid(self):
        """Test creating valid strategies."""
        strategy = StrategyFactory.create_strategy("random")
        self.assertIsInstance(strategy, RandomStrategy)

        strategy = StrategyFactory.create_strategy("killer")
        self.assertIsInstance(strategy, KillerStrategy)

        strategy = StrategyFactory.create_strategy("winner")
        self.assertIsInstance(strategy, WinnerStrategy)

    def test_create_strategy_invalid(self):
        """Test creating invalid strategy."""
        with self.assertRaises(ValueError) as context:
            StrategyFactory.create_strategy("invalid_strategy")

        self.assertIn("Unknown strategy", str(context.exception))
        self.assertIn("invalid_strategy", str(context.exception))

    def test_create_strategy_case_insensitive(self):
        """Test strategy creation is case insensitive."""
        strategy1 = StrategyFactory.create_strategy("RANDOM")
        strategy2 = StrategyFactory.create_strategy("Random")
        strategy3 = StrategyFactory.create_strategy("random")

        self.assertIsInstance(strategy1, RandomStrategy)
        self.assertIsInstance(strategy2, RandomStrategy)
        self.assertIsInstance(strategy3, RandomStrategy)

    def test_get_available_strategies(self):
        """Test getting available strategies."""
        strategies = StrategyFactory.get_available_strategies()
        self.assertIsInstance(strategies, list)
        self.assertGreater(len(strategies), 0)
        self.assertIn("random", strategies)
        self.assertIn("killer", strategies)

    def test_get_available_strategies_avoid_llm(self):
        """Test getting available strategies avoiding LLM."""
        strategies = StrategyFactory.get_available_strategies(avoid_llm=True)
        self.assertIsInstance(strategies, list)
        self.assertNotIn("llm", [s.lower() for s in strategies])

    def test_get_strategy_descriptions(self):
        """Test getting strategy descriptions."""
        descriptions = StrategyFactory.get_strategy_descriptions()
        self.assertIsInstance(descriptions, dict)
        self.assertGreater(len(descriptions), 0)

        # Check that descriptions contain expected content
        self.assertIn("random", descriptions)
        self.assertIsInstance(descriptions["random"], str)
        self.assertGreater(len(descriptions["random"]), 0)

    def test_get_strategy_descriptions_avoid_llm(self):
        """Test getting strategy descriptions avoiding LLM."""
        descriptions = StrategyFactory.get_strategy_descriptions(avoid_llm=True)
        self.assertIsInstance(descriptions, dict)
        self.assertNotIn("llm", descriptions)


class TestRandomStrategy(unittest.TestCase):
    """Test cases for RandomStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = RandomStrategy()

    def test_decide_with_moves(self):
        """Test random strategy decision making."""
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
                    strategic_value=5.0,
                    strategic_components={},
                ),
                ValidMove(
                    token_id=1,
                    current_position=-1,
                    current_state="home",
                    target_position=0,
                    move_type="exit_home",
                    is_safe_move=True,
                    captures_opponent=False,
                    captured_tokens=[],
                    strategic_value=3.0,
                    strategic_components={},
                ),
            ],
        )

        # Mock random choice to return predictable result
        with patch("random.choice", return_value=context.valid_moves[0]):
            decision = self.strategy.decide(context)
            self.assertEqual(decision, 0)

    def test_decide_no_moves(self):
        """Test random strategy with no valid moves."""
        context = create_test_decision_context(dice_value=3, valid_moves=[])

        decision = self.strategy.decide(context)
        self.assertEqual(decision, 0)  # Default fallback


class TestKillerStrategy(unittest.TestCase):
    """Test cases for KillerStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = KillerStrategy()

    def test_initialization(self):
        """Test killer strategy initialization."""
        self.assertEqual(self.strategy.name, "Killer")
        self.assertIn("aggressive", self.strategy.description.lower())

    def test_decide_prioritizes_captures(self):
        """Test that killer strategy prioritizes captures."""
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
        self.assertEqual(decision, 0)  # Should choose capture move


class TestWinnerStrategy(unittest.TestCase):
    """Test cases for WinnerStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = WinnerStrategy()

    def test_initialization(self):
        """Test winner strategy initialization."""
        self.assertEqual(self.strategy.name, "Winner")
        self.assertIn("finish", self.strategy.description.lower())

    def test_decide_prioritizes_finishing(self):
        """Test that winner strategy prioritizes finishing."""
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
                    strategic_value=15.0,
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
        self.assertEqual(decision, 0)  # Should choose finish move


if __name__ == "__main__":
    unittest.main()
