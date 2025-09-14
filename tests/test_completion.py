"""
Quick test to verify game completion works.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ludo_engine import LudoGame


def test_game_completion():
    """Test that games can complete properly."""
    print("Testing game completion...")

    # Create a simple 2-player game
    game = LudoGame(["red", "blue"], ["random", "random"], seed=42)

    print("Playing game until completion...")
    results = game.play_game(max_turns=1000)

    print("Game completed!")
    print(f"Winner: {results['winner']}")
    print(f"Turns: {results['turns_played']}")
    print(f"Total moves: {results['total_moves']}")

    # Show final token positions
    for stats in results["player_stats"]:
        print(f"{stats['color']}: {stats['tokens_finished']} tokens finished")

    return results["winner"] is not None


if __name__ == "__main__":
    success = test_game_completion()
    if success:
        print("✓ Game completion test passed!")
    else:
        print("❌ Game completion test failed!")
    sys.exit(0 if success else 1)
