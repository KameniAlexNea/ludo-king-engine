"""
Basic tests for the Ludo engine.

This module contains simple tests to verify the core functionality
of the Ludo game engine implementation.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ludo_engine import LudoGame, StrategyFactory
from ludo_engine.core.board import Board
from ludo_engine.core.player import Player
from ludo_engine.core.token import Token


def test_token_creation():
    """Test basic token functionality."""
    print("Testing token creation...")
    token = Token(0, "red")
    assert token.token_id == 0
    assert token.color == "red"
    assert token.is_at_home()
    assert not token.is_active()
    assert not token.is_finished()
    print("✓ Token creation test passed")


def test_board_creation():
    """Test board initialization."""
    print("Testing board creation...")
    board = Board()
    assert board.BOARD_SIZE == 56
    assert len(board.positions) == 57  # Including finish position
    assert 1 in board.SAFE_POSITIONS
    print("✓ Board creation test passed")


def test_player_creation():
    """Test player initialization."""
    print("Testing player creation...")
    player = Player("red", "Test Player")
    assert player.color == "red"
    assert player.name == "Test Player"
    assert len(player.tokens) == 4
    assert all(token.color == "red" for token in player.tokens)
    assert len(player.get_tokens_at_home()) == 4
    print("✓ Player creation test passed")


def test_strategy_factory():
    """Test strategy factory."""
    print("Testing strategy factory...")
    strategies = StrategyFactory.get_available_strategies()
    assert len(strategies) > 0
    assert "random" in strategies
    assert "killer" in strategies

    random_strategy = StrategyFactory.create_strategy("random")
    assert random_strategy is not None
    assert random_strategy.name == "Random"
    print("✓ Strategy factory test passed")


def test_game_creation():
    """Test game initialization."""
    print("Testing game creation...")
    game = LudoGame(seed=42)  # Use seed for deterministic testing
    assert len(game.players) == 4
    assert game.board is not None
    assert game.current_player_index == 0
    print("✓ Game creation test passed")


def test_game_start():
    """Test game start functionality."""
    print("Testing game start...")
    game = LudoGame(["red", "blue"], ["random", "killer"], seed=42)
    game.start_game()
    assert game.game_state.value == "in_progress"

    # All tokens should be at home initially
    for player in game.players:
        assert len(player.get_tokens_at_home()) == 4
    print("✓ Game start test passed")


def test_simple_game():
    """Test a simple game simulation."""
    print("Testing simple game simulation...")
    game = LudoGame(["red", "blue"], ["random", "random"], seed=42)

    # Play a few turns
    game.start_game()
    for _ in range(10):
        if game.is_finished():
            break
        turn_result = game.play_turn()
        print(
            f"  Turn: {game.turn_count}, Player: {turn_result['player']}, "
            f"Dice: {turn_result['dice_roll']}, Move: {turn_result['move_made']}"
        )

    print("✓ Simple game simulation test passed")


def run_all_tests():
    """Run all tests."""
    print("Running Ludo Engine Tests...\n")

    try:
        test_token_creation()
        test_board_creation()
        test_player_creation()
        test_strategy_factory()
        test_game_creation()
        test_game_start()
        test_simple_game()

        print("\n🎉 All tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
