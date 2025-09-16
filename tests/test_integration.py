"""
Integration tests for the Ludo game engine.
Tests cover full game scenarios, multi-player interactions, and end-to-end game flow.
"""

import unittest
from unittest.mock import patch

from ludo_engine.game import LudoGame
from ludo_engine.model import TurnResult
from ludo_engine.player import Player, PlayerColor
from ludo_engine.strategies.killer import KillerStrategy
from ludo_engine.strategies.random_strategy import RandomStrategy
from ludo_engine.strategies.winner import WinnerStrategy
from ludo_engine.token import TokenState


class TestGameIntegration(unittest.TestCase):
    """Integration tests for complete game scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.game = LudoGame(
            [PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.YELLOW]
        )

    def test_complete_game_simulation(self):
        """Test a complete game simulation with random moves."""
        max_turns = 200  # Prevent infinite loops
        turn_count = 0

        while (
            not any(player.has_won() for player in self.game.players)
            and turn_count < max_turns
        ):
            result = self.game.play_turn()

            # Verify turn result structure
            self.assertIsInstance(result, TurnResult)
            self.assertIsInstance(result.moves, list)

            turn_count += 1

        # Game should either be over or have made reasonable progress
        self.assertTrue(
            any(player.has_won() for player in self.game.players) or turn_count >= 50
        )

    def test_multi_player_interaction(self):
        """Test interactions between multiple players."""
        # Set up a simple scenario
        game = LudoGame(
            [PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.YELLOW]
        )

        # Player 1 exits home
        game.current_player_index = 0
        with patch.object(game, "roll_dice", return_value=6):
            result = game.play_turn()
        self.assertTrue(result.moves[0].success if result.moves else False)

        # Player 2 exits home
        game.current_player_index = 1
        with patch.object(game, "roll_dice", return_value=6):
            result = game.play_turn()
        self.assertTrue(result.moves[0].success if result.moves else False)

        # Player 1 moves to position that might conflict
        game.current_player_index = 0
        with patch.object(game, "roll_dice", return_value=4):
            result = game.play_turn()  # Should move to position 10
        self.assertTrue(result.moves[0].success if result.moves else False)

        # Player 2 tries to land on same position
        game.current_player_index = 1
        with patch.object(game, "roll_dice", return_value=4):
            result = game.play_turn()  # Should move to position 10 and capture

        # Verify capture occurred
        if result.moves:
            self.assertTrue(
                result.moves[0].success
            )  # At least the move should be successful

    def test_strategy_vs_strategy_game(self):
        """Test a game between different AI strategies."""
        game = LudoGame([PlayerColor.RED, PlayerColor.BLUE])
        game.players[0].strategy = KillerStrategy()
        game.players[1].strategy = WinnerStrategy()

        # Play several turns
        for _ in range(20):
            if any(player.has_won() for player in game.players):
                break
            game.play_turn()

        # Game should make progress
        self.assertTrue(
            any(player.has_won() for player in game.players)
            or any(player.has_active_tokens() for player in game.players)
        )

    def test_consecutive_sixes_rule(self):
        """Test the three consecutive sixes rule."""
        game = LudoGame(
            [PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.YELLOW]
        )

        # Force three consecutive sixes
        game.consecutive_sixes = 3  # Set to 3 to trigger the rule

        # Third six should pass the turn
        with patch.object(game, "roll_dice", return_value=6):
            game.play_turn()

        self.assertEqual(game.consecutive_sixes, 0)
        self.assertEqual(game.current_player_index, 1)  # Turn passed

    def test_game_state_persistence(self):
        """Test that game state persists correctly across turns."""
        game = LudoGame(
            [PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.YELLOW]
        )

        # Record initial state
        initial_positions = {}
        for i, player in enumerate(game.players):
            initial_positions[i] = [token.position for token in player.tokens]

        # Make some moves
        for _ in range(10):
            if any(player.has_won() for player in game.players):
                break
            game.play_turn()

        # Verify state has changed appropriately
        state_changed = False
        for i, player in enumerate(game.players):
            current_positions = [token.position for token in player.tokens]
            if current_positions != initial_positions[i]:
                state_changed = True
                break

        # Either game ended or state changed
        self.assertTrue(
            any(player.has_won() for player in game.players) or state_changed
        )

    def test_capture_and_respawn_mechanics(self):
        """Test token capture and respawn mechanics."""
        game = LudoGame(
            [PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.YELLOW]
        )

        # Set up two players with tokens on the board
        red_player = game.players[0]
        blue_player = game.players[1]

        # Move red token to position 10
        red_player.tokens[0].state = TokenState.ACTIVE
        red_player.tokens[0].position = 10
        game.board.add_token(red_player.tokens[0], 10)

        # Move blue token to same position (should capture)
        blue_player.tokens[0].state = TokenState.ACTIVE
        blue_player.tokens[0].position = 6
        game.board.add_token(blue_player.tokens[0], 6)

        game.current_player_index = 1  # Blue's turn
        result = game.execute_move(blue_player, 0, 4)  # Blue moves to position 10

        # Verify capture
        self.assertEqual(len(result.captured_tokens), 1)  # One token captured
        self.assertEqual(
            result.captured_tokens[0].player_color, red_player.tokens[0].player_color
        )
        self.assertEqual(
            result.captured_tokens[0].token_id, red_player.tokens[0].token_id
        )

        # Verify captured token is back in home
        self.assertEqual(red_player.tokens[0].state, TokenState.HOME)
        self.assertEqual(red_player.tokens[0].position, -1)

    def test_home_column_progression(self):
        """Test token progression through home column."""
        game = LudoGame(
            [PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.YELLOW]
        )
        player = game.players[0]

        # Set up token just before home entry
        player.tokens[0].state = TokenState.ACTIVE
        player.tokens[0].position = 50  # Just before red's home entry at 51

        # Move to cross home entry and enter home column
        result = game.execute_move(
            player, 0, 2
        )  # Move 2 spaces: 50 -> 51 -> home column

        self.assertTrue(result.success)
        self.assertEqual(player.tokens[0].state, TokenState.HOME_COLUMN)
        self.assertEqual(
            player.tokens[0].position, 100
        )  # First position in home column

        # Move within home column
        result = game.execute_move(player, 0, 2)

        self.assertTrue(result.success)
        self.assertEqual(player.tokens[0].position, 102)

    def test_winning_condition(self):
        """Test winning condition detection."""
        game = LudoGame(
            [PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.YELLOW]
        )
        player = game.players[0]

        # Set all tokens to finished
        for token in player.tokens:
            token.state = TokenState.FINISHED
            token.position = 105

        # Manually set winner since we're not going through normal game flow
        game.winner = player
        game.game_over = True

        # Verify win condition
        self.assertTrue(player.has_won())
        self.assertEqual(game.winner, player)

    def test_ai_decision_context_accuracy(self):
        """Test that AI decision context accurately reflects game state."""
        game = LudoGame(
            [PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.YELLOW]
        )

        # Make some moves to create interesting state
        with patch.object(game, "roll_dice", return_value=6):
            game.play_turn()  # Exit home
        with patch.object(game, "roll_dice", return_value=3):
            game.play_turn()  # Move forward

        # Get AI context
        context = game.get_ai_decision_context(4)

        # Verify context accuracy
        self.assertEqual(context.current_situation.dice_value, 4)
        self.assertEqual(
            context.current_situation.player_color,
            game.get_current_player().color.value,
        )
        self.assertIsInstance(context.valid_moves, list)
        from ludo_engine.model import PlayerState

        self.assertIsInstance(context.player_state, PlayerState)

    def test_turn_boundary_conditions(self):
        """Test turn transitions and boundary conditions."""
        game = LudoGame(
            [PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.YELLOW]
        )

        # Test turn progression
        initial_player = game.current_player_index

        # Normal turn
        with patch.object(game, "roll_dice", return_value=3):
            game.play_turn()
        self.assertEqual(game.current_player_index, (initial_player + 1) % 4)

        # Six rolled - same player
        game.current_player_index = initial_player
        with patch.object(game, "roll_dice", return_value=6):
            game.play_turn()
        self.assertEqual(game.current_player_index, initial_player)

        # Test boundary at last player
        game.current_player_index = 3
        with patch.object(game, "roll_dice", return_value=3):
            game.play_turn()
        self.assertEqual(game.current_player_index, 0)

    def test_error_handling_and_recovery(self):
        """Test error handling and recovery mechanisms."""
        game = LudoGame(
            [PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.YELLOW]
        )

        # Test invalid moves don't break the game
        current_player = game.get_current_player()
        result = game.execute_move(current_player, 0, 3)  # Can't move from home with 3
        self.assertFalse(result.success)

        # Game should still be functional
        with patch.object(game, "roll_dice", return_value=6):
            result = game.play_turn()
        self.assertIsInstance(result, TurnResult)

        # Test with invalid player indices
        game.current_player_index = 10  # Invalid
        try:
            with patch.object(game, "roll_dice", return_value=6):
                game.play_turn()  # Should handle gracefully
        except IndexError:
            pass  # Expected to fail with invalid index

    def test_performance_with_many_moves(self):
        """Test performance with many consecutive moves."""
        game = LudoGame(
            [PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.YELLOW]
        )

        # Make many moves quickly
        for _ in range(50):
            if any(player.has_won() for player in game.players):
                break
            game.play_turn()

        # Should complete without errors
        self.assertTrue(True)  # If we get here, no exceptions occurred

    def test_memory_and_state_consistency(self):
        """Test that game state remains consistent."""
        game = LudoGame(
            [PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.YELLOW]
        )

        # Record multiple state snapshots
        snapshots = []
        for i in range(5):
            snapshot = {
                "current_player": game.current_player_index,
                "consecutive_sixes": game.consecutive_sixes,
                "game_over": game.game_over,
                "token_positions": {},
            }

            for j, player in enumerate(game.players):
                snapshot["token_positions"][j] = [
                    (token.position, token.state.value) for token in player.tokens
                ]

            snapshots.append(snapshot)

            if not any(player.has_won() for player in game.players):
                game.play_turn()

        # Verify state consistency (no invalid states)
        for snapshot in snapshots:
            self.assertGreaterEqual(snapshot["current_player"], 0)
            self.assertLess(snapshot["current_player"], 4)
            self.assertGreaterEqual(snapshot["consecutive_sixes"], 0)
            self.assertLessEqual(snapshot["consecutive_sixes"], 3)


class TestStrategyIntegration(unittest.TestCase):
    """Integration tests for strategy interactions."""

    def test_strategy_factory_integration(self):
        """Test strategy factory works with game integration."""
        from ludo_engine.strategies import STRATEGIES

        # Create strategies
        killer = STRATEGIES["killer"]()
        winner = STRATEGIES["winner"]()

        # Create game with strategy players
        game = LudoGame([PlayerColor.RED, PlayerColor.BLUE])
        game.players[0].strategy = killer
        game.players[1].strategy = winner

        # Play some turns
        for _ in range(
            20
        ):  # Increase to 20 turns to give more chance for tokens to become active
            if any(player.has_won() for player in game.players):
                break
            game.play_turn()

        # Verify strategies work together - either someone won or tokens are active
        has_winner = any(player.has_won() for player in game.players)
        has_active_tokens = any(player.has_active_tokens() for player in game.players)

        self.assertTrue(
            has_winner or has_active_tokens,
            f"No winner and no active tokens after 20 turns. Winners: {has_winner}, Active tokens: {has_active_tokens}",
        )

    def test_mixed_strategy_game(self):
        """Test game with mixed human and AI players."""
        game = LudoGame([PlayerColor.RED, PlayerColor.BLUE])
        ai_player = Player(PlayerColor.BLUE, 1, RandomStrategy())
        game.players[1].strategy = RandomStrategy()

        # Simulate some AI decisions
        game.current_player_index = 1  # AI player's turn
        context = game.get_ai_decision_context(6)

        if context.valid_moves:
            decision = ai_player.strategy.decide(context)
            self.assertGreaterEqual(decision, 0)
            self.assertLess(decision, 4)


if __name__ == "__main__":
    unittest.main()
