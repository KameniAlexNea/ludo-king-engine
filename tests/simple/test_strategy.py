"""Tests for the simplified strategic value computer."""

import unittest

from ludo_engine_simple.game import Game
from ludo_engine_simple.strategy import StrategicEvaluation, StrategicValueComputer


def choose_last(players, dice_value, moves, current_index):
    _ = players, dice_value, current_index
    return moves[-1] if moves else None


class StrategicValueComputerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.game = Game(seed=2)
        self.computer = StrategicValueComputer(self.game)

    def test_evaluate_returns_recommendation(self) -> None:
        snapshot = self.computer.evaluate(6, decision_fn=choose_last)
        self.assertIsInstance(snapshot, StrategicEvaluation)
        self.assertEqual(snapshot.dice_value, 6)
        self.assertEqual(snapshot.current_index, self.game.current_player_index)
        self.assertTrue(snapshot.players[snapshot.current_index].moves)
        if snapshot.recommended is not None:
            self.assertEqual(
                snapshot.recommended.decision,
                snapshot.players[snapshot.current_index].moves[-1].decision,
            )

    def test_capture_move_flagged(self) -> None:
        board = self.game.board
        red_player = self.game.players[0]
        opponent = self.game.players[1]

        red_token = red_player.tokens[0]
        board.enter_board(red_token)

        enemy_token = opponent.tokens[0]
        enemy_token.board_index = 5
        enemy_token.steps_taken = 40  # arbitrary but consistent
        enemy_token.finished = False
        board._positions[5] = [enemy_token]

        snapshot = self.computer.evaluate(4)
        move_lookup = {move.decision: move for move in snapshot.players[0].moves}
        capture_move = move_lookup.get(("advance", red_token.index))
        self.assertIsNotNone(capture_move)
        self.assertTrue(capture_move.will_capture)
        self.assertGreater(capture_move.score, 0.0)

    def test_opponents_include_moves(self) -> None:
        board = self.game.board
        current = self.game.players[0]
        opponent = self.game.players[1]

        board.enter_board(current.tokens[0])
        board.enter_board(opponent.tokens[0])

        snapshot = self.computer.evaluate(3)
        opponent_view = next(
            (view for view in snapshot.players if view.index == 1), None
        )
        self.assertIsNotNone(opponent_view)
        self.assertTrue(opponent_view.moves)
        self.assertEqual(len(snapshot.players), len(self.game.players))


if __name__ == "__main__":
    unittest.main()
