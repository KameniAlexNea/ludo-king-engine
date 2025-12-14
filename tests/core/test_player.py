"""Player behaviour tests for the simplified engine."""

import unittest

from ludo_engine import CONFIG
from ludo_engine.player import Player
from ludo_engine.token import Token


class PlayerTestCase(unittest.TestCase):
    def test_player_initialises_tokens(self) -> None:
        player = Player("red")
        self.assertEqual(len(player.tokens), CONFIG.tokens_per_player)
        self.assertTrue(all(token.color == "red" for token in player.tokens))

    def test_ready_tokens_returns_only_tokens_in_play(self) -> None:
        tokens = [
            Token("green", 0, board_index=5),
            Token("green", 1),
            Token("green", 2, board_index=12, finished=True),
        ]
        player = Player("green", tokens=tokens)
        ready = list(player.ready_tokens())
        self.assertEqual(len(ready), 1)
        self.assertIs(ready[0], tokens[0])

    def test_home_tokens_excludes_finished(self) -> None:
        tokens = [
            Token("blue", 0),
            Token("blue", 1, finished=True),
            Token("blue", 2, board_index=7),
        ]
        player = Player("blue", tokens=tokens)
        home = list(player.home_tokens())
        self.assertEqual(home, [tokens[0]])

    def test_finished_count_and_has_won(self) -> None:
        player = Player("yellow")
        for token in player.tokens:
            token.finished = True
        self.assertEqual(player.finished_count(), CONFIG.tokens_per_player)
        self.assertTrue(player.has_won())


if __name__ == "__main__":
    unittest.main()
