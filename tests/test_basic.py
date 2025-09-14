"""
Basic tests for the Ludo engine.

This module contains simple tests to verify the core functionality
of the Ludo game engine implementation.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ludo_engine import LudoGame, StrategyFactory
from ludo_engine.core.board import Board
from ludo_engine.core.player import Player
from ludo_engine.core.token import Token


class TestLudoEngine(unittest.TestCase):
    """Test cases for the Ludo engine."""

    def test_token_creation(self):
        """Test basic token functionality."""
        token = Token(0, "red")
        self.assertEqual(token.token_id, 0)
        self.assertEqual(token.color, "red")
        self.assertTrue(token.is_at_home())
        self.assertFalse(token.is_active())
        self.assertFalse(token.is_finished())

    def test_board_creation(self):
        """Test board initialization."""
        board = Board()
        self.assertEqual(board.BOARD_SIZE, 56)
        self.assertEqual(len(board.positions), 57)  # Including finish position
        self.assertIn(1, board.SAFE_POSITIONS)

    def test_player_creation(self):
        """Test player initialization."""
        player = Player("red", "Test Player")
        self.assertEqual(player.color, "red")
        self.assertEqual(player.name, "Test Player")
        self.assertEqual(len(player.tokens), 4)
        self.assertTrue(all(token.color == "red" for token in player.tokens))
        self.assertEqual(len(player.get_tokens_at_home()), 4)

    def test_strategy_factory(self):
        """Test strategy factory."""
        strategies = StrategyFactory.get_available_strategies()
        self.assertGreater(len(strategies), 0)
        self.assertIn("random", strategies)
        self.assertIn("killer", strategies)

        random_strategy = StrategyFactory.create_strategy("random")
        self.assertIsNotNone(random_strategy)
        self.assertEqual(random_strategy.name, "Random")

    def test_game_creation(self):
        """Test game initialization."""
        game = LudoGame(seed=42)  # Use seed for deterministic testing
        self.assertEqual(len(game.players), 4)
        self.assertIsNotNone(game.board)
        self.assertEqual(game.current_player_index, 0)

    def test_game_start(self):
        """Test game start functionality."""
        game = LudoGame(["red", "blue"], ["random", "killer"], seed=42)
        game.start_game()
        self.assertEqual(game.game_state.value, "in_progress")

        # All tokens should be at home initially
        for player in game.players:
            self.assertEqual(len(player.get_tokens_at_home()), 4)

    def test_simple_game(self):
        """Test a simple game simulation."""
        game = LudoGame(["red", "blue"], ["random", "random"], seed=42)

        # Play a few turns
        game.start_game()
        for _ in range(10):
            if game.is_finished():
                break
            turn_result = game.play_turn()
            # Verify turn result structure
            self.assertIn("player", turn_result)
            self.assertIn("dice_roll", turn_result)
            self.assertIn("move_made", turn_result)


if __name__ == "__main__":
    unittest.main()
