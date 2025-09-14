"""
Comprehensive tests for Ludo utility functions.

This module contains tests for all utility functions including:
- Game result analysis
- Strategy tournaments
- Strategy comparisons
- ELO calculations
- Game replay functionality
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ludo_engine.core.game import LudoGame
from ludo_engine.core.player import Player
from ludo_engine.utils import (
    analyze_game_results,
    calculate_strategy_elo,
    compare_strategies,
    export_game_replay,
    load_game_replay,
    run_strategy_tournament,
)


class TestGameAnalysis(unittest.TestCase):
    """Test cases for game analysis functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_game_results = {
            "winner": "red",
            "turns_played": 45,
            "total_moves": 180,
            "player_stats": [
                {
                    "color": "red",
                    "tokens_finished": 4,
                    "tokens_captured": 3,
                    "total_moves": 45,
                    "sixes_rolled": 8,
                },
                {
                    "color": "blue",
                    "tokens_finished": 2,
                    "tokens_captured": 1,
                    "total_moves": 43,
                    "sixes_rolled": 6,
                },
            ],
        }

    def test_analyze_game_results(self):
        """Test game result analysis."""
        analysis = analyze_game_results(self.sample_game_results)

        # Check basic metrics
        self.assertEqual(analysis["game_length"], 45)
        self.assertEqual(analysis["efficiency"], 180 / 45)  # 4.0

        # Check player performance
        red_perf = analysis["player_performance"]["red"]
        self.assertEqual(red_perf["finish_rate"], 4 / 4)  # 1.0
        self.assertEqual(red_perf["capture_efficiency"], 3 / 45)
        self.assertEqual(red_perf["six_frequency"], 8 / 45)
        self.assertEqual(red_perf["moves_per_token_finished"], 45 / 4)

    def test_analyze_game_results_zero_turns(self):
        """Test analysis with zero turns (edge case)."""
        results = self.sample_game_results.copy()
        results["turns_played"] = 0

        analysis = analyze_game_results(results)
        self.assertEqual(analysis["efficiency"], 0)

    def test_analyze_game_results_zero_tokens_finished(self):
        """Test analysis with zero tokens finished (edge case)."""
        results = self.sample_game_results.copy()
        results["player_stats"][0]["tokens_finished"] = 0

        analysis = analyze_game_results(results)
        red_perf = analysis["player_performance"]["red"]
        self.assertEqual(red_perf["moves_per_token_finished"], 45 / 1)  # Uses max(1, tokens_finished)


class TestStrategyTournament(unittest.TestCase):
    """Test cases for strategy tournament functionality."""

    def test_run_strategy_tournament_insufficient_strategies(self):
        """Test tournament with insufficient strategies."""
        with self.assertRaises(ValueError):
            run_strategy_tournament(["random"], rounds=1, games_per_round=1)

    @patch('ludo_engine.utils.LudoGame')
    def test_run_strategy_tournament_basic(self, mock_game_class):
        """Test basic tournament execution."""
        # Mock game instance
        mock_game = Mock()
        mock_strategy1 = Mock()
        mock_strategy1.name = "Random"
        mock_strategy2 = Mock()
        mock_strategy2.name = "Killer"

        mock_player1 = Mock()
        mock_player1.color = "red"
        mock_player1.strategy = mock_strategy1
        mock_player1.get_stats.return_value = {
            "tokens_finished": 4,
            "tokens_captured": 2,
            "total_moves": 30,
        }

        mock_player2 = Mock()
        mock_player2.color = "blue"
        mock_player2.strategy = mock_strategy2
        mock_player2.get_stats.return_value = {
            "tokens_finished": 1,
            "tokens_captured": 1,
            "total_moves": 28,
        }

        mock_game.players = [mock_player1, mock_player2]
        mock_game.play_game.return_value = {
            "winner": "red",
            "turns_played": 30,
            "total_moves": 120,
        }

        mock_game_class.return_value = mock_game

        results = run_strategy_tournament(
            ["random", "killer"],
            rounds=1,
            games_per_round=1
        )

        # Verify results structure
        self.assertIn("strategies", results)
        self.assertIn("wins", results)
        self.assertIn("detailed_stats", results)
        self.assertIn("win_rates", results)

        # Verify win was recorded
        self.assertEqual(results["wins"]["random"], 1)
        self.assertEqual(results["wins"]["killer"], 0)

    @patch('random.shuffle')
    @patch('random.randint')
    @patch('ludo_engine.utils.LudoGame')
    def test_run_strategy_tournament_multiple_games(self, mock_game_class, mock_randint, mock_shuffle):
        """Test tournament with multiple games."""
        mock_shuffle.side_effect = lambda x: None  # No-op shuffle
        mock_randint.return_value = 42

        # Mock game instance
        mock_game = Mock()
        mock_strategy1 = Mock()
        mock_strategy1.name = "Random"
        mock_strategy2 = Mock()
        mock_strategy2.name = "Killer"

        mock_player1 = Mock()
        mock_player1.color = "red"
        mock_player1.strategy = mock_strategy1
        mock_player1.get_stats.return_value = {
            "tokens_finished": 4, "tokens_captured": 2, "total_moves": 30
        }

        mock_player2 = Mock()
        mock_player2.color = "blue"
        mock_player2.strategy = mock_strategy2
        mock_player2.get_stats.return_value = {
            "tokens_finished": 1, "tokens_captured": 1, "total_moves": 28
        }

        mock_game.players = [mock_player1, mock_player2]
        mock_game.play_game.return_value = {"winner": "red"}

        mock_game_class.return_value = mock_game

        results = run_strategy_tournament(
            ["random", "killer"],
            rounds=2,
            games_per_round=3
        )

        # Should have played 6 games total
        self.assertEqual(results["total_games"], 6)
        self.assertEqual(mock_game_class.call_count, 6)


