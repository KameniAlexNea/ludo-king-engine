"""Coverage for the minimalist strategy builders."""

from __future__ import annotations

import unittest

from ludo_engine_simple import CONFIG, Game
from ludo_engine_strategies import build_strategy
from ludo_engine_strategies.strategy import STRATEGY_BUILDERS, available_strategies


def prepare_finishing_context(game: Game) -> tuple[int, list]:
    player = game.players[0]
    token = player.tokens[0]
    game.board.enter_board(token)
    game.board.advance_token(token, CONFIG.travel_distance)
    game.board.advance_token(token, CONFIG.home_run - 1)
    dice_value = 1
    moves = game.available_moves(player, dice_value)
    return dice_value, moves


class StrategyBuilderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.game = Game(seed=2)
        self.dice_value, self.moves = prepare_finishing_context(self.game)

    def _assert_strategy_picks_finishing_move(self, name: str, **kwargs) -> None:
        decision_fn = build_strategy(name, self.game, **kwargs)
        decision = decision_fn(
            self.game.players,
            self.dice_value,
            self.moves,
            self.game.current_player_index,
        )
        self.assertEqual(self.moves[0], decision, msg=f"strategy {name} failed")

    def test_available_strategies_without_special(self) -> None:
        names = available_strategies(include_special=False)
        self.assertNotIn("human", names)
        self.assertNotIn("llm", names)
        self.assertTrue({"random", "killer", "balanced"}.issubset(names))

    def test_every_strategy_handles_simple_move(self) -> None:
        for name in STRATEGY_BUILDERS:
            if name == "human":
                continue  # requires interactive input
            with self.subTest(name=name):
                self._assert_strategy_picks_finishing_move(name)

    def test_llm_strategy_with_responder(self) -> None:
        def responder(_prompt: str) -> str:
            return "choice: 0"

        decision_fn = build_strategy("llm", self.game, responder=responder)
        decision = decision_fn(
            self.game.players,
            self.dice_value,
            self.moves,
            self.game.current_player_index,
        )
        self.assertEqual(self.moves[0], decision)


if __name__ == "__main__":
    unittest.main()
