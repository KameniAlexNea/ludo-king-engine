"""Token behaviour tests for the simplified engine."""

import unittest

from ludo_engine.token import Token


class TokenTestCase(unittest.TestCase):
    def test_initial_state(self) -> None:
        token = Token("red", 1)
        self.assertEqual(token.color, "red")
        self.assertEqual(token.index, 1)
        self.assertIsNone(token.board_index)
        self.assertEqual(token.steps_taken, 0)
        self.assertFalse(token.finished)

    def test_send_home_resets_token(self) -> None:
        token = Token("green", 0, board_index=12, steps_taken=5)
        token.send_home()
        self.assertIsNone(token.board_index)
        self.assertEqual(token.steps_taken, 0)
        self.assertFalse(token.finished)

    def test_mark_finished_sets_flags(self) -> None:
        token = Token("blue", 2, board_index=40, steps_taken=52)
        token.mark_finished()
        self.assertTrue(token.finished)
        self.assertIsNone(token.board_index)

    def test_advance_requires_in_play(self) -> None:
        token = Token("yellow", 0)
        with self.assertRaises(ValueError):
            token.advance(3, 52)

    def test_advance_updates_board_index_and_steps(self) -> None:
        token = Token("yellow", 0, board_index=5, steps_taken=2)
        new_position = token.advance(4, 52)
        self.assertEqual(new_position, 9)
        self.assertEqual(token.board_index, 9)
        self.assertEqual(token.steps_taken, 6)


if __name__ == "__main__":
    unittest.main()
