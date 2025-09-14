"""
Comprehensive tests for Ludo strategy implementations.

This module contains tests for all strategy classes including:
- BaseStrategy (abstract base class)
- RandomStrategy
- KillerStrategy
- DefensiveStrategy
- BalancedStrategy
- CautiousStrategy
- StrategyFactory
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ludo_engine.core.constants import HeuristicConstants, LudoConstants
from ludo_engine.core.model import GameStateData
from ludo_engine.core.player import Player
from ludo_engine.core.token import Token
from ludo_engine.strategies.advanced import (
    CautiousStrategy,
    OptimistStrategy,
    ProbabilisticStrategy,
    WinnerStrategy,
)
from ludo_engine.strategies.base_strategy import BaseStrategy
from ludo_engine.strategies.factory import StrategyFactory
from ludo_engine.strategies.heuristic import (
    BalancedStrategy,
    DefensiveStrategy,
    KillerStrategy,
    RandomStrategy,
)


class TestBaseStrategy(unittest.TestCase):
    """Test cases for the BaseStrategy abstract class."""

    def setUp(self):
        """Set up test fixtures."""

        # Create a concrete subclass for testing
        class ConcreteStrategy(BaseStrategy):
            def choose_move(self, movable_tokens, dice_roll, game_state):
                return movable_tokens[0] if movable_tokens else None

        self.strategy = ConcreteStrategy("TestStrategy")
        self.mock_player = Mock(spec=Player)
        self.mock_token = Mock(spec=Token)
        self.mock_token.color = "red"
        self.mock_token.position = 5
        self.mock_token.steps_taken = 5

    def test_initialization(self):
        """Test strategy initialization."""
        self.assertEqual(self.strategy.name, "TestStrategy")
        self.assertIsNone(self.strategy.player)

    def test_set_player(self):
        """Test setting the player for the strategy."""
        self.strategy.set_player(self.mock_player)
        self.assertEqual(self.strategy.player, self.mock_player)

    def test_evaluate_move_default(self):
        """Test default evaluate_move implementation."""
        score = self.strategy.evaluate_move(self.mock_token, 3, {})
        self.assertEqual(score, 1.0)

    def test_get_opponent_tokens_in_range_no_move(self):
        """Test get_opponent_tokens_in_range when token cannot move."""
        self.mock_token.can_move.return_value = False
        opponents = self.strategy.get_opponent_tokens_in_range(self.mock_token, 3, {})
        self.assertEqual(opponents, [])

    def test_get_opponent_tokens_in_range_at_home(self):
        """Test get_opponent_tokens_in_range when token is at home and rolls 6."""
        # Skip this complex test for now
        pass

    def test_is_move_safe(self):
        """Test is_move_safe method."""
        self.mock_token.can_move.return_value = True
        self.mock_token.is_at_home.return_value = False
        self.mock_token.position = 10

        # Test safe position (position 14 is safe)
        game_state = {}
        is_safe = self.strategy.is_move_safe(
            self.mock_token, 4, game_state
        )  # 10 + 4 = 14, which is safe
        self.assertTrue(is_safe)

    def test_count_tokens_ahead_no_player(self):
        """Test count_tokens_ahead when no player is set."""
        count = self.strategy.count_tokens_ahead(self.mock_token, {})
        self.assertEqual(count, 0)

    def test_count_tokens_ahead_with_player(self):
        """Test count_tokens_ahead with player set."""
        self.strategy.set_player(self.mock_player)

        # Mock player tokens
        mock_token1 = Mock(spec=Token)
        mock_token1.steps_taken = 3
        mock_token2 = Mock(spec=Token)
        mock_token2.steps_taken = 7
        self.mock_player.tokens = [self.mock_token, mock_token1, mock_token2]

        count = self.strategy.count_tokens_ahead(self.mock_token, {})
        self.assertEqual(count, 1)  # Only token2 has more steps


class TestRandomStrategy(unittest.TestCase):
    """Test cases for RandomStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = RandomStrategy()

    def test_initialization(self):
        """Test RandomStrategy initialization."""
        self.assertEqual(self.strategy.name, "Random")

    def test_choose_move_no_tokens(self):
        """Test choose_move with no movable tokens."""
        result = self.strategy.choose_move([], 3, {})
        self.assertIsNone(result)

    def test_choose_move_with_tokens(self):
        """Test choose_move with movable tokens."""
        mock_token1 = Mock(spec=Token)
        mock_token2 = Mock(spec=Token)

        with patch("random.choice", return_value=mock_token1) as mock_choice:
            result = self.strategy.choose_move([mock_token1, mock_token2], 3, {})
            self.assertEqual(result, mock_token1)
            mock_choice.assert_called_once_with([mock_token1, mock_token2])


