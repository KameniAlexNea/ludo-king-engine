"""
Test cases for token positioning in Ludo board visualization.

This module tests the _get_token_position function to ensure tokens are
positioned correctly based on their state, color, steps taken, and position.
"""

import unittest
from typing import Tuple

from ludo_engine.core.constants import Colors, LudoConstants
from ludo_engine.core.token import Token, TokenState
from ludo_interface.board_viz import _get_token_position


class TestTokenPositioning(unittest.TestCase):
    """Test cases for token positioning functionality."""

    def test_home_tokens_red(self):
        """Test red tokens in home nest positions."""
        # Red tokens in home: positions (0+ox+0.5, 9+oy+0.5)
        # nest_offsets = [(1, 1), (4, 1), (1, 4), (4, 4)]
        expected_positions = [
            (1.5, 10.5),  # token 0: (0+1+0.5, 9+1+0.5)
            (4.5, 10.5),  # token 1: (0+4+0.5, 9+1+0.5)
            (1.5, 13.5),  # token 2: (0+1+0.5, 9+4+0.5)
            (4.5, 13.5),  # token 3: (0+4+0.5, 9+4+0.5)
        ]

        for token_id, expected_pos in enumerate(expected_positions):
            with self.subTest(token_id=token_id):
                token = Token(token_id=token_id, color=Colors.RED, state=TokenState.HOME)
                actual_pos = _get_token_position(token)
                self.assertEqual(actual_pos, expected_pos,
                    f"Red token {token_id} should be at {expected_pos}, got {actual_pos}")

    def test_home_tokens_green(self):
        """Test green tokens in home nest positions."""
        # Green tokens in home: positions (9+ox+0.5, 9+oy+0.5)
        expected_positions = [
            (10.5, 10.5),  # token 0: (9+1+0.5, 9+1+0.5)
            (13.5, 10.5),  # token 1: (9+4+0.5, 9+1+0.5)
            (10.5, 13.5),  # token 2: (9+1+0.5, 9+4+0.5)
            (13.5, 13.5),  # token 3: (9+4+0.5, 9+4+0.5)
        ]

        for token_id, expected_pos in enumerate(expected_positions):
            with self.subTest(token_id=token_id):
                token = Token(token_id=token_id, color=Colors.GREEN, state=TokenState.HOME)
                actual_pos = _get_token_position(token)
                self.assertEqual(actual_pos, expected_pos,
                    f"Green token {token_id} should be at {expected_pos}, got {actual_pos}")

    def test_home_tokens_blue(self):
        """Test blue tokens in home nest positions."""
        # Blue tokens in home: positions (0+ox+0.5, 0+oy+0.5)
        expected_positions = [
            (1.5, 1.5),   # token 0: (0+1+0.5, 0+1+0.5)
            (4.5, 1.5),   # token 1: (0+4+0.5, 0+1+0.5)
            (1.5, 4.5),   # token 2: (0+1+0.5, 0+4+0.5)
            (4.5, 4.5),   # token 3: (0+4+0.5, 0+4+0.5)
        ]

        for token_id, expected_pos in enumerate(expected_positions):
            with self.subTest(token_id=token_id):
                token = Token(token_id=token_id, color=Colors.BLUE, state=TokenState.HOME)
                actual_pos = _get_token_position(token)
                self.assertEqual(actual_pos, expected_pos,
                    f"Blue token {token_id} should be at {expected_pos}, got {actual_pos}")

    def test_home_tokens_yellow(self):
        """Test yellow tokens in home nest positions."""
        # Yellow tokens in home: positions (9+ox+0.5, 0+oy+0.5)
        expected_positions = [
            (10.5, 1.5),  # token 0: (9+1+0.5, 0+1+0.5)
            (13.5, 1.5),  # token 1: (9+4+0.5, 0+1+0.5)
            (10.5, 4.5),  # token 2: (9+1+0.5, 0+4+0.5)
            (13.5, 4.5),  # token 3: (9+4+0.5, 0+4+0.5)
        ]

        for token_id, expected_pos in enumerate(expected_positions):
            with self.subTest(token_id=token_id):
                token = Token(token_id=token_id, color=Colors.YELLOW, state=TokenState.HOME)
                actual_pos = _get_token_position(token)
                self.assertEqual(actual_pos, expected_pos,
                    f"Yellow token {token_id} should be at {expected_pos}, got {actual_pos}")

    def test_active_tokens_start_positions(self):
        """Test tokens at their starting positions on the main path."""
        # Each color starts at different positions on the path
        expected_starts = {
            Colors.RED: (1.5, 8.5),     # (1+0.5, 8+0.5)
            Colors.GREEN: (8.5, 13.5),  # (8+0.5, 13+0.5)
            Colors.YELLOW: (13.5, 6.5), # (13+0.5, 6+0.5)
            Colors.BLUE: (6.5, 1.5),    # (6+0.5, 1+0.5)
        }

        for color, expected_pos in expected_starts.items():
            with self.subTest(color=color):
                token = Token(token_id=0, color=color, state=TokenState.ACTIVE, steps_taken=1)
                actual_pos = _get_token_position(token)
                self.assertEqual(actual_pos, expected_pos,
                    f"{color} token at start should be at {expected_pos}, got {actual_pos}")

    def test_active_tokens_path_progression_red(self):
        """Test red token progression along the main path."""
        # Test various steps for red tokens
        test_cases = [
            (1, (1.5, 8.5)),   # Start position
            (2, (2.5, 8.5)),   # Move right
            (3, (3.5, 8.5)),   # Continue right
            (5, (5.5, 8.5)),   # Further right
            (7, (6.5, 10.5)),  # Turn up
            (8, (6.5, 11.5)),  # Continue up
            (9, (6.5, 12.5)),  # Continue up
            (10, (6.5, 13.5)), # Continue up
        ]

        for steps, expected_pos in test_cases:
            with self.subTest(steps=steps):
                token = Token(token_id=0, color=Colors.RED, state=TokenState.ACTIVE, steps_taken=steps)
                actual_pos = _get_token_position(token)
                self.assertEqual(actual_pos, expected_pos,
                    f"Red token at {steps} steps should be at {expected_pos}, got {actual_pos}")

    def test_active_tokens_path_progression_green(self):
        """Test green token progression along the main path."""
        test_cases = [
            (1, (8.5, 13.5)),  # Start position
            (2, (8.5, 12.5)),  # Move up
            (3, (8.5, 11.5)),  # Continue up
            (5, (9.5, 8.5)),   # Turn right
            (7, (11.5, 8.5)),  # Continue right
            (8, (12.5, 8.5)),  # Continue right
            (9, (13.5, 8.5)),  # Continue right
            (10, (14.5, 8.5)), # Continue right
        ]

        for steps, expected_pos in test_cases:
            with self.subTest(steps=steps):
                token = Token(token_id=0, color=Colors.GREEN, state=TokenState.ACTIVE, steps_taken=steps)
                actual_pos = _get_token_position(token)
                self.assertEqual(actual_pos, expected_pos,
                    f"Green token at {steps} steps should be at {expected_pos}, got {actual_pos}")

    def test_active_tokens_path_progression_yellow(self):
        """Test yellow token progression along the main path."""
        test_cases = [
            (1, (13.5, 6.5)),  # Start position
            (2, (12.5, 6.5)),  # Move left
            (3, (11.5, 6.5)),  # Continue left
            (5, (8.5, 5.5)),   # Turn down
            (7, (8.5, 3.5)),   # Continue down
            (8, (8.5, 2.5)),   # Continue down
            (9, (8.5, 1.5)),   # Continue down
            (10, (8.5, 0.5)),  # Continue down
        ]

        for steps, expected_pos in test_cases:
            with self.subTest(steps=steps):
                token = Token(token_id=0, color=Colors.YELLOW, state=TokenState.ACTIVE, steps_taken=steps)
                actual_pos = _get_token_position(token)
                self.assertEqual(actual_pos, expected_pos,
                    f"Yellow token at {steps} steps should be at {expected_pos}, got {actual_pos}")

    def test_active_tokens_path_progression_blue(self):
        """Test blue token progression along the main path."""
        test_cases = [
            (1, (6.5, 1.5)),   # Start position
            (2, (6.5, 2.5)),   # Move down
            (3, (6.5, 3.5)),   # Continue down
            (5, (6.5, 5.5)),   # Further down
            (7, (4.5, 6.5)),   # Turn left
            (8, (3.5, 6.5)),   # Continue left
            (9, (2.5, 6.5)),   # Continue left
            (10, (1.5, 6.5)),  # Continue left
        ]

        for steps, expected_pos in test_cases:
            with self.subTest(steps=steps):
                token = Token(token_id=0, color=Colors.BLUE, state=TokenState.ACTIVE, steps_taken=steps)
                actual_pos = _get_token_position(token)
                self.assertEqual(actual_pos, expected_pos,
                    f"Blue token at {steps} steps should be at {expected_pos}, got {actual_pos}")

    def test_home_column_positions_red(self):
        """Test red tokens in home column positions."""
        # Red home column: x positions 1-5, y=7
        # Steps 57-61 correspond to home_steps 1-5
        test_cases = [
            (57, (2.5, 7.5)),  # home_step 1: x_pos = 1 + 1 = 2
            (58, (3.5, 7.5)),  # home_step 2: x_pos = 1 + 2 = 3
            (59, (4.5, 7.5)),  # home_step 3: x_pos = 1 + 3 = 4
            (60, (5.5, 7.5)),  # home_step 4: x_pos = 1 + 4 = 5
            (61, (6.5, 7.5)),  # home_step 5: x_pos = 1 + 5 = 6
        ]

        for steps, expected_pos in test_cases:
            with self.subTest(steps=steps):
                token = Token(token_id=0, color=Colors.RED, state=TokenState.ACTIVE, steps_taken=steps)
                actual_pos = _get_token_position(token)
                self.assertEqual(actual_pos, expected_pos,
                    f"Red token at {steps} steps (home) should be at {expected_pos}, got {actual_pos}")

    def test_home_column_positions_green(self):
        """Test green tokens in home column positions."""
        # Green home column: x=7, y positions 13-9
        # Steps 57-61 correspond to home_steps 1-5
        test_cases = [
            (57, (7.5, 12.5)),  # home_step 1: y_pos = 13 - 1 = 12
            (58, (7.5, 11.5)),  # home_step 2: y_pos = 13 - 2 = 11
            (59, (7.5, 10.5)),  # home_step 3: y_pos = 13 - 3 = 10
            (60, (7.5, 9.5)),   # home_step 4: y_pos = 13 - 4 = 9
            (61, (7.5, 8.5)),   # home_step 5: y_pos = 13 - 5 = 8
        ]

        for steps, expected_pos in test_cases:
            with self.subTest(steps=steps):
                token = Token(token_id=0, color=Colors.GREEN, state=TokenState.ACTIVE, steps_taken=steps)
                actual_pos = _get_token_position(token)
                self.assertEqual(actual_pos, expected_pos,
                    f"Green token at {steps} steps (home) should be at {expected_pos}, got {actual_pos}")

    def test_home_column_positions_yellow(self):
        """Test yellow tokens in home column positions."""
        # Yellow home column: x positions 13-9, y=7
        # Steps 57-61 correspond to home_steps 1-5
        test_cases = [
            (57, (12.5, 7.5)),  # home_step 1: x_pos = 13 - 1 = 12
            (58, (11.5, 7.5)),  # home_step 2: x_pos = 13 - 2 = 11
            (59, (10.5, 7.5)),  # home_step 3: x_pos = 13 - 3 = 10
            (60, (9.5, 7.5)),   # home_step 4: x_pos = 13 - 4 = 9
            (61, (8.5, 7.5)),   # home_step 5: x_pos = 13 - 5 = 8
        ]

        for steps, expected_pos in test_cases:
            with self.subTest(steps=steps):
                token = Token(token_id=0, color=Colors.YELLOW, state=TokenState.ACTIVE, steps_taken=steps)
                actual_pos = _get_token_position(token)
                self.assertEqual(actual_pos, expected_pos,
                    f"Yellow token at {steps} steps (home) should be at {expected_pos}, got {actual_pos}")

    def test_home_column_positions_blue(self):
        """Test blue tokens in home column positions."""
        # Blue home column: x=7, y positions 1-5
        # Steps 57-61 correspond to home_steps 1-5
        test_cases = [
            (57, (7.5, 2.5)),   # home_step 1: y_pos = 1 + 1 = 2
            (58, (7.5, 3.5)),   # home_step 2: y_pos = 1 + 2 = 3
            (59, (7.5, 4.5)),   # home_step 3: y_pos = 1 + 3 = 4
            (60, (7.5, 5.5)),   # home_step 4: y_pos = 1 + 4 = 5
            (61, (7.5, 6.5)),   # home_step 5: y_pos = 1 + 5 = 6
        ]

        for steps, expected_pos in test_cases:
            with self.subTest(steps=steps):
                token = Token(token_id=0, color=Colors.BLUE, state=TokenState.ACTIVE, steps_taken=steps)
                actual_pos = _get_token_position(token)
                self.assertEqual(actual_pos, expected_pos,
                    f"Blue token at {steps} steps (home) should be at {expected_pos}, got {actual_pos}")

    def test_finished_tokens_positions(self):
        """Test finished tokens in center triangle positions."""
        expected_positions = {
            Colors.RED: (6.5, 7.5),    # Left triangle
            Colors.GREEN: (7.5, 8.5),  # Top triangle
            Colors.YELLOW: (8.5, 7.5), # Right triangle
            Colors.BLUE: (7.5, 6.5),   # Bottom triangle
        }

        for color, expected_pos in expected_positions.items():
            with self.subTest(color=color):
                token = Token(token_id=0, color=color, state=TokenState.FINISHED)
                actual_pos = _get_token_position(token)
                self.assertEqual(actual_pos, expected_pos,
                    f"Finished {color} token should be at {expected_pos}, got {actual_pos}")

    def test_different_colors_same_steps_different_positions(self):
        """Test that tokens of different colors at same step count have different positions."""
        steps = 10
        positions = {}

        for color in [Colors.RED, Colors.GREEN, Colors.YELLOW, Colors.BLUE]:
            token = Token(token_id=0, color=color, state=TokenState.ACTIVE, steps_taken=steps)
            pos = _get_token_position(token)
            positions[color] = pos

        # All positions should be different
        pos_values = list(positions.values())
        self.assertEqual(len(pos_values), len(set(pos_values)),
            f"Tokens at same steps should have different positions: {positions}")

    def test_token_id_does_not_affect_position(self):
        """Test that token ID doesn't affect position (only nest positions use token_id)."""
        color = Colors.RED
        steps = 15

        positions = []
        for token_id in range(4):
            token = Token(token_id=token_id, color=color, state=TokenState.ACTIVE, steps_taken=steps)
            pos = _get_token_position(token)
            positions.append(pos)

        # All positions should be the same (except for home tokens)
        first_pos = positions[0]
        for pos in positions[1:]:
            self.assertEqual(pos, first_pos,
                f"All tokens with same color/steps should have same position: {positions}")

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test steps = 0 (should use fallback logic)
        token = Token(token_id=0, color=Colors.RED, state=TokenState.ACTIVE, steps_taken=0)
        pos = _get_token_position(token)
        self.assertIsInstance(pos, tuple)
        self.assertEqual(len(pos), 2)

        # Test very high steps (should wrap around path)
        token = Token(token_id=0, color=Colors.RED, state=TokenState.ACTIVE, steps_taken=100)
        pos = _get_token_position(token)
        self.assertIsInstance(pos, tuple)
        self.assertEqual(len(pos), 2)

        # Test unknown color (should use default index 0)
        token = Token(token_id=0, color="unknown", state=TokenState.ACTIVE, steps_taken=5)
        pos = _get_token_position(token)
        self.assertEqual(pos, (5.5, 8.5))  # Default fallback uses index 0 -> PATH_LIST[0] = (1,8) -> (1.5, 8.5), but with steps_taken=5: index (0+5-1)%50 = 4 -> PATH_LIST[4] = (5,8) -> (5.5, 8.5)


if __name__ == '__main__':
    unittest.main()