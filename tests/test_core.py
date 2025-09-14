"""
Comprehensive tests for Ludo c        self.assertEqual(self.token.position, LudoConstants.FINISH_POSITION)re classes.

This module contains detailed tests for the core game classes:
- Token: Individual game pieces with movement and state
- Player: Game participants with tokens and strategy
- Board: Game board with position management and rules
"""

import os
import sys
import unittest
from unittest.mock import Mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ludo_engine.core.board import Board
from ludo_engine.core.constants import LudoConstants
from ludo_engine.core.player import Player
from ludo_engine.core.token import Token, TokenState
from ludo_engine.strategies.base_strategy import BaseStrategy


class TestToken(unittest.TestCase):
    """Comprehensive test cases for Token class."""

    def setUp(self):
        """Set up test fixtures."""
        self.token = Token(0, "red")

    def test_initialization(self):
        """Test token initialization."""
        self.assertEqual(self.token.token_id, 0)
        self.assertEqual(self.token.color, "red")
        self.assertEqual(self.token.position, -1)
        self.assertEqual(self.token.state, TokenState.HOME)
        self.assertEqual(self.token.steps_taken, 0)

    def test_is_at_home(self):
        """Test is_at_home method."""
        self.assertTrue(self.token.is_at_home())

        # Move token to active
        self.token.state = TokenState.ACTIVE
        self.assertFalse(self.token.is_at_home())

    def test_is_active(self):
        """Test is_active method."""
        self.assertFalse(self.token.is_active())

        # Move token to active
        self.token.state = TokenState.ACTIVE
        self.assertTrue(self.token.is_active())

    def test_is_finished(self):
        """Test is_finished method."""
        self.assertFalse(self.token.is_finished())

        # Move token to finished
        self.token.state = TokenState.FINISHED
        self.assertTrue(self.token.is_finished())

    def test_is_safe(self):
        """Test is_safe method."""
        self.assertFalse(self.token.is_safe())

        # Move token to safe
        self.token.state = TokenState.SAFE
        self.assertTrue(self.token.is_safe())

    def test_can_move_from_home(self):
        """Test can_move when token is at home."""
        # Can only move with 6
        self.assertFalse(self.token.can_move(1))
        self.assertFalse(self.token.can_move(5))
        self.assertTrue(self.token.can_move(6))

    def test_can_move_active_token(self):
        """Test can_move for active token."""
        self.token.state = TokenState.ACTIVE
        self.token.steps_taken = 10

        # Can move with various rolls
        self.assertTrue(self.token.can_move(1))
        self.assertTrue(self.token.can_move(6))

        # Cannot move if would exceed finish
        self.token.steps_taken = LudoConstants.FINISH_POSITION  # Close to finish
        self.assertFalse(self.token.can_move(6))  # Would be 62 > TOTAL_STEPS_TO_FINISH

    def test_can_move_finished_token(self):
        """Test can_move for finished token."""
        self.token.state = TokenState.FINISHED
        self.assertFalse(self.token.can_move(1))
        self.assertFalse(self.token.can_move(6))

    def test_move_from_home_with_6(self):
        """Test moving from home with roll of 6."""
        success = self.token.move(6)
        self.assertTrue(success)
        self.assertEqual(self.token.state, TokenState.ACTIVE)
        self.assertEqual(self.token.steps_taken, 1)
        self.assertEqual(self.token.position, 0)  # Red start position

    def test_move_from_home_invalid(self):
        """Test moving from home with invalid roll."""
        success = self.token.move(5)
        self.assertFalse(success)
        self.assertEqual(self.token.state, TokenState.HOME)

    def test_move_active_token(self):
        """Test moving active token."""
        self.token.state = TokenState.ACTIVE
        self.token.position = 5
        self.token.steps_taken = 6

        success = self.token.move(3)
        self.assertTrue(success)
        self.assertEqual(self.token.steps_taken, 9)
        self.assertEqual(self.token.position, 8)

    def test_move_to_finish(self):
        """Test moving token to finish."""
        self.token.state = TokenState.ACTIVE
        self.token.steps_taken = LudoConstants.FINISH_POSITION  # One step from finish

        success = self.token.move(1)
        self.assertTrue(success)
        self.assertEqual(self.token.state, TokenState.FINISHED)
        self.assertEqual(self.token.position, LudoConstants.FINISH_POSITION)  # Finish position

    def test_move_near_finish(self):
        """Test token movement when close to finish."""
        self.token.state = TokenState.ACTIVE
        self.token.steps_taken = 53  # Need 4 more steps to finish

        # Should be able to move with rolls that don't exceed TOTAL_STEPS_TO_FINISH
        self.assertTrue(self.token.can_move(2))  # 53 + 2 = 55 <= TOTAL_STEPS_TO_FINISH
        self.assertTrue(self.token.can_move(4))  # 53 + 4 = TOTAL_STEPS_TO_FINISH <= TOTAL_STEPS_TO_FINISH

        # Should not be able to move with rolls that exceed TOTAL_STEPS_TO_FINISH
        self.assertFalse(self.token.can_move(5))  # 53 + 5 = 58 > TOTAL_STEPS_TO_FINISH
        self.assertFalse(self.token.can_move(6))  # 53 + 6 = 59 > TOTAL_STEPS_TO_FINISH

        # Test actual moves
        success = self.token.move(2)
        self.assertTrue(success)
        self.assertEqual(self.token.steps_taken, 55)
        self.assertEqual(self.token.state, TokenState.ACTIVE)

        # Reset for next test
        self.token.steps_taken = 53
        success = self.token.move(4)
        self.assertTrue(success)
        self.assertEqual(self.token.steps_taken, LudoConstants.TOTAL_STEPS_TO_FINISH)
        self.assertEqual(self.token.state, TokenState.FINISHED)
        self.assertEqual(self.token.position, LudoConstants.FINISH_POSITION)

    def test_move_at_finish_threshold(self):
        """Test token movement at the finish threshold."""
        self.token.state = TokenState.ACTIVE
        self.token.steps_taken = LudoConstants.FINISH_POSITION  # Need exactly 1 more step to finish

        # Should be able to move with roll that reaches exactly TOTAL_STEPS_TO_FINISH
        self.assertTrue(self.token.can_move(1))  # FINISH_POSITION + 1 = TOTAL_STEPS_TO_FINISH <= TOTAL_STEPS_TO_FINISH

        # Should not be able to move with rolls that exceed TOTAL_STEPS_TO_FINISH
        self.assertFalse(self.token.can_move(2))  # FINISH_POSITION + 2 = 58 > TOTAL_STEPS_TO_FINISH
        self.assertFalse(self.token.can_move(6))  # FINISH_POSITION + 6 = 62 > TOTAL_STEPS_TO_FINISH

        # Test actual move to finish
        success = self.token.move(1)
        self.assertTrue(success)
        self.assertEqual(self.token.steps_taken, LudoConstants.TOTAL_STEPS_TO_FINISH)
        self.assertEqual(self.token.state, TokenState.FINISHED)
        self.assertEqual(self.token.position, LudoConstants.FINISH_POSITION)

    def test_board_calculate_position_near_finish(self):
        """Test board position calculation near finish."""
        board = Board()
        token = Token(token_id=0, color="red")
        token.state = TokenState.ACTIVE

        # Test with 53 steps taken
        token.steps_taken = 53

        # Rolling 4 should lead to finish
        position = board._calculate_new_position(token, 4)
        self.assertEqual(position, LudoConstants.FINISH_POSITION)  # Finish position

        # Rolling 2 should lead to normal position calculation
        position = board._calculate_new_position(token, 2)
        # With red token starting at 0: (0 + 55 - 1) % BOARD_SIZE = 54
        self.assertEqual(position, 54)

    def test_token_exit_home(self):
        """Test token exiting home with roll of 6."""
        self.assertTrue(self.token.can_move(6))  # Should be able to exit home

        success = self.token.move(6)
        self.assertTrue(success)
        self.assertEqual(self.token.state, TokenState.ACTIVE)
        self.assertEqual(self.token.steps_taken, 1)
        self.assertEqual(self.token.position, 0)  # Red starts at 0

        # After exiting home, should not be able to exit again
        self.token.position = -1
        self.token.state = TokenState.HOME
        self.token.steps_taken = 0

        # Non-6 rolls should not allow exiting home
        self.assertFalse(self.token.can_move(1))
        self.assertFalse(self.token.can_move(5))

    def test_token_start_positions(self):
        """Test token start positions for different colors."""
        red_token = Token(token_id=0, color="red")
        blue_token = Token(token_id=0, color="blue")
        green_token = Token(token_id=0, color="green")
        yellow_token = Token(token_id=0, color="yellow")

        self.assertEqual(red_token._get_start_position(), 0)
        self.assertEqual(blue_token._get_start_position(), 14)
        self.assertEqual(green_token._get_start_position(), 28)
        self.assertEqual(yellow_token._get_start_position(), 42)

    def test_prevent_overshooting_finish(self):
        """Test that overshooting the finish is properly prevented."""
        # This test ensures that even if can_move() fails, the board logic is robust
        board = Board()
        token = Token(token_id=0, color="red")
        token.state = TokenState.ACTIVE
        token.steps_taken = LudoConstants.FINISH_POSITION

        # Test overshooting: FINISH_POSITION + 2 = 58 > TOTAL_STEPS_TO_FINISH
        position = board._calculate_new_position(token, 2)
        self.assertEqual(position, -1)  # Should return -1 for invalid move

        # Test exact finish: FINISH_POSITION + 1 = TOTAL_STEPS_TO_FINISH
        position = board._calculate_new_position(token, 1)
        self.assertEqual(position, LudoConstants.FINISH_POSITION)  # Should return finish position

        # Test normal move: 53 + 2 = 55
        token.steps_taken = 53
        position = board._calculate_new_position(token, 2)
        # Red token: (0 + 55 - 1) % BOARD_SIZE = 54
        self.assertEqual(position, 54)

    def test_get_start_position(self):
        """Test getting start position for different colors."""
        red_token = Token(0, "red")
        blue_token = Token(0, "blue")
        green_token = Token(0, "green")
        yellow_token = Token(0, "yellow")

        self.assertEqual(red_token._get_start_position(), 0)
        self.assertEqual(blue_token._get_start_position(), 14)
        self.assertEqual(green_token._get_start_position(), 28)
        self.assertEqual(yellow_token._get_start_position(), 42)

    def test_repr(self):
        """Test string representation."""
        repr_str = repr(self.token)
        self.assertIn("Token(red_0", repr_str)
        self.assertIn("pos=-1", repr_str)
        self.assertIn("state=home", repr_str)

    def test_equality(self):
        """Test token equality."""
        token1 = Token(0, "red")
        token2 = Token(0, "red")
        token3 = Token(1, "red")
        token4 = Token(0, "blue")

        self.assertEqual(token1, token2)
        self.assertNotEqual(token1, token3)
        self.assertNotEqual(token1, token4)
        self.assertNotEqual(token1, "not a token")

    def test_to_dict(self):
        """Test converting token to dictionary."""
        token_dict = self.token.to_dict()
        expected = {
            "token_id": 0,
            "color": "red",
            "position": -1,
            "state": "home",
            "steps_taken": 0,
        }
        self.assertEqual(token_dict, expected)

    def test_from_dict(self):
        """Test creating token from dictionary."""
        data = {
            "token_id": 1,
            "color": "blue",
            "position": 5,
            "state": "active",
            "steps_taken": 6,
        }
        token = Token.from_dict(data)
        self.assertEqual(token.token_id, 1)
        self.assertEqual(token.color, "blue")
        self.assertEqual(token.position, 5)
        self.assertEqual(token.state, TokenState.ACTIVE)
        self.assertEqual(token.steps_taken, 6)