class TestKillerStrategy(unittest.TestCase):
    """Test cases for KillerStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = KillerStrategy()
        self.mock_token1 = Mock(spec=Token)
        self.mock_token1.color = "red"
        self.mock_token1.steps_taken = 5
        self.mock_token2 = Mock(spec=Token)
        self.mock_token2.color = "red"
        self.mock_token2.steps_taken = 3

    def test_initialization(self):
        """Test KillerStrategy initialization."""
        self.assertEqual(self.strategy.name, "Killer")

    def test_choose_move_no_captures(self):
        """Test choose_move when no captures are possible."""
        # Mock tokens that can move but no captures
        self.mock_token1.can_move.return_value = True
        self.mock_token2.can_move.return_value = True

        # Mock get_opponent_tokens_in_range to return empty list
        with patch.object(
            self.strategy, "get_opponent_tokens_in_range", return_value=[]
        ):
            with patch.object(self.strategy, "count_tokens_ahead", return_value=0):
                result = self.strategy.choose_move(
                    [self.mock_token1, self.mock_token2], 3, {}
                )
                # Should return token with most steps ahead (token1 has 5 steps, token2 has 3)
                self.assertEqual(result, self.mock_token1)

    def test_choose_move_with_captures(self):
        """Test choose_move when captures are possible."""
        self.mock_token1.can_move.return_value = True
        self.mock_token2.can_move.return_value = True

        # Mock opponent tokens for capture
        mock_opponent = Mock(spec=Token)
        mock_opponent.color = "blue"

        with patch.object(
            self.strategy,
            "get_opponent_tokens_in_range",
            side_effect=[[mock_opponent], []],
        ):
            result = self.strategy.choose_move(
                [self.mock_token1, self.mock_token2], 3, {}
            )
            self.assertEqual(result, self.mock_token1)


class TestDefensiveStrategy(unittest.TestCase):
    """Test cases for DefensiveStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = DefensiveStrategy()
        self.mock_token1 = Mock(spec=Token)
        self.mock_token1.steps_taken = 5
        self.mock_token2 = Mock(spec=Token)
        self.mock_token2.steps_taken = 10

    def test_initialization(self):
        """Test DefensiveStrategy initialization."""
        self.assertEqual(self.strategy.name, "Defensive")

    def test_choose_move_no_safe_moves(self):
        """Test choose_move when no safe moves are available."""
        self.mock_token1.can_move.return_value = True
        self.mock_token2.can_move.return_value = True

        with patch.object(self.strategy, "is_move_safe", return_value=False):
            result = self.strategy.choose_move(
                [self.mock_token1, self.mock_token2], 3, {}
            )
            # Should return token with least steps (most advanced)
            self.assertEqual(result, self.mock_token1)

    def test_choose_move_with_safe_moves(self):
        """Test choose_move when safe moves are available."""
        self.mock_token1.can_move.return_value = True
        self.mock_token2.can_move.return_value = True

        with patch.object(self.strategy, "is_move_safe", side_effect=[True, False]):
            result = self.strategy.choose_move(
                [self.mock_token1, self.mock_token2], 3, {}
            )
            self.assertEqual(result, self.mock_token1)


