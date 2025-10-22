"""
Tournament system for Ludo strategies.

This module implements a league-style tournament where different strategies
compete against each other in a round-robin format with home and away games.
"""

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from config import TournamentConfig

from ludo_engine.core import LudoGame, PlayerColor
from ludo_engine.strategies.base import Strategy
from ludo_engine.strategies.strategy import StrategyFactory


@dataclass
class MatchResult:
    """Result of a single match between two strategies."""

    home_strategy: str
    away_strategy: str
    home_points: int
    away_points: int
    winner: Optional[str]
    turns_played: int
    is_draw: bool


@dataclass
class TeamStats:
    """Statistics for a team/strategy in the tournament."""

    strategy_name: str
    games_played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    points: int = 0
    goals_for: int = 0  # Games won
    goals_against: int = 0  # Games lost
    goal_difference: int = 0

    @property
    def win_percentage(self) -> float:
        """Calculate win percentage."""
        if self.games_played == 0:
            return 0.0
        return (self.wins / self.games_played) * 100

    def update_stats(self, result: MatchResult, is_home: bool):
        """Update team statistics based on match result."""
        self.games_played += 1

        if is_home:
            points_earned = result.home_points
        else:
            points_earned = result.away_points

        self.points += points_earned

        if result.is_draw:
            self.draws += 1
        elif (is_home and result.winner == result.home_strategy) or (
            not is_home and result.winner == result.away_strategy
        ):
            self.wins += 1
            self.goals_for += 1
        else:
            self.losses += 1
            self.goals_against += 1

        self.goal_difference = self.goals_for - self.goals_against