class TestPlayer(unittest.TestCase):
    """Comprehensive test cases for Player class."""

    def setUp(self):
        """Set up test fixtures."""
        self.player = Player("red", "Test Player")

    def test_initialization(self):
        """Test player initialization."""
        self.assertEqual(self.player.color, "red")
        self.assertEqual(self.player.name, "Test Player")
        self.assertIsNone(self.player.strategy)
        self.assertEqual(len(self.player.tokens), 4)
        self.assertEqual(self.player.tokens_finished, 0)
        self.assertEqual(self.player.tokens_captured, 0)

    def test_initialization_default_name(self):
        """Test player initialization with default name."""
        player = Player("blue")
        self.assertEqual(player.name, "Player_blue")

    def test_get_tokens_at_home(self):
        """Test getting tokens at home."""
        tokens_at_home = self.player.get_tokens_at_home()
        self.assertEqual(len(tokens_at_home), 4)
        self.assertTrue(all(token.is_at_home() for token in tokens_at_home))

    def test_get_active_tokens(self):
        """Test getting active tokens."""
        active_tokens = self.player.get_active_tokens()
        self.assertEqual(len(active_tokens), 0)

        # Move a token to active
        self.player.tokens[0].state = TokenState.ACTIVE
        active_tokens = self.player.get_active_tokens()
        self.assertEqual(len(active_tokens), 1)

    def test_get_finished_tokens(self):
        """Test getting finished tokens."""
        finished_tokens = self.player.get_finished_tokens()
        self.assertEqual(len(finished_tokens), 0)

        # Move a token to finished
        self.player.tokens[0].state = TokenState.FINISHED
        finished_tokens = self.player.get_finished_tokens()
        self.assertEqual(len(finished_tokens), 1)

    def test_get_movable_tokens(self):
        """Test getting movable tokens."""
        # All tokens at home, only movable with 6
        movable = self.player.get_movable_tokens(6)
        self.assertEqual(len(movable), 4)

        movable = self.player.get_movable_tokens(5)
        self.assertEqual(len(movable), 0)

        # Move one token to active
        self.player.tokens[0].state = TokenState.ACTIVE
        self.player.tokens[0].steps_taken = 5
        movable = self.player.get_movable_tokens(3)
        self.assertEqual(len(movable), 1)

    def test_has_won(self):
        """Test checking if player has won."""
        self.assertFalse(self.player.has_won())

        # Set all tokens to finished
        for token in self.player.tokens:
            token.state = TokenState.FINISHED
        self.assertTrue(self.player.has_won())

    def test_can_make_move(self):
        """Test checking if player can make any move."""
        # All tokens at home
        self.assertTrue(self.player.can_make_move(6))
        self.assertFalse(self.player.can_make_move(5))

        # Move one token to active
        self.player.tokens[0].state = TokenState.ACTIVE
        self.player.tokens[0].steps_taken = 5
        self.assertTrue(self.player.can_make_move(3))

    def test_choose_move_with_strategy(self):
        """Test choosing move with strategy."""
        mock_strategy = Mock(spec=BaseStrategy)
        mock_token = Mock(spec=Token)
        mock_token.can_move.return_value = True
        mock_strategy.choose_move.return_value = mock_token

        self.player.set_strategy(mock_strategy)

        # Set up a token that can move
        self.player.tokens[0].can_move = Mock(return_value=True)

        result = self.player.choose_move(3, {})
        self.assertEqual(result, mock_token)
        mock_strategy.choose_move.assert_called_once()

    def test_choose_move_without_strategy(self):
        """Test choosing move without strategy (default behavior)."""
        # Move one token to active so it can move
        self.player.tokens[0].state = TokenState.ACTIVE
        self.player.tokens[0].steps_taken = 5

        result = self.player.choose_move(3, {})
        self.assertEqual(result, self.player.tokens[0])

    def test_choose_move_no_moves(self):
        """Test choosing move when no moves are possible."""
        result = self.player.choose_move(5, {})  # Can't move from home with 5
        self.assertIsNone(result)

    def test_set_strategy(self):
        """Test setting strategy."""
        mock_strategy = Mock(spec=BaseStrategy)
        self.player.set_strategy(mock_strategy)
        self.assertEqual(self.player.strategy, mock_strategy)
        mock_strategy.set_player.assert_called_once_with(self.player)

    def test_update_stats(self):
        """Test updating player statistics."""
        # Test six rolled
        self.player.update_stats(6, True)
        self.assertEqual(self.player.sixes_rolled, 1)
        self.assertEqual(self.player.total_moves, 1)

        # Test capture
        captured_tokens = [Mock(spec=Token), Mock(spec=Token)]
        self.player.update_stats(3, True, captured_tokens)
        self.assertEqual(self.player.tokens_captured, 2)
        self.assertEqual(self.player.total_moves, 2)

        # Test failed move
        self.player.update_stats(4, False)
        self.assertEqual(self.player.total_moves, 2)  # Should not increment

    def test_get_position_summary(self):
        """Test getting position summary."""
        summary = self.player.get_position_summary()
        self.assertEqual(summary.home, 4)
        self.assertEqual(summary.active, 0)
        self.assertEqual(summary.finished, 0)
        self.assertEqual(summary.total, 4)

    def test_get_stats(self):
        """Test getting player statistics."""
        stats = self.player.get_stats()
        self.assertEqual(stats.color, "red")
        self.assertEqual(stats.name, "Test Player")
        self.assertEqual(stats.tokens_finished, 0)
        self.assertEqual(stats.tokens_captured, 0)
        self.assertEqual(stats.total_moves, 0)
        self.assertEqual(stats.sixes_rolled, 0)

    def test_reset(self):
        """Test resetting player to initial state."""
        # Set up some state
        self.player.tokens[0].state = TokenState.ACTIVE
        self.player.tokens[0].position = 10
        self.player.tokens[0].steps_taken = 11
        self.player.tokens_finished = 2
        self.player.tokens_captured = 3
        self.player.total_moves = 15
        self.player.sixes_rolled = 4

        self.player.reset()

        # Check tokens are reset
        self.assertTrue(all(token.is_at_home() for token in self.player.tokens))
        self.assertEqual(self.player.tokens_finished, 0)
        self.assertEqual(self.player.tokens_captured, 0)
        self.assertEqual(self.player.total_moves, 0)
        self.assertEqual(self.player.sixes_rolled, 0)

    def test_to_dict(self):
        """Test converting player to dictionary."""
        player_dict = self.player.to_dict()
        self.assertEqual(player_dict["color"], "red")
        self.assertEqual(player_dict["name"], "Test Player")
        self.assertEqual(len(player_dict["tokens"]), 4)

    def test_from_dict(self):
        """Test creating player from dictionary."""
        data = {
            "color": "blue",
            "name": "Test Blue",
            "tokens": [
                {
                    "token_id": 0,
                    "color": "blue",
                    "position": 5,
                    "steps_taken": 6,
                    "is_finished": False,
                    "is_at_home": False,
                }
            ],
            "stats": {
                "tokens_finished": 1,
                "tokens_captured": 2,
                "total_moves": 10,
                "sixes_rolled": 3,
            },
        }

        player = Player.from_dict(data)
        self.assertEqual(player.color, "blue")
        self.assertEqual(player.name, "Test Blue")
        self.assertEqual(len(player.tokens), 1)
        self.assertEqual(player.tokens_finished, 1)
        self.assertEqual(player.tokens_captured, 2)

    def test_repr(self):
        """Test string representation."""
        repr_str = repr(self.player)
        self.assertIn("Player(Test Player", repr_str)
        self.assertIn("red", repr_str)
        self.assertIn("tokens_finished=0", repr_str)

    def test_equality(self):
        """Test player equality."""
        player1 = Player("red", "Player1")
        player2 = Player("red", "Player2")
        player3 = Player("blue", "Player1")

        self.assertEqual(player1, player2)  # Same color
        self.assertNotEqual(player1, player3)  # Different color
        self.assertNotEqual(player1, "not a player")