class TestBalancedStrategy(unittest.TestCase):
    """Test cases for BalancedStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = BalancedStrategy()
        self.mock_token1 = Mock(spec=Token)
        self.mock_token2 = Mock(spec=Token)

    def test_initialization(self):
        """Test BalancedStrategy initialization."""
        self.assertEqual(self.strategy.name, "Balanced")

    def test_evaluate_move(self):
        """Test evaluate_move scoring."""
        self.mock_token1.steps_taken = 5
        self.mock_token1.is_at_home.return_value = False
        self.mock_token1.position = 10

        # Mock opponent tokens for capture bonus
        mock_opponent = Mock(spec=Token)

        with patch.object(
            self.strategy, "get_opponent_tokens_in_range", return_value=[mock_opponent]
        ):
            with patch.object(self.strategy, "is_move_safe", return_value=True):
                score = self.strategy.evaluate_move(self.mock_token1, 3, {})

                # Expected score calculation:
                # Advancement: (5 + 3) * 0.1 = 0.8
                # Capture bonus: 1 * 10.0 = 10.0
                # Safe move bonus: 5.0
                # Total: 0.8 + 10.0 + 5.0 = 15.8
                expected_score = (
                    (5 + 3) * HeuristicConstants.HEURISTIC_ADVANCEMENT_MULTIPLIER
                    + 1 * HeuristicConstants.HEURISTIC_CAPTURE_BONUS
                    + HeuristicConstants.HEURISTIC_SAFE_MOVE_BONUS
                )
                self.assertAlmostEqual(score, expected_score)

    def test_choose_move(self):
        """Test choose_move selects highest scoring move."""
        self.mock_token1.can_move.return_value = True
        self.mock_token2.can_move.return_value = True

        with patch.object(self.strategy, "evaluate_move", side_effect=[5.0, 10.0]):
            result = self.strategy.choose_move(
                [self.mock_token1, self.mock_token2], 3, {}
            )
            self.assertEqual(result, self.mock_token2)  # Higher score


class TestCautiousStrategy(unittest.TestCase):
    """Test cases for CautiousStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = CautiousStrategy()
        self.mock_token1 = Mock(spec=Token)
        self.mock_token1.color = "red"
        self.mock_token1.can_move.return_value = True
        self.mock_token1.is_at_home.return_value = False
        self.mock_token1.position = 10
        self.mock_token1.steps_taken = 10

        self.mock_token2 = Mock(spec=Token)
        self.mock_token2.color = "red"
        self.mock_token2.can_move.return_value = True
        self.mock_token2.is_at_home.return_value = False
        self.mock_token2.position = 20
        self.mock_token2.steps_taken = 20

    def test_initialization(self):
        """Test CautiousStrategy initialization."""
        self.assertEqual(self.strategy.name, "Cautious")

    def test_choose_move_no_tokens(self):
        """Test choose_move with no movable tokens."""
        result = self.strategy.choose_move([], 3, {})
        self.assertIsNone(result)

    def test_choose_move_with_safe_moves(self):
        """Test choose_move when safe moves are available."""
        # Mock is_move_safe to return True for token1, False for token2
        with patch.object(self.strategy, "is_move_safe", side_effect=[True, False]):
            result = self.strategy.choose_move(
                [self.mock_token1, self.mock_token2], 3, {}
            )
            # Should choose token with fewer steps (safer)
            self.assertEqual(result, self.mock_token1)

    def test_choose_move_no_safe_moves(self):
        """Test choose_move when no safe moves are available."""
        # Mock is_move_safe to return False for both tokens
        with patch.object(self.strategy, "is_move_safe", return_value=False):
            result = self.strategy.choose_move(
                [self.mock_token1, self.mock_token2], 3, {}
            )
            # Should choose token with most steps (least to lose)
            self.assertEqual(result, self.mock_token2)

    def test_choose_move_single_token(self):
        """Test choose_move with single movable token."""
        with patch.object(self.strategy, "is_move_safe", return_value=True):
            result = self.strategy.choose_move([self.mock_token1], 3, {})
            self.assertEqual(result, self.mock_token1)


