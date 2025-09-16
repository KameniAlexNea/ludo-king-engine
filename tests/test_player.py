"""
Comprehensive unit tests for Player class.
Tests cover token management, move validation, strategic decision making,
and game state representation.
"""

import unittest
from unittest.mock import patch

from ludo_engine.constants import GameConstants
from ludo_engine.model import (
    AIDecisionContext,
    CurrentSituation,
    OpponentInfo,
    PlayerState,
    StrategicAnalysis,
    ValidMove,
)
from ludo_engine.player import Player, PlayerColor
from ludo_engine.strategies.random_strategy import RandomStrategy
from ludo_engine.token import TokenState


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


class TestPlayer(unittest.TestCase):
    """Test cases for Player class."""

    def setUp(self):
        """Set up test fixtures."""
        self.player = Player(PlayerColor.RED, 0)
        self.strategy = RandomStrategy()
        self.player.set_strategy(self.strategy)

    def test_initialization(self):
        """Test player initialization."""
        # Create a fresh player without setting strategy
        fresh_player = Player(PlayerColor.RED, 0)
        self.assertEqual(fresh_player.color, PlayerColor.RED)
        self.assertEqual(fresh_player.player_id, 0)
        self.assertEqual(len(fresh_player.tokens), 4)
        self.assertIsNone(fresh_player.strategy)

        # Check tokens are properly initialized
        for i, token in enumerate(fresh_player.tokens):
            self.assertEqual(token.token_id, i)
            self.assertEqual(token.player_color, PlayerColor.RED.value)
            self.assertEqual(token.state, TokenState.HOME)
            self.assertEqual(token.position, -1)

    def test_player_positions(self):
        """Test getting player token positions."""
        positions = self.player.player_positions()
        self.assertEqual(len(positions), 4)
        self.assertEqual(positions, [-1, -1, -1, -1])

        # Move a token
        self.player.tokens[0].position = 5
        positions = self.player.player_positions()
        self.assertEqual(positions, [5, -1, -1, -1])

    def test_get_movable_tokens_no_moves(self):
        """Test getting movable tokens when none can move."""
        movable = self.player.get_movable_tokens(3)
        self.assertEqual(len(movable), 0)  # Can't exit home with 3

    def test_get_movable_tokens_exit_home(self):
        """Test getting movable tokens for exiting home."""
        movable = self.player.get_movable_tokens(6)
        self.assertEqual(len(movable), 4)  # All tokens can exit home

    def test_get_movable_tokens_active_tokens(self):
        """Test getting movable tokens when some are active."""
        # Move token to active state
        self.player.tokens[0].state = TokenState.ACTIVE
        self.player.tokens[0].position = 5

        movable = self.player.get_movable_tokens(4)
        self.assertEqual(len(movable), 1)
        self.assertEqual(movable[0], self.player.tokens[0])

    def test_has_tokens_in_home(self):
        """Test checking if player has tokens in home."""
        self.assertTrue(self.player.has_tokens_in_home())

        # Move all tokens out of home
        for token in self.player.tokens:
            token.state = TokenState.ACTIVE
            token.position = 0

        self.assertFalse(self.player.has_tokens_in_home())

    def test_has_active_tokens(self):
        """Test checking if player has active tokens."""
        self.assertFalse(self.player.has_active_tokens())

        # Activate one token
        self.player.tokens[0].state = TokenState.ACTIVE
        self.player.tokens[0].position = 5

        self.assertTrue(self.player.has_active_tokens())

    def test_get_finished_tokens_count(self):
        """Test counting finished tokens."""
        self.assertEqual(self.player.get_finished_tokens_count(), 0)

        # Finish some tokens
        self.player.tokens[0].state = TokenState.FINISHED
        self.player.tokens[1].state = TokenState.FINISHED

        self.assertEqual(self.player.get_finished_tokens_count(), 2)

    def test_has_won(self):
        """Test checking if player has won."""
        self.assertFalse(self.player.has_won())

        # Finish all tokens
        for token in self.player.tokens:
            token.state = TokenState.FINISHED

        self.assertTrue(self.player.has_won())

    def test_can_move_any_token(self):
        """Test checking if any token can move."""
        self.assertFalse(self.player.can_move_any_token(3))  # Can't exit home
        self.assertTrue(self.player.can_move_any_token(6))  # Can exit home

        # Test with active token
        self.player.tokens[0].state = TokenState.ACTIVE
        self.player.tokens[0].position = 5
        self.assertTrue(self.player.can_move_any_token(4))

    def test_move_token_invalid(self):
        """Test moving token with invalid parameters."""
        self.assertFalse(self.player.move_token(-1, 6))  # Invalid token ID
        self.assertFalse(self.player.move_token(4, 6))  # Invalid token ID
        self.assertFalse(self.player.move_token(0, 0))  # Invalid dice value

    def test_move_token_exit_home(self):
        """Test moving token to exit home."""
        success = self.player.move_token(0, 6)
        self.assertTrue(success)
        self.assertEqual(self.player.tokens[0].state, TokenState.ACTIVE)
        self.assertEqual(self.player.tokens[0].position, self.player.start_position)

    def test_move_token_active_movement(self):
        """Test moving active token."""
        # Set up token in active state
        self.player.tokens[0].state = TokenState.ACTIVE
        self.player.tokens[0].position = 5

        success = self.player.move_token(0, 4)
        self.assertTrue(success)
        self.assertEqual(self.player.tokens[0].position, 9)

    def test_get_game_state(self):
        """Test getting player game state."""
        state = self.player.get_game_state()

        self.assertEqual(state.player_id, 0)
        self.assertEqual(state.color, PlayerColor.RED.value)
        self.assertEqual(state.tokens_in_home, 4)
        self.assertEqual(state.active_tokens, 0)
        self.assertEqual(state.finished_tokens, 0)
        self.assertFalse(state.has_won)

    def test_get_possible_moves_exit_home(self):
        """Test getting possible moves for exiting home."""
        moves = self.player.get_possible_moves(6)

        self.assertEqual(len(moves), 4)
        for move in moves:
            self.assertIsInstance(move, ValidMove)
            self.assertEqual(move.move_type, "exit_home")
            self.assertEqual(move.current_position, -1)
            self.assertEqual(move.target_position, self.player.start_position)

    def test_get_possible_moves_active_tokens(self):
        """Test getting possible moves for active tokens."""
        # Set up active token
        self.player.tokens[0].state = TokenState.ACTIVE
        self.player.tokens[0].position = 5

        moves = self.player.get_possible_moves(4)

        self.assertEqual(len(moves), 1)
        move = moves[0]
        self.assertEqual(move.token_id, 0)
        self.assertEqual(move.current_position, 5)
        self.assertEqual(move.target_position, 9)
        self.assertEqual(move.move_type, "advance_main_board")

    def test_calculate_strategic_value_exit_home(self):
        """Test strategic value calculation for exiting home."""
        token = self.player.tokens[0]
        value, components = self.player._calculate_strategic_value(token, 6)

        self.assertGreater(value, 0)
        self.assertGreater(components.exit_home, 0)

    def test_calculate_strategic_value_forward_progress(self):
        """Test strategic value calculation for forward progress."""
        token = self.player.tokens[0]
        token.state = TokenState.ACTIVE
        token.position = 10

        value, components = self.player._calculate_strategic_value(token, 4)

        self.assertGreater(value, 0)
        self.assertGreater(components.forward_progress, 0)

    def test_calculate_strategic_value_home_column(self):
        """Test strategic value calculation for home column movement."""
        token = self.player.tokens[0]
        token.state = TokenState.HOME_COLUMN
        token.position = 100

        value, components = self.player._calculate_strategic_value(token, 3)

        self.assertGreater(value, 0)
        self.assertGreater(components.home_column_depth, 0)

    def test_calculate_strategic_value_finish(self):
        """Test strategic value calculation for finishing."""
        token = self.player.tokens[0]
        token.state = TokenState.HOME_COLUMN
        token.position = GameConstants.FINISH_POSITION - 1

        value, components = self.player._calculate_strategic_value(token, 1)

        self.assertGreater(value, 0)
        self.assertGreater(components.finish, 0)

    def test_estimate_steps_to_finish(self):
        """Test estimating steps to finish from various positions."""
        # From main board
        steps = self.player._estimate_steps_to_finish(10)
        self.assertGreater(steps, 0)

        # From home column
        steps = self.player._estimate_steps_to_finish(100)
        self.assertGreater(steps, 0)

    def test_set_strategy(self):
        """Test setting player strategy."""
        # Create a fresh player without strategy
        fresh_player = Player(PlayerColor.RED, 0)
        self.assertIsNone(fresh_player.strategy)

        strategy = RandomStrategy()
        fresh_player.set_strategy(strategy)

        self.assertEqual(fresh_player.strategy, strategy)

    def test_make_strategic_decision_with_strategy(self):
        """Test making strategic decision with assigned strategy."""
        strategy = RandomStrategy()
        self.player.set_strategy(strategy)

        context = create_test_decision_context(dice_value=6, valid_moves=[])

        with patch.object(strategy, "decide", return_value=2):
            decision = self.player.make_strategic_decision(context)
            self.assertEqual(decision, 2)

    def test_make_strategic_decision_no_strategy(self):
        """Test making strategic decision without assigned strategy."""
        self.player.strategy = None

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
                )
            ],
        )

        decision = self.player.make_strategic_decision(context)
        self.assertEqual(decision, 0)  # Should choose first available move

    def test_get_strategy_name(self):
        """Test getting strategy name."""
        self.assertEqual(self.player.get_strategy_name(), "Random")

        strategy = RandomStrategy()
        self.player.set_strategy(strategy)
        self.assertEqual(self.player.get_strategy_name(), "Random")

    def test_get_strategy_description(self):
        """Test getting strategy description."""
        self.assertEqual(
            self.player.get_strategy_description(),
            "Baseline strategy that makes random valid moves",
        )

        strategy = RandomStrategy()
        self.player.set_strategy(strategy)
        self.assertIn("random", self.player.get_strategy_description().lower())

    def test_string_representation(self):
        """Test string representation of player."""
        str_repr = str(self.player)
        self.assertIn("Player", str_repr)
        self.assertIn("red", str_repr)
        self.assertIn("Random", str_repr)

    def test_move_type_detection(self):
        """Test move type detection for different scenarios."""
        # Exit home
        move_type = self.player._get_move_type(self.player.tokens[0], 6)
        self.assertEqual(move_type, "exit_home")

        # Active token
        self.player.tokens[0].state = TokenState.ACTIVE
        move_type = self.player._get_move_type(self.player.tokens[0], 4)
        self.assertEqual(move_type, "advance_main_board")

        # Home column
        self.player.tokens[0].state = TokenState.HOME_COLUMN
        move_type = self.player._get_move_type(self.player.tokens[0], 3)
        self.assertEqual(move_type, "advance_home_column")

        # Finish
        self.player.tokens[0].position = GameConstants.FINISH_POSITION - 1
        move_type = self.player._get_move_type(self.player.tokens[0], 1)
        self.assertEqual(move_type, "finish")

    def test_safe_move_detection(self):
        """Test safe move detection."""
        # Safe position
        is_safe = self.player._is_safe_move(self.player.tokens[0], 8)  # Star position
        self.assertTrue(is_safe)

        # Unsafe position
        is_safe = self.player._is_safe_move(self.player.tokens[0], 5)
        self.assertFalse(is_safe)


if __name__ == "__main__":
    unittest.main()
