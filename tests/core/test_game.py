"""Game loop tests for the simplified engine."""

import unittest

from ludo_engine import CONFIG, Game


def choose_first_move(players, _dice, moves, current_index):
    _ = players, current_index
    return moves[0] if moves else None


class GameTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.game = Game(seed=1)
        self.game.strategies = {color: choose_first_move for color in CONFIG.colors}

    def test_play_turn_uses_strategy_choice(self) -> None:
        calls = []

        def choose_last(players, dice_value, moves, current_index):
            player = players[current_index]
            calls.append((player.color, dice_value, len(moves)))
            return moves[-1]

        self.game.strategies["red"] = choose_last

        result = self.game.play_turn(6)

        self.assertTrue(result.valid)
        self.assertEqual(calls, [("red", 6, CONFIG.tokens_per_player)])
        red_player = self.game.players[0]
        for token in red_player.tokens[:-1]:
            self.assertIsNone(token.board_index)
        self.assertEqual(
            red_player.tokens[-1].board_index,
            CONFIG.start_offsets["red"],
        )

    def test_extra_turn_awarded_on_six(self) -> None:
        result = self.game.play_turn(6)
        self.assertTrue(result.valid)
        self.assertEqual(self.game.current_player_index, 0)

    def test_extra_turn_awarded_on_capture(self) -> None:
        red_token = self.game.players[0].tokens[0]
        self.game.board.enter_board(red_token)
        self.game.board.advance_token(red_token, 4)

        blue_token = self.game.players[3].tokens[0]
        self.game.board.enter_board(blue_token)

        self.game.current_player_index = 3
        result = self.game.play_turn(17)

        self.assertIs(result.captured, red_token)
        self.assertIsNone(red_token.board_index)
        self.assertEqual(self.game.current_player_index, 3)

    def test_extra_turn_awarded_on_finish(self) -> None:
        token = self.game.players[0].tokens[0]
        self.game.board.enter_board(token)
        self.game.board.advance_token(token, CONFIG.travel_distance)
        self.game.board.advance_token(token, CONFIG.home_run - 1)

        self.game.current_player_index = 0
        result = self.game.play_turn(1)

        self.assertTrue(result.finished)
        self.assertTrue(token.finished)
        self.assertEqual(self.game.current_player_index, 0)

    def test_no_moves_advances_turn(self) -> None:
        result = self.game.play_turn(3)
        self.assertFalse(result.valid)
        self.assertEqual(self.game.current_player_index, 1)

    def test_winner_detected_when_all_tokens_finished(self) -> None:
        player = self.game.players[0]
        for token in player.tokens:
            token.finished = True
            token.board_index = None
        self.assertIs(self.game.recalculate_winner(), player)
        self.assertIs(self.game.winner(), player)


if __name__ == "__main__":
    unittest.main()