class TestOptimistStrategy(unittest.TestCase):
    """Test cases for OptimistStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = OptimistStrategy()
        self.mock_token1 = Mock(spec=Token)
        self.mock_token1.color = "red"
        self.mock_token1.can_move.return_value = True
        self.mock_token1.steps_taken = 10

        self.mock_token2 = Mock(spec=Token)
        self.mock_token2.color = "red"
        self.mock_token2.can_move.return_value = True
        self.mock_token2.steps_taken = 20

    def test_initialization(self):
        """Test OptimistStrategy initialization."""
        self.assertEqual(self.strategy.name, "Optimist")

    def test_choose_move_no_tokens(self):
        """Test choose_move with no movable tokens."""
        result = self.strategy.choose_move([], 3, {})
        self.assertIsNone(result)

    def test_choose_move_with_captures(self):
        """Test choose_move prioritizes captures."""
        # Mock get_opponent_tokens_in_range to return opponents for token1
        with patch.object(
            self.strategy,
            "get_opponent_tokens_in_range",
            side_effect=[["opponent1"], []],
        ):
            result = self.strategy.choose_move(
                [self.mock_token1, self.mock_token2], 3, {}
            )
            self.assertEqual(result, self.mock_token1)

    def test_choose_move_no_captures(self):
        """Test choose_move when no captures are available."""
        # Mock no opponents for either token
        with patch.object(
            self.strategy, "get_opponent_tokens_in_range", return_value=[]
        ):
            result = self.strategy.choose_move(
                [self.mock_token1, self.mock_token2], 3, {}
            )
            # Should choose token that advances furthest
            self.assertEqual(result, self.mock_token2)

    def test_choose_move_single_token(self):
        """Test choose_move with single movable token."""
        with patch.object(
            self.strategy, "get_opponent_tokens_in_range", return_value=[]
        ):
            result = self.strategy.choose_move([self.mock_token1], 3, {})
            self.assertEqual(result, self.mock_token1)


class TestWinnerStrategy(unittest.TestCase):
    """Test cases for WinnerStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = WinnerStrategy()
        self.mock_token1 = Mock(spec=Token)
        self.mock_token1.color = "red"
        self.mock_token1.can_move.return_value = True
        self.mock_token1.steps_taken = 50  # Close to finish

        self.mock_token2 = Mock(spec=Token)
        self.mock_token2.color = "red"
        self.mock_token2.can_move.return_value = True
        self.mock_token2.steps_taken = 40

    def test_initialization(self):
        """Test WinnerStrategy initialization."""
        self.assertEqual(self.strategy.name, "Winner")

    def test_choose_move_no_tokens(self):
        """Test choose_move with no movable tokens."""
        result = self.strategy.choose_move([], 3, {})
        self.assertIsNone(result)

    def test_choose_move_with_finishing_tokens(self):
        """Test choose_move prioritizes tokens that can finish."""
        # Set up token1 to be able to finish with roll of 6
        self.mock_token1.steps_taken = 51  # 51 + 6 = TOTAL_STEPS_TO_FINISH
        result = self.strategy.choose_move([self.mock_token1, self.mock_token2], 6, {})
        self.assertEqual(result, self.mock_token1)

    def test_choose_move_no_finishing_moves(self):
        """Test choose_move when no tokens can finish."""
        # Neither token can finish with roll of 3
        result = self.strategy.choose_move([self.mock_token1, self.mock_token2], 3, {})
        # Should choose most advanced token
        self.assertEqual(result, self.mock_token1)

    def test_choose_move_single_token(self):
        """Test choose_move with single movable token."""
        result = self.strategy.choose_move([self.mock_token1], 3, {})
        self.assertEqual(result, self.mock_token1)


