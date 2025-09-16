"""
Comprehensive unit tests for Board class.
Tests cover position validation, token placement, capture logic, blocking positions,
and board state representation.
"""

import unittest

from ludo_engine.board import Board, Position
from ludo_engine.constants import BoardConstants
from ludo_engine.player import Player, PlayerColor
from ludo_engine.token import TokenState


class TestBoard(unittest.TestCase):
    """Test cases for Board class."""

    def setUp(self):
        """Set up test fixtures."""
        self.board = Board()
        self.player_red = Player(PlayerColor.RED, 0)
        self.player_blue = Player(PlayerColor.BLUE, 1)
        self.token_red = self.player_red.tokens[0]
        self.token_blue = self.player_blue.tokens[0]

    def test_initialization(self):
        """Test board initialization."""
        self.assertEqual(self.board.main_path_size, 52)
        self.assertEqual(self.board.home_column_size, 6)
        self.assertEqual(len(self.board.positions), 58)  # 52 main + 6 home

        # Check that positions are initialized
        for i in range(52):
            self.assertIsInstance(self.board.positions[i], Position)

        for i in range(100, 106):
            self.assertIsInstance(self.board.positions[i], Position)

    def test_reset_token_positions(self):
        """Test resetting token positions."""
        # Add some tokens
        self.board.add_token(self.token_red, 5)
        self.board.add_token(self.token_blue, 10)

        # Reset
        self.board.reset_token_positions()

        # Check positions are empty
        self.assertEqual(len(self.board.get_tokens_at_position(5)), 0)
        self.assertEqual(len(self.board.get_tokens_at_position(10)), 0)

    def test_add_and_remove_token(self):
        """Test adding and removing tokens."""
        # Add token
        self.board.add_token(self.token_red, 5)
        tokens = self.board.get_tokens_at_position(5)
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0], self.token_red)

        # Remove token
        self.board.remove_token(self.token_red, 5)
        tokens = self.board.get_tokens_at_position(5)
        self.assertEqual(len(tokens), 0)

    def test_multi_token_tracking(self):
        """Test tracking of multiple tokens per position."""
        token_red2 = self.player_red.tokens[1]

        # Add two tokens of same color
        self.board.add_token(self.token_red, 5)
        self.board.add_token(token_red2, 5)

        # Should be tracked as multi-token position
        self.assertIn(5, self.board._multi_token_positions[PlayerColor.RED.value])

        # Remove one token
        self.board.remove_token(self.token_red, 5)

        # Should no longer be tracked (now has only 1 token)
        self.assertNotIn(5, self.board._multi_token_positions[PlayerColor.RED.value])

        # Remove second token
        self.board.remove_token(token_red2, 5)

        # Should still not be tracked
        self.assertNotIn(5, self.board._multi_token_positions[PlayerColor.RED.value])

    def test_is_position_safe(self):
        """Test safe position detection."""
        # Star positions are safe
        for pos in BoardConstants.STAR_SQUARES:
            self.assertTrue(self.board.is_position_safe(pos, "red"))
            self.assertTrue(self.board.is_position_safe(pos, "blue"))

        # Colored safe squares
        red_safe = BoardConstants.COLORED_SAFE_SQUARES["red"]
        for pos in red_safe:
            self.assertTrue(self.board.is_position_safe(pos, "red"))
            # Starting positions are safe for everyone, not just the owning color
            if pos in BoardConstants.START_POSITIONS.values():
                self.assertTrue(self.board.is_position_safe(pos, "blue"))
            else:
                self.assertFalse(self.board.is_position_safe(pos, "blue"))

        # Regular positions are not safe
        self.assertFalse(self.board.is_position_safe(5, "red"))
        self.assertFalse(self.board.is_position_safe(15, "blue"))

    def test_can_move_to_position_empty(self):
        """Test moving to empty position."""
        can_move, captured = self.board.can_move_to_position(self.token_red, 5)
        self.assertTrue(can_move)
        self.assertEqual(len(captured), 0)

    def test_can_move_to_position_safe_with_opponent(self):
        """Test moving to safe position with opponent tokens."""
        # Add opponent token to safe position
        self.board.add_token(self.token_blue, 8)  # Star position

        # Red token should be able to move there (safe positions allow it)
        can_move, captured = self.board.can_move_to_position(self.token_red, 8)
        self.assertTrue(can_move)
        self.assertEqual(len(captured), 0)  # No captures in safe positions

    def test_can_move_to_position_unsafe_single_opponent(self):
        """Test moving to unsafe position with single opponent token."""
        # Add opponent token to unsafe position
        self.board.add_token(self.token_blue, 5)

        # Red token should capture it
        can_move, captured = self.board.can_move_to_position(self.token_red, 5)
        self.assertTrue(can_move)
        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0], self.token_blue)

    def test_can_move_to_position_blocked_by_two_opponents(self):
        """Test moving to position blocked by two opponent tokens."""
        token_blue2 = self.player_blue.tokens[1]

        # Add two opponent tokens to same position
        self.board.add_token(self.token_blue, 5)
        self.board.add_token(token_blue2, 5)

        # Red token should not be able to move there
        can_move, captured = self.board.can_move_to_position(self.token_red, 5)
        self.assertFalse(can_move)
        self.assertEqual(len(captured), 0)

    def test_can_move_to_position_own_tokens(self):
        """Test moving to position with own tokens."""
        token_red2 = self.player_red.tokens[1]

        # Add own tokens to position
        self.board.add_token(self.token_red, 5)
        self.board.add_token(token_red2, 5)

        # Should be able to stack
        can_move, captured = self.board.can_move_to_position(
            self.player_red.tokens[2], 5
        )
        self.assertTrue(can_move)
        self.assertEqual(len(captured), 0)

    def test_execute_move_capture(self):
        """Test executing move with capture."""
        # Set up tokens
        self.token_red.state = TokenState.ACTIVE
        self.token_red.position = 1
        self.token_blue.state = TokenState.ACTIVE
        self.token_blue.position = 5

        self.board.add_token(self.token_blue, 5)

        # Execute move that captures
        captured = self.board.execute_move(self.token_red, 1, 5)

        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0], self.token_blue)
        self.assertEqual(self.token_blue.state, TokenState.HOME)
        self.assertEqual(self.token_blue.position, -1)

        # Check token positions
        self.assertEqual(len(self.board.get_tokens_at_position(1)), 0)
        self.assertEqual(len(self.board.get_tokens_at_position(5)), 1)
        self.assertEqual(self.board.get_tokens_at_position(5)[0], self.token_red)

    def test_execute_move_no_capture(self):
        """Test executing move without capture."""
        # Set up token
        self.token_red.state = TokenState.ACTIVE
        self.token_red.position = 1

        # Execute move to empty position
        captured = self.board.execute_move(self.token_red, 1, 5)

        self.assertEqual(len(captured), 0)

        # Check token positions
        self.assertEqual(len(self.board.get_tokens_at_position(1)), 0)
        self.assertEqual(len(self.board.get_tokens_at_position(5)), 1)
        self.assertEqual(self.board.get_tokens_at_position(5)[0], self.token_red)

    def test_execute_move_invalid(self):
        """Test executing invalid move."""
        # Set up token
        self.token_red.state = TokenState.ACTIVE
        self.token_red.position = 1

        # Try to move to invalid position
        captured = self.board.execute_move(self.token_red, 1, 60)  # Invalid position

        # Should not move
        self.assertEqual(len(captured), 0)
        self.assertEqual(
            len(self.board.get_tokens_at_position(1)), 0
        )  # Token not at old position
        # Note: In current implementation, token might be added to invalid position
        # This tests the expected behavior

    def test_get_board_state_for_ai(self):
        """Test getting board state for AI."""
        # Add some tokens
        self.board.add_token(self.token_red, 5)
        self.board.add_token(self.token_blue, 10)

        board_state = self.board.get_board_state_for_ai(self.player_red)

        self.assertEqual(board_state.current_player, "red")
        self.assertIn(5, board_state.board_positions)
        self.assertIn(10, board_state.board_positions)
        self.assertEqual(len(board_state.board_positions[5]), 1)
        self.assertEqual(len(board_state.board_positions[10]), 1)

    def test_get_position_info_main_board(self):
        """Test getting position info for main board."""
        # Add token to position
        self.board.add_token(self.token_red, 5)

        info = self.board.get_position_info(5)

        self.assertEqual(info.type, "main_board")
        self.assertEqual(info.position, 5)
        self.assertFalse(info.is_safe)  # Position 5 is not safe
        self.assertEqual(len(info.tokens), 1)

    def test_get_position_info_safe_position(self):
        """Test getting position info for safe position."""
        info = self.board.get_position_info(8)  # Star position

        self.assertEqual(info.type, "main_board")
        self.assertTrue(info.is_safe)
        self.assertTrue(info.is_star)

    def test_get_position_info_home_column(self):
        """Test getting position info for home column."""
        # Add token to home column
        self.token_red.state = TokenState.HOME_COLUMN
        self.token_red.position = 100
        self.board.add_token(self.token_red, 100)

        info = self.board.get_position_info(100)

        self.assertEqual(info.type, "home_column")
        self.assertTrue(info.is_safe)
        self.assertEqual(len(info.tokens), 1)

    def test_get_position_info_home(self):
        """Test getting position info for home."""
        info = self.board.get_position_info(-1)

        self.assertEqual(info.type, "home")
        self.assertTrue(info.is_safe)
        self.assertEqual(len(info.tokens), 0)

    def test_get_position_info_unknown(self):
        """Test getting position info for unknown position."""
        info = self.board.get_position_info(999)

        self.assertEqual(info.type, "unknown")
        self.assertFalse(info.is_safe)
        self.assertEqual(len(info.tokens), 0)

    def test_blocking_positions_calculation(self):
        """Test blocking positions calculation."""
        # Add two tokens of same color to same position
        token_red2 = self.player_red.tokens[1]
        self.board.add_token(self.token_red, 5)
        self.board.add_token(token_red2, 5)

        blocking = self.board.get_blocking_positions("red")
        self.assertIn(5, blocking)

        # Add another blocking position
        token_red3 = self.player_red.tokens[2]
        token_red4 = self.player_red.tokens[3]
        self.board.add_token(token_red3, 15)
        self.board.add_token(token_red4, 15)

        blocking = self.board.get_blocking_positions("red")
        self.assertIn(5, blocking)
        self.assertIn(15, blocking)

    def test_blocking_positions_safe_squares(self):
        """Test that safe squares don't create blocking positions."""
        # Add two tokens to safe position
        self.board.add_token(self.token_red, 8)  # Star position
        self.board.add_token(self.player_red.tokens[1], 8)

        blocking = self.board.get_blocking_positions("red")
        self.assertNotIn(8, blocking)  # Safe squares don't block

    def test_get_all_blocking_positions(self):
        """Test getting blocking positions for all players."""
        # Set up blocking for red
        self.board.add_token(self.token_red, 5)
        self.board.add_token(self.player_red.tokens[1], 5)

        # Set up blocking for blue
        self.board.add_token(self.token_blue, 10)
        self.board.add_token(self.player_blue.tokens[1], 10)

        all_blocking = self.board.get_all_blocking_positions()

        self.assertIn(5, all_blocking["red"])
        self.assertIn(10, all_blocking["blue"])
        self.assertNotIn(5, all_blocking["blue"])
        self.assertNotIn(10, all_blocking["red"])

    def test_has_blocking_position(self):
        """Test checking if specific position is blocking."""
        # Set up blocking
        self.board.add_token(self.token_red, 5)
        self.board.add_token(self.player_red.tokens[1], 5)

        self.assertTrue(self.board.has_blocking_position("red", 5))
        self.assertFalse(self.board.has_blocking_position("red", 10))
        self.assertFalse(self.board.has_blocking_position("blue", 5))

    def test_has_blocking_position_safe_square(self):
        """Test that safe squares are not considered blocking."""
        # Add multiple tokens to safe square
        self.board.add_token(self.token_red, 8)  # Star position
        self.board.add_token(self.player_red.tokens[1], 8)

        self.assertFalse(self.board.has_blocking_position("red", 8))

    def test_has_blocking_position_invalid_position(self):
        """Test invalid positions are not blocking."""
        self.assertFalse(self.board.has_blocking_position("red", -1))
        self.assertFalse(self.board.has_blocking_position("red", 60))

    def test_blocking_cache_invalidation(self):
        """Test blocking cache invalidation."""
        # Initially cache should be invalid
        self.assertFalse(self.board._cache_valid)

        # Getting blocking positions should build cache
        self.board.get_blocking_positions("red")
        self.assertTrue(self.board._cache_valid)

        # Adding token should invalidate cache
        self.board.add_token(self.token_red, 5)
        self.assertFalse(self.board._cache_valid)

    def test_update_token_position(self):
        """Test updating token position tracking."""
        # Add token to position 5
        self.board.add_token(self.token_red, 5)
        self.assertEqual(len(self.board.get_tokens_at_position(5)), 1)

        # Update position to 10
        self.board.update_token_position(self.token_red, 5, 10)
        self.assertEqual(len(self.board.get_tokens_at_position(5)), 0)
        self.assertEqual(len(self.board.get_tokens_at_position(10)), 1)

    def test_string_representation(self):
        """Test string representation of board."""
        # Add some tokens
        self.board.add_token(self.token_red, 5)
        self.board.add_token(self.token_blue, 10)

        str_repr = str(self.board)
        self.assertIn("Board State", str_repr)
        self.assertIn("Position 5", str_repr)
        self.assertIn("Position 10", str_repr)

    def test_complex_capture_scenario(self):
        """Test complex capture scenario with multiple tokens."""
        # Set up three tokens at same position: 2 red, 1 blue
        token_red2 = self.player_red.tokens[1]
        self.board.add_token(self.token_red, 5)
        self.board.add_token(token_red2, 5)
        self.board.add_token(self.token_blue, 5)

        # Red token tries to move to this position
        can_move, captured = self.board.can_move_to_position(
            self.player_red.tokens[2], 5
        )

        # Should be able to move and capture (can stack with own tokens, can capture unprotected opponent)
        self.assertTrue(can_move)
        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0], self.token_blue)

    def test_home_column_positions(self):
        """Test home column position handling."""
        # Test that home column positions are properly initialized
        for i in range(100, 106):
            self.assertIn(i, self.board.positions)
            self.assertIsInstance(self.board.positions[i], Position)

        # Test token placement in home column
        self.token_red.state = TokenState.HOME_COLUMN
        self.token_red.position = 100
        self.board.add_token(self.token_red, 100)

        tokens = self.board.get_tokens_at_position(100)
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0], self.token_red)


if __name__ == "__main__":
    unittest.main()