class LudoTournament:
    """
    Liga/Premier League style tournament for Ludo strategies.

    Each strategy plays against every other strategy twice:
    once at home and once away. Points are awarded as:
    - Win: 3 points
    - Draw: 1 point
    - Loss: 0 points

    Supports both strategy names (strings) and pre-instantiated Strategy objects.

    Configuration is loaded from .env file or environment variables:
    - TOURNAMENT_MAX_TURNS: Maximum turns per game (default: 200)
    - TOURNAMENT_GAMES_PER_MATCH: Games per match (default: 1)
    - TOURNAMENT_SEED: Random seed for reproducibility (default: None)

    Example usage:
        # Use strategy names (strings)
        tournament = LudoTournament(['random', 'killer'])

        # Use pre-instantiated Strategy objects
        strategies = [RandomStrategy(), KillerStrategy()]
        tournament = LudoTournament(strategies)

        # Custom config
        custom_config = TournamentConfig()
        tournament = LudoTournament(['random', 'killer'], config=custom_config)
    """

    def __init__(
        self,
        strategies: Union[List[str], List[Strategy]],
        config: Optional[TournamentConfig] = None,
    ):
        """
        Initialize the tournament.

        Args:
            strategies: List of strategy names (strings) or Strategy objects to compete
            config: TournamentConfig instance (default: global config)
        """
        # Use provided config or global config
        self.config = config or TournamentConfig()

        # Handle both list of strings and list of Strategy objects
        self._original_strategies = strategies  # Keep original input for reference
        self.strategies: List[Strategy] = []
        self.strategy_names: List[str] = []

        if not strategies:
            raise ValueError("At least one strategy required for tournament")

        # Check if all items are strings (strategy names)
        if all(isinstance(s, str) for s in strategies):
            # Validate strategy names and create instances
            available_strategies = StrategyFactory.get_available_strategies()
            for strategy_name in strategies:
                if strategy_name not in available_strategies:
                    raise ValueError(f"Unknown strategy: {strategy_name}")
                strategy_instance = StrategyFactory.create_strategy(strategy_name)
                self.strategies.append(strategy_instance)
                # Use the capitalized name from the strategy object for consistency
                self.strategy_names.append(strategy_instance.name)

        # Check if all items are Strategy objects
        elif all(isinstance(s, Strategy) for s in strategies):
            # Use the strategy objects directly
            self.strategies = list(strategies)  # Create a copy
            self.strategy_names = [s.name for s in strategies]

        else:
            raise ValueError(
                "Strategies must be either all strings (strategy names) or all Strategy objects"
            )

        if len(self.strategies) < 2:
            raise ValueError("At least 2 strategies required for tournament")

        self.games_per_match = self.config.games_per_match
        self.seed = self.config.seed
        self.max_turns = self.config.max_turns

        # Initialize tournament data using strategy names for keys
        self.team_stats: Dict[str, TeamStats] = {
            name: TeamStats(name) for name in self.strategy_names
        }
        self.match_results: List[MatchResult] = []
        self.completed = False

        if self.seed is not None:
            random.seed(self.seed)

    def _play_match(self, home_strategy: str, away_strategy: str) -> MatchResult:
        """
        Play a match between two strategies.

        Args:
            home_strategy: Name of strategy playing at home
            away_strategy: Name of strategy playing away

        Returns:
            MatchResult with the outcome
        """
        home_wins = 0
        away_wins = 0
        total_turns = 0

        # Get strategy objects by name (case-insensitive lookup)
        home_strategy_obj = next(
            s for s in self.strategies if s.name.lower() == home_strategy.lower()
        )
        away_strategy_obj = next(
            s for s in self.strategies if s.name.lower() == away_strategy.lower()
        )

        # Play multiple games if configured
        for _ in range(self.games_per_match):
            # Create game with home team having slight advantage (goes first)
            game = LudoGame(player_colors=[PlayerColor.RED, PlayerColor.GREEN])

            # Set strategies for players using pre-created objects
            game.players[0].set_strategy(home_strategy_obj)
            game.players[1].set_strategy(away_strategy_obj)

            turns = list(game.play_game(max_turns=self.max_turns))
            total_turns += len(turns)

            winner = game.winner.color if game.winner else None

            if winner == PlayerColor.RED:  # Home team
                home_wins += 1
            elif winner == PlayerColor.GREEN:  # Away team
                away_wins += 1
            # If no winner, it's a draw (no points added)

        # Determine match result
        if home_wins > away_wins:
            winner = home_strategy
            home_points = 3
            away_points = 0
            is_draw = False
        elif away_wins > home_wins:
            winner = away_strategy
            home_points = 0
            away_points = 3
            is_draw = False
        else:
            winner = None
            home_points = 1
            away_points = 1
            is_draw = True

        return MatchResult(
            home_strategy=home_strategy,
            away_strategy=away_strategy,
            home_points=home_points,
            away_points=away_points,
            winner=winner,
            turns_played=total_turns // self.games_per_match,
            is_draw=is_draw,
        )

    def run_tournament(self, verbose: bool = True) -> Dict[str, TeamStats]:
        """
        Run the complete tournament.

        Args:
            verbose: Whether to print match results

        Returns:
            Final team statistics
        """
        if verbose:
            print("🏆 Ludo Strategy Tournament")
            print(f"📊 {len(self.strategy_names)} teams competing")
            print(f"🎮 {self.games_per_match} game(s) per match")
            print("🏠 Home and away format")
            print("=" * 60)

        total_matches = len(self.strategy_names) * (len(self.strategy_names) - 1)
        match_count = 0

        # Round-robin: every team plays every other team home and away
        for home_strategy in self.strategy_names:
            for away_strategy in self.strategy_names:
                if home_strategy != away_strategy:
                    match_count += 1

                    if verbose:
                        print(
                            f"Match {match_count}/{total_matches}: {home_strategy} vs {away_strategy}"
                        )

                    # Play the match
                    result = self._play_match(home_strategy, away_strategy)
                    self.match_results.append(result)

                    # Update team statistics
                    self.team_stats[home_strategy].update_stats(result, is_home=True)
                    self.team_stats[away_strategy].update_stats(result, is_home=False)

                    if verbose:
                        if result.is_draw:
                            print("   📊 DRAW - Both teams get 1 point")
                        else:
                            print(
                                f"   🏆 {result.winner} wins - {result.winner} gets 3 points"
                            )
                        print()

        self.completed = True

        if verbose:
            print("=" * 60)
            print("🏁 Tournament completed!")
            print()
            self.display_final_table()

        return self.team_stats

    def display_final_table(self):
        """Display the final league table."""
        if not self.completed:
            print("⚠️  Tournament not yet completed!")
            return

        # Sort teams by points (descending), then by goal difference, then by goals for
        sorted_teams = sorted(
            self.team_stats.values(),
            key=lambda x: (x.points, x.goal_difference, x.goals_for, -x.losses),
            reverse=True,
        )

        print("🏆 FINAL LEAGUE TABLE")
        print("=" * 85)
        print(
            f"{'Pos':<3} {'Team':<15} {'P':<3} {'W':<3} {'D':<3} {'L':<3} {'GF':<3} {'GA':<3} {'GD':<4} {'Pts':<4} {'Win%':<6}"
        )
        print("-" * 85)

        for pos, team in enumerate(sorted_teams, 1):
            # Add emoji for top positions
            position_emoji = ""
            if pos == 1:
                position_emoji = "🥇"
            elif pos == 2:
                position_emoji = "🥈"
            elif pos == 3:
                position_emoji = "🥉"
            elif pos == len(sorted_teams):
                position_emoji = "🔻"

            gd_str = (
                f"+{team.goal_difference}"
                if team.goal_difference > 0
                else str(team.goal_difference)
            )

            print(
                f"{pos:<3} {team.strategy_name:<15} {team.games_played:<3} {team.wins:<3} "
                f"{team.draws:<3} {team.losses:<3} {team.goals_for:<3} {team.goals_against:<3} "
                f"{gd_str:<4} {team.points:<4} {team.win_percentage:<6.1f} {position_emoji}"
            )

        print("-" * 85)
        print(
            "Legend: P=Played, W=Won, D=Draw, L=Lost, GF=Goals For, GA=Goals Against, GD=Goal Difference"
        )

        # Display champion
        champion = sorted_teams[0]
        print(f"\n🏆 CHAMPION: {champion.strategy_name}")
        print(f"   📊 {champion.points} points from {champion.games_played} games")
        print(f"   🎯 {champion.win_percentage:.1f}% win rate")

        # Display some interesting stats
        print("\n📈 TOURNAMENT STATISTICS:")
        print(f"   🎮 Total matches played: {len(self.match_results)}")

        total_draws = sum(1 for result in self.match_results if result.is_draw)
        print(
            f"   📊 Draws: {total_draws} ({total_draws / len(self.match_results) * 100:.1f}%)"
        )

        # Most competitive match (closest points)
        if self.match_results:
            avg_turns = sum(result.turns_played for result in self.match_results) / len(
                self.match_results
            )
            print(f"   ⏱️  Average game length: {avg_turns:.1f} turns")

    def get_head_to_head(self, strategy1: str, strategy2: str) -> Dict:
        """Get head-to-head record between two strategies."""
        if strategy1 not in self.strategy_names or strategy2 not in self.strategy_names:
            raise ValueError("Both strategies must be in the tournament")

        relevant_matches = [
            result
            for result in self.match_results
            if (result.home_strategy == strategy1 and result.away_strategy == strategy2)
            or (result.home_strategy == strategy2 and result.away_strategy == strategy1)
        ]

        strategy1_wins = 0
        strategy2_wins = 0
        draws = 0

        for match in relevant_matches:
            if match.is_draw:
                draws += 1
            elif match.winner == strategy1:
                strategy1_wins += 1
            elif match.winner == strategy2:
                strategy2_wins += 1

        return {
            "strategy1": strategy1,
            "strategy2": strategy2,
            "strategy1_wins": strategy1_wins,
            "strategy2_wins": strategy2_wins,
            "draws": draws,
            "total_matches": len(relevant_matches),
        }


