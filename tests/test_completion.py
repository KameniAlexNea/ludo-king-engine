"""
Test to verify game completion works.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ludo_engine import LudoGame


class TestGameCompletion(unittest.TestCase):
    """Test cases for game completion functionality."""

    def test_game_completion(self):
        """Test that games can complete properly."""
        # Create a simple 2-player game
        game = LudoGame(["red", "blue"], ["random", "random"], seed=42)

        results = game.play_game(max_turns=1000)

        # Verify game completed
        self.assertIsNotNone(results["winner"])
        self.assertGreater(results["turns_played"], 0)
        self.assertGreater(results["total_moves"], 0)

        # Verify player stats
        self.assertEqual(len(results["player_stats"]), 2)
        for stats in results["player_stats"]:
            self.assertIn("color", stats)
            self.assertIn("tokens_finished", stats)
            self.assertGreaterEqual(stats["tokens_finished"], 0)


if __name__ == "__main__":
    unittest.main()
