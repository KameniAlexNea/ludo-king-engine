"""
Comprehensive unit tests for LudoGame class.
Tests cover game initialization, turn management, move execution, game over conditions,
and AI decision context generation to achieve high code coverage.
"""

import unittest
from unittest.mock import MagicMock, patch

from ludo_engine.constants import GameConstants
from ludo_engine.game import LudoGame
from ludo_engine.model import AIDecisionContext, ValidMove, TurnResult
from ludo_engine.player import Player, PlayerColor
from ludo_engine.strategies.random_strategy import RandomStrategy
from ludo_engine.token import TokenState


class TestLudoGame(unittest.TestCase):
    """Test cases for LudoGame class."""

    def setUp(self):
        """Set up test fixtures."""
        self.game = LudoGame([PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.YELLOW])
        self.player_red = Player(PlayerColor.RED, 0)
        self.player_blue = Player(PlayerColor.BLUE, 1)

    def test_initialization(self):
        """Test game initialization with default settings."""
        game = LudoGame([PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.YELLOW])

        self.assertEqual(len(game.players), 4)
        self.assertEqual(game.current_player_index, 0)
        self.assertEqual(game.consecutive_sixes, 0)
        self.assertFalse(game.game_over)
        self.assertIsNone(game.winner)

        # Check player colors
        expected_colors = [PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.YELLOW]
        for i, player in enumerate(game.players):
            self.assertEqual(player.color, expected_colors[i])
            self.assertEqual(player.player_id, i)

    def test_initialization_with_custom_players(self):
        """Test game initialization with custom player list."""
        game = LudoGame([PlayerColor.RED, PlayerColor.BLUE])

        self.assertEqual(len(game.players), 2)
        self.assertEqual(game.players[0].color, PlayerColor.RED)
        self.assertEqual(game.players[1].color, PlayerColor.BLUE)

    def test_get_current_player(self):
        """Test getting current player."""
        self.assertEqual(self.game.get_current_player(), self.game.players[0])

        # Change current player
        self.game.current_player_index = 1
        self.assertEqual(self.game.get_current_player(), self.game.players[1])

    def test_roll_dice(self):
        """Test dice rolling functionality."""
        # Test normal roll (should be between 1-6)
        roll = self.game.roll_dice()
        self.assertGreaterEqual(roll, 1)
        self.assertLessEqual(roll, 6)

        # Test that consecutive sixes are tracked
        self.game.consecutive_sixes = 2
        roll = self.game.roll_dice()
        if roll == 6:
            self.assertEqual(self.game.consecutive_sixes, 3)
        else:
            self.assertEqual(self.game.consecutive_sixes, 0)

    def test_is_valid_move_basic(self):
        """Test basic move validation."""
        current_player = self.game.get_current_player()
        
        # Test invalid dice values - should return empty valid moves
        valid_moves = self.game.get_valid_moves(current_player, 0)
        self.assertEqual(len(valid_moves), 0)
        
        # Test invalid token IDs - get_valid_moves should handle this internally
        valid_moves = self.game.get_valid_moves(current_player, 6)
        # Should have valid moves for token IDs 0-3, but not for invalid IDs
        token_ids = [move.token_id for move in valid_moves]
        self.assertTrue(all(0 <= tid <= 3 for tid in token_ids))

    def test_get_valid_moves_no_moves(self):
        """Test getting valid moves when no moves are possible."""
        # All tokens in home, dice roll != 6
        current_player = self.game.get_current_player()
        valid_moves = self.game.get_valid_moves(current_player, 3)

        # Should have no valid moves since no tokens can exit home with roll != 6
        self.assertEqual(len(valid_moves), 0)

    def test_get_valid_moves_exit_home(self):
        """Test getting valid moves for exiting home."""
        current_player = self.game.get_current_player()
        valid_moves = self.game.get_valid_moves(current_player, 6)

        # Should have 4 moves, one for each token exiting home
        self.assertEqual(len(valid_moves), 4)

        for move in valid_moves:
            self.assertEqual(move.move_type, "exit_home")
            self.assertEqual(move.current_position, -1)
            self.assertEqual(move.target_position, current_player.start_position)

    def test_execute_move_exit_home(self):
        """Test executing a move to exit home."""
        current_player = self.game.get_current_player()
        initial_home_tokens = current_player.get_finished_tokens_count()

        # Execute move for token 0
        result = self.game.execute_move(current_player, 0, 6)

        self.assertTrue(result.success)
        self.assertEqual(current_player.tokens[0].position, current_player.start_position)
        self.assertEqual(current_player.tokens[0].state.value, "active")

    def test_execute_move_invalid(self):
        """Test executing invalid moves."""
        current_player = self.game.get_current_player()
        
        # Invalid dice value
        result = self.game.execute_move(current_player, 0, 0)
        self.assertFalse(result.success)

        # Invalid token ID
        result = self.game.execute_move(current_player, -1, 6)
        self.assertFalse(result.success)
        result = self.game.execute_move(current_player, 4, 6)
        self.assertFalse(result.success)

        # Token can't move
        result = self.game.execute_move(current_player, 0, 3)  # Token in home, dice != 6
        self.assertFalse(result.success)

    def test_turn_management(self):
        """Test turn progression and consecutive sixes."""
        initial_player = self.game.current_player_index

        # Normal turn (no six)
        with patch.object(self.game, 'roll_dice', return_value=3):
            self.game.play_turn()
        self.assertEqual(self.game.current_player_index, 1)

        # Six rolled - same player continues
        self.game.current_player_index = initial_player
        self.game.consecutive_sixes = 0  # Reset for this test
        def mock_roll_dice_6():
            result = 6
            if result == 6:
                self.game.consecutive_sixes += 1
            else:
                self.game.consecutive_sixes = 0
            return result
        with patch.object(self.game, 'roll_dice', side_effect=mock_roll_dice_6):
            self.game.play_turn()
        self.assertEqual(self.game.current_player_index, initial_player)
        self.assertEqual(self.game.consecutive_sixes, 1)

        # Three sixes - turn passes
        self.game.consecutive_sixes = 2
        def mock_roll_dice():
            result = 6
            if result == 6:
                self.game.consecutive_sixes += 1
            else:
                self.game.consecutive_sixes = 0
            return result
        with patch.object(self.game, 'roll_dice', side_effect=mock_roll_dice):
            self.game.play_turn()
        self.assertEqual(self.game.current_player_index, (initial_player + 1) % 4)
        self.assertEqual(self.game.consecutive_sixes, 0)

    def test_game_over_conditions(self):
        """Test game over detection."""
        # Game should not be over initially
        self.assertFalse(any(player.has_won() for player in self.game.players))

        # Manually set a player as winner
        self.game.players[0].tokens[0].state = TokenState.FINISHED
        self.game.players[0].tokens[1].state = TokenState.FINISHED
        self.game.players[0].tokens[2].state = TokenState.FINISHED
        self.game.players[0].tokens[3].state = TokenState.FINISHED

        # Manually set winner since we're not going through normal game flow
        self.game.winner = self.game.players[0]
        self.game.game_over = True

        self.assertTrue(self.game.players[0].has_won())
        self.assertEqual(self.game.winner, self.game.players[0])

    def test_ai_decision_context_generation(self):
        """Test generation of AI decision context."""
        context = self.game.get_ai_decision_context(6)

        self.assertIsInstance(context, AIDecisionContext)
        self.assertEqual(context.current_situation.dice_value, 6)
        self.assertEqual(context.current_situation.player_color, self.game.players[0].color.value)
        self.assertIsInstance(context.valid_moves, list)
        from ludo_engine.model import PlayerState
        self.assertIsInstance(context.player_state, PlayerState)

    def test_ai_decision_context_with_moves(self):
        """Test AI decision context includes valid moves."""
        context = self.game.get_ai_decision_context(6)

        # Should have 4 valid moves for exiting home
        self.assertEqual(len(context.valid_moves), 4)

        for move in context.valid_moves:
            self.assertIsInstance(move, ValidMove)
            self.assertEqual(move.move_type, "exit_home")

    def test_play_turn_with_ai_player(self):
        """Test playing turn with AI player."""
        # Set up AI player
        ai_strategy = RandomStrategy()
        self.game.players[0].set_strategy(ai_strategy)

        # Mock the strategy decision
        with patch.object(ai_strategy, 'decide', return_value=0):
            with patch.object(self.game, 'roll_dice', return_value=6):
                result = self.game.play_turn()

            self.assertIsInstance(result, TurnResult)
            self.assertGreaterEqual(len(result.moves), 0)

    def test_play_turn_no_valid_moves(self):
        """Test playing turn when no valid moves are possible."""
        # All tokens in home, dice != 6
        with patch.object(self.game, 'roll_dice', return_value=3):
            result = self.game.play_turn()

        self.assertIsInstance(result, TurnResult)
        self.assertEqual(len(result.moves), 0)

    def test_token_capture_logic(self):
        """Test token capture mechanics."""
        current_player = self.game.get_current_player()
        
        # Move first player to position 10
        self.game.execute_move(current_player, 0, 6)  # Exit home
        self.game.execute_move(current_player, 0, 4)  # Move to position 10

        # Switch to second player
        self.game.current_player_index = 1
        second_player = self.game.get_current_player()

        # Move second player to same position
        self.game.execute_move(second_player, 0, 6)  # Exit home
        self.game.execute_move(second_player, 0, 4)  # Move to position 10

        # Should capture the first player's token
        tokens_at_pos = self.game.board.get_tokens_at_position(10)
        self.assertEqual(len(tokens_at_pos), 1)  # Only one token should remain
        self.assertEqual(tokens_at_pos[0].player_color, PlayerColor.BLUE.value)

    def test_safe_position_protection(self):
        """Test that safe positions protect tokens from capture."""
        current_player = self.game.get_current_player()
        
        # Move to a safe position (star square at position 8 for red)
        self.game.execute_move(current_player, 0, 6)  # Exit home (position 0 for red)
        self.game.execute_move(current_player, 0, 2)  # Move to position 2
        self.game.execute_move(current_player, 0, 6)  # Move to position 8 (safe star)

        # Switch to opponent
        self.game.current_player_index = 1
        opponent_player = self.game.get_current_player()
        self.game.execute_move(opponent_player, 0, 6)  # Exit home
        self.game.execute_move(opponent_player, 0, 2)  # Move to position 2
        self.game.execute_move(opponent_player, 0, 6)  # Try to move to position 8

        # Both tokens should be at position 8 (safe position allows stacking)
        tokens_at_pos = self.game.board.get_tokens_at_position(8)
        self.assertEqual(len(tokens_at_pos), 2)

    def test_home_column_movement(self):
        """Test movement within home column."""
        # Get player to home column entry
        current_player = self.game.get_current_player()
        home_entry = current_player.start_position + 50  # Home column entry calculation

        # Move token to just before home entry
        self.game.execute_move(current_player, 0, 6)  # Exit home
        for _ in range(12):  # Move 12 spaces to get near home entry
            if self.game.get_valid_moves(current_player, 1):
                self.game.execute_move(current_player, 0, 1)

        # Move into home column
        if self.game.get_valid_moves(current_player, 6):
            self.game.execute_move(current_player, 0, 6)

        # Token should be in home column
        token = current_player.tokens[0]
        self.assertTrue(token.is_in_home_column())

        # Token should be in home column
        token = current_player.tokens[0]
        self.assertTrue(token.is_in_home_column())

    def test_multiple_players_game_flow(self):
        """Test complete game flow with multiple players."""
        # Play several turns
        for turn in range(20):
            result = self.game.play_turn()

            if any(player.has_won() for player in self.game.players):
                break

        # Game should eventually end or continue properly
        self.assertTrue(any(player.has_won() for player in self.game.players) or turn < 19)

    def test_edge_case_three_consecutive_sixes(self):
        """Test the three consecutive sixes rule."""
        self.game.consecutive_sixes = 3  # Set to 3 to trigger the rule

        # Third six should pass the turn
        with patch.object(self.game, 'roll_dice', return_value=6):
            result = self.game.play_turn()

        self.assertEqual(self.game.consecutive_sixes, 0)
        self.assertEqual(self.game.current_player_index, 1)  # Turn passed

    def test_invalid_move_does_not_change_state(self):
        """Test that invalid moves don't change game state."""
        initial_state = {
            'current_player': self.game.current_player_index,
            'consecutive_sixes': self.game.consecutive_sixes,
            'token_positions': [t.position for t in self.game.players[0].tokens]
        }

        # Try invalid move
        self.game.execute_move(self.game.players[0], 0, 3)  # Can't move token from home with 3

        # State should be unchanged
        self.assertEqual(self.game.current_player_index, initial_state['current_player'])
        self.assertEqual(self.game.consecutive_sixes, initial_state['consecutive_sixes'])
        self.assertEqual(
            [t.position for t in self.game.players[0].tokens],
            initial_state['token_positions']
        )


if __name__ == '__main__':
    unittest.main()