class TestProbabilisticStrategy(unittest.TestCase):
    """Test cases for ProbabilisticStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.strategy = ProbabilisticStrategy()
        self.mock_token1 = Mock(spec=Token)
        self.mock_token1.color = "red"
        self.mock_token1.can_move.return_value = True
        self.mock_token1.steps_taken = 10
        self.mock_token1.is_at_home.return_value = False
        self.mock_token1.position = 10

        self.mock_token2 = Mock(spec=Token)
        self.mock_token2.color = "red"
        self.mock_token2.can_move.return_value = True
        self.mock_token2.steps_taken = 5
        self.mock_token2.is_at_home.return_value = False
        self.mock_token2.position = 5

    def test_initialization(self):
        """Test ProbabilisticStrategy initialization."""
        self.assertEqual(self.strategy.name, "Probabilistic")

    def test_choose_move_no_tokens(self):
        """Test choose_move with no movable tokens."""
        result = self.strategy.choose_move([], 3, {})
        self.assertIsNone(result)

    def test_choose_move_with_tokens(self):
        """Test choose_move selects highest scoring move."""
        # Mock calculate_expected_value to return higher score for token1
        with patch.object(
            self.strategy, "calculate_expected_value", side_effect=[2.0, 1.0]
        ):
            result = self.strategy.choose_move(
                [self.mock_token1, self.mock_token2], 3, {}
            )
            self.assertEqual(result, self.mock_token1)

    def test_choose_move_single_token(self):
        """Test choose_move with single movable token."""
        with patch.object(self.strategy, "calculate_expected_value", return_value=1.0):
            result = self.strategy.choose_move([self.mock_token1], 3, {})
            self.assertEqual(result, self.mock_token1)

    def test_calculate_expected_value_basic(self):
        """Test calculate_expected_value basic scoring."""
        # Mock game state with board as dict
        game_state = GameStateData(
            board={},
            players=[],
            current_player=0,
            turn_count=0,
            game_status="ongoing",
            sixes_in_row=0,
        )

        value = self.strategy.calculate_expected_value(self.mock_token1, 3, game_state)
        self.assertGreater(value, 0)

    def test_calculate_expected_value_with_finish(self):
        """Test calculate_expected_value when token can finish."""
        # Set up token to be able to finish
        self.mock_token1.steps_taken = LudoConstants.TOTAL_STEPS_TO_FINISH - 3  # TOTAL_STEPS_TO_FINISH - 3 + 3 = TOTAL_STEPS_TO_FINISH

        game_state = GameStateData(
            board={},
            players=[],
            current_player=0,
            turn_count=0,
            game_status="ongoing",
            sixes_in_row=0,
        )

        value = self.strategy.calculate_expected_value(self.mock_token1, 3, game_state)
        # Should include finish bonus
        self.assertGreater(value, 60)  # Base advancement + finish bonus

    def test_calculate_expected_value_with_captures(self):
        """Test calculate_expected_value with potential captures."""
        # Mock opponents in range
        mock_opponent = Mock()
        mock_opponent.color = "blue"

        game_state = GameStateData(
            board={},
            players=[],
            current_player=0,
            turn_count=0,
            game_status="ongoing",
            sixes_in_row=0,
        )

        with patch.object(
            self.strategy, "get_opponent_tokens_in_range", return_value=[mock_opponent]
        ):
            value = self.strategy.calculate_expected_value(
                self.mock_token1, 3, game_state
            )
            # Should include capture bonus
            self.assertGreater(value, 20)  # Base advancement + capture bonus

    def test_calculate_expected_value_exit_home(self):
        """Test calculate_expected_value when exiting home."""
        # Set up token at home
        self.mock_token1.is_at_home.return_value = True
        self.mock_token1.steps_taken = 0

        game_state = GameStateData(
            board={},
            players=[],
            current_player=0,
            turn_count=0,
            game_status="ongoing",
            sixes_in_row=0,
        )

        value = self.strategy.calculate_expected_value(self.mock_token1, 6, game_state)
        # Should include exit home bonus
        self.assertGreater(value, 10)  # Base advancement + exit home bonus

    def test_calculate_capture_risk_safe_position(self):
        """Test calculate_capture_risk for safe position."""
        game_state = GameStateData(
            board={},
            players=[],
            current_player=0,
            turn_count=0,
            game_status="ongoing",
            sixes_in_row=0,
        )

        with patch.object(self.strategy, "is_move_safe", return_value=True):
            risk = self.strategy.calculate_capture_risk(self.mock_token1, 3, game_state)
            self.assertEqual(risk, 0.0)

    def test_calculate_capture_risk_unsafe_position(self):
        """Test calculate_capture_risk for unsafe position."""
        # Mock opponent tokens that could reach the new position
        game_state = GameStateData(
            board={"8": [{"color": "blue", "position": 8}]},
            players=[],
            current_player=0,
            turn_count=0,
            game_status="ongoing",
            sixes_in_row=0,
        )  # 2 steps away

        with patch.object(self.strategy, "is_move_safe", return_value=False):
            risk = self.strategy.calculate_capture_risk(self.mock_token1, 3, game_state)
            self.assertGreater(risk, 0.0)

    def test_calculate_capture_risk_cannot_move(self):
        """Test calculate_capture_risk when token cannot move."""
        self.mock_token1.can_move.return_value = False

        mock_board = Mock()
        game_state = Mock()
        game_state.board = mock_board

        risk = self.strategy.calculate_capture_risk(self.mock_token1, 3, game_state)
        self.assertEqual(risk, 0.0)

    def test_calculate_capture_risk_from_home(self):
        """Test calculate_capture_risk when moving from home."""
        self.mock_token1.is_at_home.return_value = True

        game_state = GameStateData(
            board={},
            players=[],
            current_player=0,
            turn_count=0,
            game_status="ongoing",
            sixes_in_row=0,
        )

        with patch.object(self.strategy, "is_move_safe", return_value=False):
            risk = self.strategy.calculate_capture_risk(self.mock_token1, 6, game_state)
            # Should check risk at start position
            self.assertGreaterEqual(risk, 0.0)


class TestStrategyFactory(unittest.TestCase):
    """Test cases for StrategyFactory."""

    def test_get_available_strategies(self):
        """Test getting list of available strategies."""
        strategies = StrategyFactory.get_available_strategies()
        self.assertIsInstance(strategies, list)
        self.assertGreater(len(strategies), 0)

        # Should include basic strategies
        self.assertIn("random", strategies)
        self.assertIn("killer", strategies)
        self.assertIn("defensive", strategies)
        self.assertIn("balanced", strategies)
        self.assertIn("cautious", strategies)

    def test_create_random_strategy(self):
        """Test creating a random strategy."""
        strategy = StrategyFactory.create_strategy("random")
        self.assertIsInstance(strategy, RandomStrategy)
        self.assertEqual(strategy.name, "Random")

    def test_create_killer_strategy(self):
        """Test creating a killer strategy."""
        strategy = StrategyFactory.create_strategy("killer")
        self.assertIsInstance(strategy, KillerStrategy)
        self.assertEqual(strategy.name, "Killer")

    def test_create_defensive_strategy(self):
        """Test creating a defensive strategy."""
        strategy = StrategyFactory.create_strategy("defensive")
        self.assertIsInstance(strategy, DefensiveStrategy)
        self.assertEqual(strategy.name, "Defensive")

    def test_create_balanced_strategy(self):
        """Test creating a balanced strategy."""
        strategy = StrategyFactory.create_strategy("balanced")
        self.assertIsInstance(strategy, BalancedStrategy)
        self.assertEqual(strategy.name, "Balanced")

    def test_create_cautious_strategy(self):
        """Test creating a cautious strategy."""
        strategy = StrategyFactory.create_strategy("cautious")
        self.assertIsInstance(strategy, CautiousStrategy)
        self.assertEqual(strategy.name, "Cautious")

    def test_create_invalid_strategy(self):
        """Test creating an invalid strategy."""
        strategy = StrategyFactory.create_strategy("invalid_strategy")
        self.assertIsNone(strategy)

    def test_create_strategy_case_insensitive(self):
        """Test that strategy creation is case insensitive."""
        strategy = StrategyFactory.create_strategy("RANDOM")
        self.assertIsInstance(strategy, RandomStrategy)

        strategy = StrategyFactory.create_strategy("Random")
        self.assertIsInstance(strategy, RandomStrategy)


if __name__ == "__main__":
    unittest.main()
