"""Baseline random strategies behaviour tests."""

from __future__ import annotations

import unittest

from ludo_engine import CONFIG, Game
from ludo_engine_strategies.baseline import build_random, build_weighted


def prepare_finishing_move(game: Game) -> tuple[int, list]:
    player = game.players[0]
    token = player.tokens[0]
    game.board.enter_board(token)
    game.board.advance_token(token, CONFIG.travel_distance)
    game.board.advance_token(token, CONFIG.home_run - 1)
    dice_value = 1
    moves = game.available_moves(player, dice_value)
    return dice_value, moves


class RandomBaselineStrategyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.game = Game(seed=1)

    def test_random_strategy_returns_only_move(self) -> None:
        dice_value, moves = prepare_finishing_move(self.game)
        strategy = build_random(self.game, seed=123)
        decision = strategy(
            self.game.players,
            dice_value,
            moves,
            self.game.current_player_index,
        )
        self.assertEqual(moves, [decision])

    def test_weighted_random_returns_only_move(self) -> None:
        dice_value, moves = prepare_finishing_move(self.game)
        strategy = build_weighted(
            self.game,
            temperature=2.0,
            epsilon=0.0,
            seed=5,
        )
        decision = strategy(
            self.game.players,
            dice_value,
            moves,
            self.game.current_player_index,
        )
        self.assertEqual(moves, [decision])


if __name__ == "__main__":
    unittest.main()
