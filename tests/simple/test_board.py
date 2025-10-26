"""Board behaviour tests for the simplified engine."""

import unittest

from ludo_engine_simple import Board, CONFIG
from ludo_engine_simple.token import Token


class BoardTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.board = Board()

    def test_enter_board_places_token_at_start(self) -> None:
        token = Token("red", 0)

        result = self.board.enter_board(token)

        self.assertTrue(result.valid)
        self.assertEqual(result.end, CONFIG.start_offsets["red"])
        self.assertEqual(token.board_index, CONFIG.start_offsets["red"])

    def test_capture_on_non_safe_square_sends_token_home(self) -> None:
        red = Token("red", 0)
        blue = Token("blue", 0)

        self.board.enter_board(red)
        self.board.advance_token(red, 4)  # moves to index 4

        self.board.enter_board(blue)
        capture_result = self.board.advance_token(blue, 17)  # wrap to index 4

        self.assertIs(capture_result.captured, red)
        self.assertIsNone(red.board_index)
        self.assertEqual(red.steps_taken, 0)
        self.assertEqual(self.board.occupants(capture_result.end), [blue])

    def test_safe_positions_prevent_capture(self) -> None:
        red = Token("red", 0)
        blue = Token("blue", 1)

        self.board.enter_board(red)
        self.board.advance_token(red, 7)  # land on safe position 8

        self.board.enter_board(blue)
        result = self.board.advance_token(blue, 20)  # land on same safe index

        occupants = self.board.occupants(8)
        self.assertEqual(len(occupants), 2)
        self.assertIn(red, occupants)
        self.assertIn(blue, occupants)
        self.assertIsNone(result.captured)

    def test_home_lane_is_safe_from_capture(self) -> None:
        red = Token("red", 0)
        blue = Token("blue", 0)

        self.board.enter_board(red)
        self.board.advance_token(red, CONFIG.track_size)

        self.board.enter_board(blue)
        result = self.board.advance_token(blue, CONFIG.track_size)

        occupants = self.board.occupants(100)
        self.assertEqual(len(occupants), 2)
        self.assertIn(red, occupants)
        self.assertIn(blue, occupants)
        self.assertIsNone(result.captured)

    def test_cannot_overrun_total_steps(self) -> None:
        token = Token("red", 0)
        self.board.enter_board(token)

        result = self.board.advance_token(token, CONFIG.total_steps + 1)

        self.assertFalse(result.valid)
        self.assertEqual(token.board_index, CONFIG.start_offsets["red"])
        self.assertEqual(token.steps_taken, 0)

    def test_token_traverses_home_lane_then_finishes(self) -> None:
        token = Token("green", 0)

        self.board.enter_board(token)
        home_entry = self.board.advance_token(token, CONFIG.track_size)
        self.assertEqual(home_entry.end, 100)
        self.assertEqual(token.steps_taken, CONFIG.track_size)

        remaining = CONFIG.total_steps - token.steps_taken
        finish_result = self.board.advance_token(token, remaining)

        self.assertTrue(finish_result.finished)
        self.assertTrue(token.finished)
        self.assertIsNone(token.board_index)


if __name__ == "__main__":
    unittest.main()
