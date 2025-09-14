"""
Utility functions for the Ludo engine.

This module provides helper functions for game analysis,
statistics, and common operations.
"""

from typing import Any, Dict, List

from ..core.game import LudoGame
from ..core.model import GameAnalysis, GameResults, StrategyComparison, TournamentResult


def analyze_game_results(results: GameResults) -> GameAnalysis:
    """
    Analyze game results and provide insights.

    Args:
        results: GameResults from LudoGame.get_game_results()

    Returns:
        GameAnalysis with analysis insights
    """
    analysis = GameAnalysis(
        game_length=results.turns_played,
        efficiency=(
            results.total_moves / results.turns_played
            if results.turns_played > 0
            else 0
        ),
        player_performance={},
        strategy_insights={},
    )

    # Analyze each player's performance
    for player_stats in results.player_stats:
        color = player_stats.color
        analysis.player_performance[color] = {
            "finish_rate": player_stats.tokens_finished / 4,
            "capture_efficiency": player_stats.tokens_captured
            / max(player_stats.total_moves, 1),
            "six_frequency": player_stats.sixes_rolled
            / max(player_stats.total_moves, 1),
            "moves_per_token_finished": player_stats.total_moves
            / max(player_stats.tokens_finished, 1),
        }

    return analysis


def run_strategy_tournament(
    strategies: List[str], rounds: int = 10, games_per_round: int = 5
) -> TournamentResult:
    """
    Run a comprehensive tournament between strategies.

    Args:
        strategies: List of strategy names to compete
        rounds: Number of tournament rounds
        games_per_round: Games per round

    Returns:
        TournamentResult with tournament statistics
    """
    import random

    if len(strategies) < 2:
        raise ValueError("Need at least 2 strategies for tournament")

    results = TournamentResult(
        strategies=strategies,
        rounds=rounds,
        games_per_round=games_per_round,
        total_games=rounds * games_per_round,
        wins={strategy: 0 for strategy in strategies},
        detailed_stats={
            strategy: {
                "games_played": 0,
                "total_tokens_finished": 0,
                "total_captures": 0,
                "total_moves": 0,
                "avg_finish_time": 0,
            }
            for strategy in strategies
        },
        win_rates={},
    )

    all_games = []

    for round_num in range(rounds):
        for game_num in range(games_per_round):
            # Shuffle strategies to avoid position bias
            shuffled_strategies = strategies.copy()
            random.shuffle(shuffled_strategies)

            # Create and play game
            game = LudoGame(
                player_colors=["red", "blue", "green", "yellow"][: len(strategies)],
                strategies=shuffled_strategies,
                seed=random.randint(1, 100000),
            )

            game_results = game.play_game(max_turns=500)
            all_games.append(game_results)

            # Record results
            if game_results.winner:
                for player in game.players:
                    if player.color == game_results.winner:
                        strategy_name = player.strategy.name.lower()
                        results.wins[strategy_name] += 1
                        break

            # Record detailed stats
            for player in game.players:
                strategy_name = player.strategy.name.lower()
                stats = results.detailed_stats[strategy_name]
                player_stats = player.get_stats()

                stats["games_played"] += 1
                stats["total_tokens_finished"] += player_stats["tokens_finished"]
                stats["total_captures"] += player_stats["tokens_captured"]
                stats["total_moves"] += player_stats["total_moves"]

    # Calculate averages
    for strategy in strategies:
        stats = results.detailed_stats[strategy]
        if stats["games_played"] > 0:
            stats["avg_tokens_per_game"] = (
                stats["total_tokens_finished"] / stats["games_played"]
            )
            stats["avg_captures_per_game"] = (
                stats["total_captures"] / stats["games_played"]
            )
            stats["avg_moves_per_game"] = stats["total_moves"] / stats["games_played"]

    # Calculate win rates
    total_games = results.total_games
    results.win_rates = {
        strategy: (wins / total_games) * 100 for strategy, wins in results.wins.items()
    }

    return results


