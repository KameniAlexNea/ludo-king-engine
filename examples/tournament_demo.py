#!/usr/bin/env python3
"""
Ludo Strategy Tournament Demo

This script demonstrates the tournament system by running competitions
between different AI strategies in a Premier League style format.
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ludo_engine.tournament import LudoTournament, run_sample_tournament


def run_basic_tournament():
    """Run a basic tournament with 4 strategies."""
    print("🏆 BASIC TOURNAMENT (4 Teams)")
    print("=" * 50)

    strategies = ["random", "killer", "defensive", "balanced"]

    tournament = LudoTournament(strategies=strategies, games_per_match=1, seed=42)

    tournament.run_tournament(verbose=True)

    print("\n" + "=" * 50)
    print("🤝 HEAD-TO-HEAD ANALYSIS:")

    # Show head-to-head between different strategy types
    h2h = tournament.get_head_to_head("killer", "defensive")
    print(
        f"🗡️  Killer vs 🛡️  Defensive: {h2h['strategy1_wins']}-{h2h['draws']}-{h2h['strategy2_wins']}"
    )

    h2h = tournament.get_head_to_head("balanced", "random")
    print(
        f"⚖️  Balanced vs 🎲 Random: {h2h['strategy1_wins']}-{h2h['draws']}-{h2h['strategy2_wins']}"
    )


def run_advanced_tournament():
    """Run a more comprehensive tournament with advanced strategies."""
    print("\n\n🏆 ADVANCED TOURNAMENT (8 Teams)")
    print("=" * 50)

    strategies = [
        "random",  # 🎲 Pure randomness
        "killer",  # 🗡️  Aggressive capture-focused
        "defensive",  # 🛡️  Safety-first approach
        "balanced",  # ⚖️  Balanced risk/reward
        "cautious",  # 🐢 Very conservative
        "optimist",  # 🚀 High-risk high-reward
        "winner",  # 🏁 Finish-line focused
        "probabilistic",  # 🧮 Mathematical approach
    ]

    tournament = LudoTournament(
        strategies=strategies,
        games_per_match=1,  # Single game per match for speed
        seed=123,  # Different seed for variety
    )

    tournament.run_tournament(verbose=True)

    print("\n" + "=" * 60)
    print("📊 STRATEGY ANALYSIS:")

    # Analyze different strategy matchups
    print("\n🔥 AGGRESSIVE vs DEFENSIVE:")
    aggressive = ["killer", "optimist"]
    defensive = ["defensive", "cautious"]

    for agg in aggressive:
        for def_strat in defensive:
            h2h = tournament.get_head_to_head(agg, def_strat)
            print(
                f"   {agg.capitalize()} vs {def_strat.capitalize()}: "
                f"{h2h['strategy1_wins']}-{h2h['draws']}-{h2h['strategy2_wins']}"
            )

    print("\n🧠 SMART vs RANDOM:")
    smart = ["probabilistic", "balanced", "winner"]

    for smart_strat in smart:
        h2h = tournament.get_head_to_head(smart_strat, "random")
        print(
            f"   {smart_strat.capitalize()} vs Random: "
            f"{h2h['strategy1_wins']}-{h2h['draws']}-{h2h['strategy2_wins']}"
        )


def run_custom_tournament():
    """Allow user to create a custom tournament."""
    print("\n\n🎮 CUSTOM TOURNAMENT BUILDER")
    print("=" * 50)

    from ludo_engine.strategies.factory import StrategyFactory

    available = StrategyFactory.get_available_strategies()
    print(f"📋 Available strategies: {', '.join(available)}")

    print("\nEnter strategies to compete (comma-separated):")
    print("Example: random,killer,defensive,balanced")

    try:
        user_input = input("Strategies: ").strip()
        if not user_input:
            print("Using default strategies...")
            strategies = ["random", "killer", "defensive", "balanced"]
        else:
            strategies = [s.strip().lower() for s in user_input.split(",")]

        # Validate strategies
        invalid = [s for s in strategies if s not in available]
        if invalid:
            print(f"❌ Invalid strategies: {invalid}")
            return

        if len(strategies) < 2:
            print("❌ Need at least 2 strategies!")
            return

        games_per_match = 1
        try:
            games_input = input("Games per match (default 1): ").strip()
            if games_input:
                games_per_match = int(games_input)
        except ValueError:
            print("Using default: 1 game per match")

        print(f"\n🚀 Starting tournament with {len(strategies)} strategies...")

        tournament = LudoTournament(
            strategies=strategies,
            games_per_match=games_per_match,
            seed=None,  # Random seed for variety
        )

        tournament.run_tournament(verbose=True)

    except KeyboardInterrupt:
        print("\n👋 Tournament cancelled!")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main function to run different tournament types."""
    print("🎮 LUDO STRATEGY TOURNAMENT SYSTEM")
    print("=" * 60)

    while True:
        print("\nChoose tournament type:")
        print("1. 🏃 Quick Tournament (4 strategies)")
        print("2. 🏆 Full Tournament (8 strategies)")
        print("3. 🎮 Custom Tournament")
        print("4. 📊 Sample Tournament (demo)")
        print("5. 👋 Exit")

        try:
            choice = input("\nEnter choice (1-5): ").strip()

            if choice == "1":
                run_basic_tournament()
            elif choice == "2":
                run_advanced_tournament()
            elif choice == "3":
                run_custom_tournament()
            elif choice == "4":
                run_sample_tournament()
            elif choice == "5":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