class TestBoard(unittest.TestCase):
    """Comprehensive test cases for Board class."""

    def setUp(self):
        """Set up test fixtures."""
        self.board = Board()
        self.red_token = Token(0, "red")
        self.blue_token = Token(0, "blue")

    def test_initialization(self):
        """Test board initialization."""
        self.assertEqual(len(self.board.positions), LudoConstants.TOTAL_STEPS_TO_FINISH)  # 0-FINISH_POSITION
        self.assertIsInstance(self.board.safe_positions, set)

    def test_is_safe_position(self):
        """Test checking if position is safe."""
        # Test some known safe positions
        self.assertTrue(self.board.is_safe_position(14))  # Blue start
        self.assertTrue(self.board.is_safe_position(28))  # Green start
        self.assertFalse(self.board.is_safe_position(5))  # Regular position

    def test_get_tokens_at_position(self):
        """Test getting tokens at specific position."""
        tokens = self.board.get_tokens_at_position(5)
        self.assertEqual(len(tokens), 0)

        # Place a token
        self.board.place_token(self.red_token, 5)
        tokens = self.board.get_tokens_at_position(5)
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0], self.red_token)

    def test_place_token_valid_position(self):
        """Test placing token at valid position."""
        success = self.board.place_token(self.red_token, 5)
        self.assertTrue(success)
        self.assertEqual(self.red_token.position, 5)
        self.assertIn(self.red_token, self.board.positions[5])

    def test_place_token_invalid_position(self):
        """Test placing token at invalid position."""
        success = self.board.place_token(self.red_token, 100)
        self.assertFalse(success)

    def test_remove_token(self):
        """Test removing token from board."""
        # Place token first
        self.board.place_token(self.red_token, 5)
        self.assertIn(self.red_token, self.board.positions[5])

        # Remove token
        self.board.remove_token(self.red_token)
        self.assertNotIn(self.red_token, self.board.positions[5])

    def test_move_token_from_home(self):
        """Test moving token from home."""
        success, captured = self.board.move_token(self.red_token, 6)
        self.assertTrue(success)
        self.assertEqual(len(captured), 0)
        self.assertEqual(self.red_token.position, 0)  # Red start position

    def test_move_token_invalid_from_home(self):
        """Test invalid move from home."""
        success, captured = self.board.move_token(self.red_token, 5)
        self.assertFalse(success)
        self.assertEqual(len(captured), 0)

    def test_move_token_with_capture(self):
        """Test moving token that captures opponent."""
        # Place blue token at position 5
        self.board.place_token(self.blue_token, 5)

        # Move red token to position 5 (should capture blue)
        self.red_token.state = TokenState.ACTIVE
        self.red_token.position = 2
        self.red_token.steps_taken = 3

        success, captured = self.board.move_token(self.red_token, 3)
        self.assertTrue(success)
        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0], self.blue_token)
        self.assertTrue(self.blue_token.is_at_home())

    def test_move_token_to_safe_position(self):
        """Test moving token to safe position (no capture)."""
        # Place blue token at safe position 14
        self.board.place_token(self.blue_token, 14)

        # Move red token to position 14
        self.red_token.state = TokenState.ACTIVE
        self.red_token.position = 11
        self.red_token.steps_taken = 12

        success, captured = self.board.move_token(self.red_token, 3)
        self.assertTrue(success)
        self.assertEqual(len(captured), 0)  # No capture on safe position

    def test_get_possible_moves(self):
        """Test getting possible moves for a player."""
        # Place red token at position 5
        self.board.place_token(self.red_token, 5)
        self.red_token.state = TokenState.ACTIVE
        self.red_token.steps_taken = 6

        moves = self.board.get_possible_moves("red", 3)
        self.assertEqual(len(moves), 1)
        self.assertEqual(moves[0][0], self.red_token)
        self.assertEqual(moves[0][1], 8)  # 5 + 3

    def test_is_blocked(self):
        """Test checking if position is blocked."""
        # Place two blue tokens at position 5
        blue_token2 = Token(1, "blue")
        self.board.place_token(self.blue_token, 5)
        self.board.place_token(blue_token2, 5)

        # Red token should be blocked
        self.assertTrue(self.board.is_blocked(self.red_token, 5))

        # Single opponent token should not block
        self.board.remove_token(blue_token2)
        self.assertFalse(self.board.is_blocked(self.red_token, 5))

    def test_get_board_state(self):
        """Test getting board state."""
        # Place some tokens
        self.board.place_token(self.red_token, 5)
        self.board.place_token(self.blue_token, 10)

        state = self.board.get_board_state()
        self.assertIn(5, state)
        self.assertIn(10, state)
        self.assertEqual(len(state[5]), 1)
        self.assertEqual(len(state[10]), 1)

    def test_get_color_positions(self):
        """Test getting positions for specific color."""
        self.board.place_token(self.red_token, 5)
        self.board.place_token(self.blue_token, 10)

        red_positions = self.board.get_color_positions("red")
        blue_positions = self.board.get_color_positions("blue")

        self.assertEqual(red_positions, [5])
        self.assertEqual(blue_positions, [10])

    def test_count_tokens_at_finish(self):
        """Test counting finished tokens."""
        # Place red token at finish
        self.board.place_token(self.red_token, LudoConstants.FINISH_POSITION)

        count = self.board.count_tokens_at_finish("red")
        self.assertEqual(count, 1)

        count = self.board.count_tokens_at_finish("blue")
        self.assertEqual(count, 0)

    def test_is_game_finished(self):
        """Test checking if game is finished."""
        self.assertFalse(self.board.is_game_finished())

        # Place 4 red tokens at finish
        for i in range(4):
            token = Token(i, "red")
            self.board.place_token(token, LudoConstants.FINISH_POSITION)

        self.assertTrue(self.board.is_game_finished())

    def test_get_winner(self):
        """Test getting game winner."""
        self.assertIsNone(self.board.get_winner())

        # Place 4 red tokens at finish
        for i in range(4):
            token = Token(i, "red")
            self.board.place_token(token, LudoConstants.FINISH_POSITION)

        self.assertEqual(self.board.get_winner(), "red")

    def test_repr(self):
        """Test string representation."""
        # Place some tokens
        self.board.place_token(self.red_token, 5)
        self.board.place_token(self.blue_token, 10)

        repr_str = repr(self.board)
        self.assertIn("pos5", repr_str)
        self.assertIn("pos10", repr_str)


if __name__ == "__main__":
    unittest.main()