def compare_strategies(
    strategy1: str, strategy2: str, games: int = 50
) -> StrategyComparison:
    """
    Head-to-head comparison between two strategies.

    Args:
        strategy1: First strategy name
        strategy2: Second strategy name
        games: Number of games to play

    Returns:
        StrategyComparison with comparison results
    """
    import random

    results = StrategyComparison(
        strategy1=strategy1,
        strategy2=strategy2,
        games_played=games,
        strategy1_wins=0,
        strategy2_wins=0,
        draws=0,
        games=[],
        strategy1_win_rate=0.0,
        strategy2_win_rate=0.0,
        draw_rate=0.0,
    )

    for i in range(games):
        # Alternate who goes first
        if i % 2 == 0:
            strategies = [strategy1, strategy2]
            colors = ["red", "blue"]
        else:
            strategies = [strategy2, strategy1]
            colors = ["red", "blue"]

        game = LudoGame(colors, strategies, seed=random.randint(1, 100000))
        game_result = game.play_game(max_turns=400)

        results.games.append(game_result)

        if game_result.winner:
            if i % 2 == 0:  # strategy1 was red
                if game_result.winner == "red":
                    results.strategy1_wins += 1
                else:
                    results.strategy2_wins += 1
            else:  # strategy2 was red
                if game_result.winner == "red":
                    results.strategy2_wins += 1
                else:
                    results.strategy1_wins += 1
        else:
            results.draws += 1

    # Calculate statistics
    results.strategy1_win_rate = (results.strategy1_wins / games) * 100
    results.strategy2_win_rate = (results.strategy2_wins / games) * 100
    results.draw_rate = (results.draws / games) * 100

    return results


def calculate_strategy_elo(
    tournament_results: TournamentResult, initial_elo: int = 1200
) -> Dict[str, int]:
    """
    Calculate ELO ratings for strategies based on tournament results.

    Args:
        tournament_results: TournamentResult from run_strategy_tournament
        initial_elo: Starting ELO rating

    Returns:
        Dictionary mapping strategy names to ELO ratings
    """
    strategies = tournament_results.strategies
    elo_ratings = {strategy: initial_elo for strategy in strategies}

    K = 32  # ELO K-factor

    # Process each game (simplified - assumes all matchups)

    for strategy1 in strategies:
        for strategy2 in strategies:
            if strategy1 != strategy2:
                # Calculate expected scores
                rating_diff = elo_ratings[strategy2] - elo_ratings[strategy1]
                expected_score = 1 / (1 + 10 ** (rating_diff / 400))

                # Get actual score (win rate against this opponent)
                wins1 = tournament_results.wins[strategy1]
                wins2 = tournament_results.wins[strategy2]
                total_wins = wins1 + wins2

                if total_wins > 0:
                    actual_score = wins1 / total_wins

                    # Update ELO
                    elo_change = K * (actual_score - expected_score)
                    elo_ratings[strategy1] += elo_change
                    elo_ratings[strategy2] -= elo_change

    # Round to integers
    return {strategy: round(rating) for strategy, rating in elo_ratings.items()}


def export_game_replay(game: LudoGame, filename: str):
    """
    Export game history to a file for replay/analysis.

    Args:
        game: Completed LudoGame instance
        filename: Output filename
    """
    import json
    from datetime import datetime

    game_state = game.get_game_state()

    replay_data = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "players": [player.color for player in game.players],
            "strategies": [player.strategy.name for player in game.players],
            "total_turns": game.turn_count,
            "winner": game.get_winner(),
        },
        "history": game.game_history,
        "final_state": (
            game_state.to_dict() if hasattr(game_state, "to_dict") else game_state
        ),
    }

    with open(filename, "w") as f:
        json.dump(replay_data, f, indent=2)


def load_game_replay(filename: str) -> Dict[str, Any]:
    """
    Load game replay data from file.

    Args:
        filename: Input filename

    Returns:
        Replay data dictionary
    """
    import json

    with open(filename, "r") as f:
        return json.load(f)
