"""
Comprehensive Ludo Engine Example.

This script demonstrates the full capabilities of the Ludo Core Engine,
including different strategies, game analysis, and tournament simulation.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random

from ludo_engine import LudoGame, StrategyFactory


def demonstrate_basic_game():
    """Demonstrate a basic game with different strategies."""
    print("=== Basic Game Demonstration ===")

    # Create a game with different strategies
    game = LudoGame(
        player_colors=["red", "blue", "green", "yellow"],
        strategies=["random", "killer", "defensive", "balanced"],
        seed=12345,
    )

    print(f"Created game with {len(game.players)} players:")
    for player in game.players:
        print(f"  - {player.name} ({player.color}): {player.strategy.name}")

    # Play the complete game
    print("\nPlaying complete game...")
    results = game.play_game(max_turns=500)  # Prevent infinite games

    print("\nGame Results:")
    print(f"Winner: {results.winner}")
    print(f"Turns played: {results.turns_played}")
    print(f"Total moves: {results.total_moves}")

    print("\nPlayer Statistics:")
    for stats in results.player_stats:
        print(f"  {stats.name} ({stats.color}):")
        print(f"    Tokens finished: {stats.tokens_finished}")
        print(f"    Tokens captured: {stats.tokens_captured}")
        print(f"    Total moves: {stats.total_moves}")
        print(f"    Sixes rolled: {stats.sixes_rolled}")


def demonstrate_strategy_comparison():
    """Compare different strategies head-to-head."""
    print("\n=== Strategy Comparison ===")

    strategies = ["random", "killer", "defensive", "balanced"]
    wins = {strategy: 0 for strategy in strategies}
    games_played = 20

    print(f"Running {games_played} games to compare strategies...")

    for game_num in range(games_played):
        # Randomize strategy assignment to avoid bias
        random.shuffle(strategies)

        game = LudoGame(
            player_colors=["red", "blue", "green", "yellow"],
            strategies=strategies.copy(),
            seed=random.randint(1, 10000),
        )

        results = game.play_game(max_turns=300)
        winner_color = results.winner

        if winner_color:
            # Find which strategy won
            for player in game.players:
                if player.color == winner_color:
                    wins[player.strategy.name.lower()] += 1
                    break

        if (game_num + 1) % 5 == 0:
            print(f"  Completed {game_num + 1}/{games_played} games...")

    print(f"\nStrategy Win Rates (out of {games_played} games):")
    for strategy, win_count in wins.items():
        win_rate = (win_count / games_played) * 100
        print(f"  {strategy.capitalize()}: {win_count} wins ({win_rate:.1f}%)")


def demonstrate_advanced_strategies():
    """Demonstrate advanced strategy capabilities."""
    print("\n=== Advanced Strategy Demonstration ===")

    advanced_strategies = ["cautious", "optimist", "winner", "probabilistic"]

    print("Available advanced strategies:")
    strategy_info = StrategyFactory.get_strategy_info()
    for strategy in advanced_strategies:
        print(f"  - {strategy.capitalize()}: {strategy_info[strategy]}")

    # Play a game with all advanced strategies
    game = LudoGame(
        player_colors=["red", "blue", "green", "yellow"],
        strategies=advanced_strategies,
        seed=54321,
    )

    print("\nPlaying game with advanced strategies...")
    results = game.play_game(max_turns=400)

    print(f"Winner: {results.winner} ({results.turns_played} turns)")


def demonstrate_game_analysis():
    """Demonstrate game state analysis capabilities."""
    print("\n=== Game Analysis Demonstration ===")

    game = LudoGame(["red", "blue"], ["balanced", "probabilistic"], seed=99999)
    game.start_game()

    print("Playing game with detailed analysis...")

    for turn in range(20):  # Play 20 turns for analysis
        if game.is_finished():
            break

        current_player = game.get_current_player()
        print(f"\nTurn {turn + 1} - {current_player.name} ({current_player.color}):")

        # Show token positions before move
        tokens_home = len(current_player.get_tokens_at_home())
        tokens_active = len(current_player.get_active_tokens())
        tokens_finished = len(current_player.get_finished_tokens())

        print(
            f"  Tokens - Home: {tokens_home}, Active: {tokens_active}, Finished: {tokens_finished}"
        )

        # Play turn
        turn_result = game.play_turn()

        print(f"  Dice roll: {turn_result.dice_roll}")
        print(f"  Move made: {turn_result.move_made}")

        if turn_result.captured_tokens:
            print(f"  Captured {len(turn_result.captured_tokens)} opponent token(s)!")

        if turn_result.finished_tokens > 0:
            print(f"  Has {turn_result.finished_tokens} token(s) finished!")

        if turn_result.another_turn:
            print("  Gets another turn!")

    print(f"\nGame state after {turn + 1} turns:")
    game_state = game.get_game_state()
    print(f"Current player: {game.players[game_state.current_player].name}")
    print(f"Total turns: {game_state.turn_count}")


def demonstrate_tournament_mode():
    """Demonstrate tournament-style competition."""
    print("\n=== Tournament Mode Demonstration ===")

    # Create tournament with all available strategies
    tournament_strategies = StrategyFactory.get_available_strategies()[
        :4
    ]  # Use 4 strategies

    print(f"Tournament participants: {tournament_strategies}")

    tournament_results = {}
    for strategy in tournament_strategies:
        tournament_results[strategy] = {"wins": 0, "games": 0}

    rounds = 5
    print(f"Running {rounds} tournament rounds...")

    for round_num in range(rounds):
        # Each round, each strategy plays once
        random.shuffle(tournament_strategies)

        game = LudoGame(
            player_colors=["red", "blue", "green", "yellow"],
            strategies=tournament_strategies.copy(),
            seed=random.randint(1, 100000),
        )

        results = game.play_game(max_turns=400)

        # Record results
        for player in game.players:
            strategy_name = player.strategy.name.lower()
            tournament_results[strategy_name]["games"] += 1

            if player.color == results.winner:
                tournament_results[strategy_name]["wins"] += 1

        print(f"  Round {round_num + 1}: Winner = {results.winner}")

    print("\nTournament Results:")
    sorted_results = sorted(
        tournament_results.items(), key=lambda x: x[1]["wins"], reverse=True
    )

    for rank, (strategy, stats) in enumerate(sorted_results, 1):
        win_rate = (stats["wins"] / stats["games"]) * 100 if stats["games"] > 0 else 0
        print(
            f"  {rank}. {strategy.capitalize()}: {stats['wins']}/{stats['games']} wins ({win_rate:.1f}%)"
        )


def main():
    """Run all demonstrations."""
    print("🎲 Ludo Core Engine - Comprehensive Demonstration 🎲\n")

    try:
        demonstrate_basic_game()
        demonstrate_strategy_comparison()
        demonstrate_advanced_strategies()
        demonstrate_game_analysis()
        demonstrate_tournament_mode()

        print("\n🎉 All demonstrations completed successfully!")
        print("\nThe Ludo Core Engine is ready for:")
        print("  ✓ Reinforcement learning training")
        print("  ✓ Strategy development and testing")
        print("  ✓ Game analysis and research")
        print("  ✓ Tournament simulations")
        print("  ✓ Educational purposes")

    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