class TestStrategyComparison(unittest.TestCase):
    """Test cases for strategy comparison functionality."""

    @patch('ludo_engine.utils.LudoGame')
    def test_compare_strategies(self, mock_game_class):
        """Test strategy comparison."""
        # Mock game instance
        mock_game = Mock()
        mock_strategy1 = Mock()
        mock_strategy1.name = "Strategy1"
        mock_strategy2 = Mock()
        mock_strategy2.name = "Strategy2"

        mock_player1 = Mock()
        mock_player1.color = "red"
        mock_player1.strategy = mock_strategy1

        mock_player2 = Mock()
        mock_player2.color = "blue"
        mock_player2.strategy = mock_strategy2

        mock_game.players = [mock_player1, mock_player2]

        # Alternate winners for fairness
        mock_game.play_game.side_effect = [
            {"winner": "red", "turns_played": 30},
            {"winner": "blue", "turns_played": 35},
            {"winner": None, "turns_played": 50},  # Draw
        ]

        mock_game_class.return_value = mock_game

        results = compare_strategies("strategy1", "strategy2", games=3)

        # Verify results structure
        self.assertIn("strategy1_wins", results)
        self.assertIn("strategy2_wins", results)
        self.assertIn("draws", results)
        self.assertIn("games_played", results)
        self.assertIn("strategy1_win_rate", results)
        self.assertIn("strategy2_win_rate", results)

        # Verify counts based on actual function logic
        # Game 0: strategy1=red wins -> strategy1_wins=1
        # Game 1: strategy1=blue wins -> strategy1_wins=2  
        # Game 2: draw -> draws=1
        self.assertEqual(results["strategy1_wins"], 2)
        self.assertEqual(results["strategy2_wins"], 0)
        self.assertEqual(results["draws"], 1)
        self.assertEqual(results["games_played"], 3)


class TestEloCalculation(unittest.TestCase):
    """Test cases for ELO calculation functionality."""

    def test_calculate_strategy_elo(self):
        """Test ELO rating calculation."""
        tournament_results = {
            "strategies": ["random", "killer", "defensive"],
            "wins": {"random": 15, "killer": 20, "defensive": 10},
            "total_games": 45,
        }

        elo_ratings = calculate_strategy_elo(tournament_results)

        # Verify all strategies have ELO ratings
        self.assertIn("random", elo_ratings)
        self.assertIn("killer", elo_ratings)
        self.assertIn("defensive", elo_ratings)

        # Killer should have highest rating (most wins)
        self.assertGreater(elo_ratings["killer"], elo_ratings["random"])
        self.assertGreater(elo_ratings["random"], elo_ratings["defensive"])

    def test_calculate_strategy_elo_perfect_scores(self):
        """Test ELO with perfect and zero win records."""
        tournament_results = {
            "strategies": ["perfect", "terrible"],
            "wins": {"perfect": 10, "terrible": 0},
            "total_games": 10,
        }

        elo_ratings = calculate_strategy_elo(tournament_results)

        # Perfect strategy should have higher rating than terrible
        self.assertGreater(elo_ratings["perfect"], elo_ratings["terrible"])


class TestGameReplay(unittest.TestCase):
    """Test cases for game replay functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_game = Mock(spec=LudoGame)
        self.mock_game.turn_count = 5
        self.mock_game.game_state = Mock()
        self.mock_game.game_state.value = "finished"
        self.mock_game.winner = "red"
        self.mock_game.game_history = []
        self.mock_game.get_winner.return_value = "red"
        self.mock_game.get_game_state.return_value = {"board": {}, "players": {}}

        # Mock players with strategy
        mock_strategy = Mock()
        mock_strategy.name = "TestStrategy"

        mock_player = Mock(spec=Player)
        mock_player.color = "red"
        mock_player.strategy = mock_strategy
        mock_player.get_stats.return_value = {
            "tokens_finished": 4,
            "tokens_captured": 2,
            "total_moves": 25,
        }
        self.mock_game.players = [mock_player]

    def test_export_game_replay(self):
        """Test exporting game replay."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_filename = f.name

        try:
            export_game_replay(self.mock_game, temp_filename)

            # Verify file was created
            self.assertTrue(os.path.exists(temp_filename))

            # Verify file content
            with open(temp_filename, 'r') as f:
                import json
                data = json.load(f)

            self.assertIn("metadata", data)
            self.assertIn("history", data)
            self.assertIn("final_state", data)
            self.assertEqual(data["metadata"]["winner"], "red")
            self.assertEqual(data["metadata"]["strategies"], ["TestStrategy"])

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_load_game_replay(self):
        """Test loading game replay."""
        replay_data = {
            "game_state": "finished",
            "turn_count": 10,
            "winner": "blue",
            "players": [
                {
                    "color": "red",
                    "stats": {"tokens_finished": 3},
                }
            ],
        }

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            import json
            json.dump(replay_data, f)
            temp_filename = f.name

        try:
            loaded_data = load_game_replay(temp_filename)

            self.assertEqual(loaded_data["game_state"], "finished")
            self.assertEqual(loaded_data["turn_count"], 10)
            self.assertEqual(loaded_data["winner"], "blue")

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_load_game_replay_file_not_found(self):
        """Test loading replay from non-existent file."""
        with self.assertRaises(FileNotFoundError):
            load_game_replay("non_existent_file.json")


if __name__ == "__main__":
    unittest.main()