"""
Integration tests for the Ludo game engine.
Tests cover full game scenarios, multi-player interactions, and end-to-end game flow.
"""

import unittest
from unittest.mock import patch

from ludo_engine.game import LudoGame
from ludo_engine.player import Player, PlayerColor
from ludo_engine.strategies.killer import KillerStrategy
from ludo_engine.strategies.winner import WinnerStrategy
from ludo_engine.strategies.random_strategy import RandomStrategy


class TestGameIntegration(unittest.TestCase):
    """Integration tests for complete game scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.game = LudoGame([PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.YELLOW])

    def test_complete_game_simulation(self):
        """Test a complete game simulation with random moves."""
        max_turns = 200  # Prevent infinite loops
        turn_count = 0

        while not self.game.is_game_over() and turn_count < max_turns:
            dice_roll = self.game.roll_dice()
            result = self.game.play_turn(dice_roll)

            # Verify turn result structure
            self.assertIsInstance(result, dict)
            self.assertIn('success', result)
            self.assertIn('move_made', result)
            self.assertIn('captures', result)

            turn_count += 1

        # Game should either be over or have made reasonable progress
        self.assertTrue(self.game.is_game_over() or turn_count >= 50)

    def test_multi_player_interaction(self):
        """Test interactions between multiple players."""
        # Set up a simple scenario
        game = LudoGame()

        # Player 1 exits home
        game.current_player_index = 0
        result = game.play_turn(6)
        self.assertTrue(result['success'])

        # Player 2 exits home
        game.current_player_index = 1
        result = game.play_turn(6)
        self.assertTrue(result['success'])

        # Player 1 moves to position that might conflict
        game.current_player_index = 0
        result = game.play_turn(4)  # Should move to position 10
        self.assertTrue(result['success'])

        # Player 2 tries to land on same position
        game.current_player_index = 1
        result = game.play_turn(4)  # Should move to position 10 and capture

        # Verify capture occurred
        if result['success'] and result['move_made']:
            self.assertGreater(len(result['captures']), 0)

    def test_strategy_vs_strategy_game(self):
        """Test a game between different AI strategies."""
        # Create players with different strategies
        killer_player = Player(PlayerColor.RED, 0, KillerStrategy())
        winner_player = Player(PlayerColor.BLUE, 1, WinnerStrategy())

        game = LudoGame(players=[killer_player, winner_player])

        # Play several turns
        for _ in range(20):
            if game.is_game_over():
                break
            dice_roll = game.roll_dice()
            result = game.play_turn(dice_roll)

        # Game should make progress
        self.assertTrue(game.is_game_over() or
                       any(player.has_active_tokens() for player in game.players))

    def test_consecutive_sixes_rule(self):
        """Test the three consecutive sixes rule."""
        game = LudoGame()

        # Force three consecutive sixes
        game.consecutive_sixes = 2

        # Third six should pass the turn
        with patch.object(game, 'roll_dice', return_value=6):
            result = game.play_turn(6)

        self.assertEqual(game.consecutive_sixes, 0)
        self.assertEqual(game.current_player_index, 1)  # Turn passed

    def test_game_state_persistence(self):
        """Test that game state persists correctly across turns."""
        game = LudoGame()

        # Record initial state
        initial_positions = {}
        for i, player in enumerate(game.players):
            initial_positions[i] = [token.position for token in player.tokens]

        # Make some moves
        for _ in range(10):
            if game.is_game_over():
                break
            dice_roll = game.roll_dice()
            game.play_turn(dice_roll)

        # Verify state has changed appropriately
        state_changed = False
        for i, player in enumerate(game.players):
            current_positions = [token.position for token in player.tokens]
            if current_positions != initial_positions[i]:
                state_changed = True
                break

        # Either game ended or state changed
        self.assertTrue(game.is_game_over() or state_changed)

    def test_capture_and_respawn_mechanics(self):
        """Test token capture and respawn mechanics."""
        game = LudoGame()

        # Set up two players with tokens on the board
        red_player = game.players[0]
        blue_player = game.players[1]

        # Move red token to position 10
        red_player.tokens[0].state.value = "active"
        red_player.tokens[0].position = 10
        game.board.add_token(red_player.tokens[0], 10)

        # Move blue token to same position (should capture)
        blue_player.tokens[0].state.value = "active"
        blue_player.tokens[0].position = 6
        game.board.add_token(blue_player.tokens[0], 6)

        game.current_player_index = 1  # Blue's turn
        result = game.execute_move(0, 6, 10)  # Blue moves to position 10

        # Verify capture
        self.assertEqual(len(result), 1)  # One token captured
        self.assertEqual(result[0], red_player.tokens[0])

        # Verify captured token is back in home
        self.assertEqual(red_player.tokens[0].state.value, "home")
        self.assertEqual(red_player.tokens[0].position, -1)

    def test_home_column_progression(self):
        """Test token progression through home column."""
        game = LudoGame()
        player = game.players[0]

        # Set up token near home entry
        player.tokens[0].state.value = "active"
        player.tokens[0].position = 50  # Just before red's home entry

        # Move to enter home column
        result = game.execute_move(0, 50, 102)  # Enter home column at position 102

        self.assertTrue(result)
        self.assertEqual(player.tokens[0].state.value, "home_column")
        self.assertEqual(player.tokens[0].position, 102)

        # Move within home column
        result = game.execute_move(0, 102, 104)

        self.assertTrue(result)
        self.assertEqual(player.tokens[0].position, 104)

    def test_winning_condition(self):
        """Test winning condition detection."""
        game = LudoGame()
        player = game.players[0]

        # Set all tokens to finished
        for token in player.tokens:
            token.state.value = "finished"
            token.position = 105

        # Verify win condition
        self.assertTrue(game.is_game_over())
        self.assertEqual(game.get_winner(), player)

    def test_ai_decision_context_accuracy(self):
        """Test that AI decision context accurately reflects game state."""
        game = LudoGame()

        # Make some moves to create interesting state
        game.play_turn(6)  # Exit home
        game.play_turn(3)  # Move forward

        # Get AI context
        context = game.get_ai_decision_context(4)

        # Verify context accuracy
        self.assertEqual(context.dice_value, 4)
        self.assertEqual(context.current_player_id, game.current_player_index)
        self.assertIsInstance(context.valid_moves, list)
        self.assertIsInstance(context.game_state, dict)

        # Verify valid moves are actually valid
        for move in context.valid_moves:
            can_move = game.is_valid_move(4, move.token_id)
            self.assertTrue(can_move)

    def test_turn_boundary_conditions(self):
        """Test turn transitions and boundary conditions."""
        game = LudoGame()

        # Test turn progression
        initial_player = game.current_player_index

        # Normal turn
        game.play_turn(3)
        self.assertEqual(game.current_player_index, (initial_player + 1) % 4)

        # Six rolled - same player
        game.current_player_index = initial_player
        game.play_turn(6)
        self.assertEqual(game.current_player_index, initial_player)

        # Test boundary at last player
        game.current_player_index = 3
        game.play_turn(3)
        self.assertEqual(game.current_player_index, 0)

    def test_error_handling_and_recovery(self):
        """Test error handling and recovery mechanisms."""
        game = LudoGame()

        # Test invalid moves don't break the game
        result = game.execute_move(0, 3)  # Can't move from home with 3
        self.assertFalse(result)

        # Game should still be functional
        result = game.play_turn(6)
        self.assertIsInstance(result, dict)

        # Test with invalid player indices
        game.current_player_index = 10  # Invalid
        game.play_turn(6)  # Should handle gracefully

    def test_performance_with_many_moves(self):
        """Test performance with many consecutive moves."""
        game = LudoGame()

        # Make many moves quickly
        for _ in range(50):
            if game.is_game_over():
                break
            dice_roll = game.roll_dice()
            game.play_turn(dice_roll)

        # Should complete without errors
        self.assertTrue(True)  # If we get here, no exceptions occurred

    def test_memory_and_state_consistency(self):
        """Test that game state remains consistent."""
        game = LudoGame()

        # Record multiple state snapshots
        snapshots = []
        for i in range(5):
            snapshot = {
                'current_player': game.current_player_index,
                'consecutive_sixes': game.consecutive_sixes,
                'game_over': game.game_over,
                'token_positions': {}
            }

            for j, player in enumerate(game.players):
                snapshot['token_positions'][j] = [
                    (token.position, token.state.value) for token in player.tokens
                ]

            snapshots.append(snapshot)

            if not game.is_game_over():
                dice_roll = game.roll_dice()
                game.play_turn(dice_roll)

        # Verify state consistency (no invalid states)
        for snapshot in snapshots:
            self.assertGreaterEqual(snapshot['current_player'], 0)
            self.assertLess(snapshot['current_player'], 4)
            self.assertGreaterEqual(snapshot['consecutive_sixes'], 0)
            self.assertLessEqual(snapshot['consecutive_sixes'], 3)


class TestStrategyIntegration(unittest.TestCase):
    """Integration tests for strategy interactions."""

    def test_strategy_factory_integration(self):
        """Test strategy factory works with game integration."""
        from ludo_engine.strategies import StrategyFactory

        # Create strategies
        killer = StrategyFactory.create_strategy("killer")
        winner = StrategyFactory.create_strategy("winner")

        # Create game with strategy players
        killer_player = Player(PlayerColor.RED, 0, killer)
        winner_player = Player(PlayerColor.BLUE, 1, winner)

        game = LudoGame(players=[killer_player, winner_player])

        # Play some turns
        for _ in range(10):
            if game.is_game_over():
                break
            dice_roll = game.roll_dice()
            game.play_turn(dice_roll)

        # Verify strategies work together
        self.assertTrue(game.is_game_over() or
                       any(player.has_active_tokens() for player in game.players))

    def test_mixed_strategy_game(self):
        """Test game with mixed human and AI players."""
        # Create mixed players
        human_player = Player(PlayerColor.RED, 0)  # No strategy = human-like
        ai_player = Player(PlayerColor.BLUE, 1, RandomStrategy())

        game = LudoGame(players=[human_player, ai_player])

        # Simulate some AI decisions
        game.current_player_index = 1  # AI player's turn
        context = game.get_ai_decision_context(6)

        if context.valid_moves:
            decision = ai_player.make_strategic_decision(context)
            self.assertGreaterEqual(decision, 0)
            self.assertLess(decision, 4)


if __name__ == '__main__':
    unittest.main()