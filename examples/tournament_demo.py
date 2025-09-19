#!/usr/bin/env python3
"""
Ludo Strategy Tournament Demo

This script demonstrates the tournament system by running competitions
between different AI strategies using configuration from .env file.
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TournamentConfig
from tournament import LudoTournament


def main():
    """Run tournament using configuration from .env file."""
    print("🎮 LUDO STRATEGY TOURNAMENT")
    print("=" * 50)

    # Load configuration from .env file
    config = TournamentConfig()
    print("🎛️ Configuration loaded from .env file:")
    print(f"   Max turns per game: {config.max_turns}")
    print(f"   Games per match: {config.games_per_match}")
    print(f"   Default strategies: {', '.join(config.default_strategies)}")
    print(f"   Verbose logging: {config.verbose_logging}")
    print()

    # Create and run tournament with config defaults
    tournament = LudoTournament(strategies=config.default_strategies, config=config)

    print("🚀 Starting tournament...")
    tournament.run_tournament(seed=42, verbose=True)


if __name__ == "__main__":
    main()