def run_sample_tournament():
    """Run a sample tournament with diverse strategies."""
    strategies = [
        "random",
        "killer",
        "defensive",
        "balanced",
        "cautious",
        "optimist",
        "winner",
        "probabilistic",
    ]

    print("🚀 Running Sample Ludo Strategy Tournament")
    print(f"🎯 Strategies: {', '.join(strategies)}")
    print()

    tournament = LudoTournament(
        strategies=strategies,
        seed=42,  # For reproducible results
    )

    tournament.run_tournament(verbose=True)

    # Show some head-to-head examples
    print("\n🤝 HEAD-TO-HEAD EXAMPLES:")
    h2h = tournament.get_head_to_head("killer", "defensive")
    print(
        f"Killer vs Defensive: {h2h['strategy1_wins']}-{h2h['draws']}-{h2h['strategy2_wins']}"
    )

    h2h = tournament.get_head_to_head("probabilistic", "random")
    print(
        f"Probabilistic vs Random: {h2h['strategy1_wins']}-{h2h['draws']}-{h2h['strategy2_wins']}"
    )

    return tournament


def run_custom_strategy_tournament():
    """Demonstrate tournament with custom Strategy objects."""
    from ludo_engine.strategies.aggressive.killer import KillerStrategy
    from ludo_engine.strategies.baseline.random_strategy import RandomStrategy

    # Create custom strategy instances
    custom_random = RandomStrategy()
    custom_killer = KillerStrategy()

    # You can modify strategies here if needed
    # custom_killer.some_parameter = custom_value

    strategies = [custom_random, custom_killer]

    print("🚀 Running Custom Strategy Tournament")
    print("🎯 Using pre-instantiated Strategy objects")
    print(f"📊 Strategies: {', '.join(s.name for s in strategies)}")
    print()

    tournament = LudoTournament(
        strategies=strategies,  # Pass Strategy objects directly
        seed=42,
    )

    tournament.run_tournament(verbose=True)
    return tournament


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--custom":
        print("Running custom strategy tournament...")
        run_custom_strategy_tournament()
    else:
        print("Running standard tournament...")
        run_sample_tournament()
