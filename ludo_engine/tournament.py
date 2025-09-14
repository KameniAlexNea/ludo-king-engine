"""
Tournament system for Ludo strategies.

This module implements a league-style tournament where different strategies
compete against each other in a round-robin format with home and away games.
"""

import random
from dataclasses import dataclass
from typing import Dict, List, Optional

from .core.game import LudoGame
from .strategies.factory import StrategyFactory


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
    """

    def __init__(
        self,
        strategies: List[str],
        games_per_match: int = 1,
        seed: Optional[int] = None,
    ):
        """
        Initialize the tournament.

        Args:
            strategies: List of strategy names to compete
            games_per_match: Number of games per match (default 1)
            seed: Random seed for reproducible results
        """
        self.strategies = strategies
        self.games_per_match = games_per_match
        self.seed = seed

        # Validate strategies
        available_strategies = StrategyFactory.get_available_strategies()
        for strategy in strategies:
            if strategy not in available_strategies:
                raise ValueError(f"Unknown strategy: {strategy}")

        if len(strategies) < 2:
            raise ValueError("At least 2 strategies required for tournament")

        # Initialize tournament data
        self.team_stats: Dict[str, TeamStats] = {
            strategy: TeamStats(strategy) for strategy in strategies
        }
        self.match_results: List[MatchResult] = []
        self.completed = False

        if seed is not None:
            random.seed(seed)

    def _play_match(self, home_strategy: str, away_strategy: str) -> MatchResult:
        """
        Play a match between two strategies.

        Args:
            home_strategy: Strategy playing at home
            away_strategy: Strategy playing away

        Returns:
            MatchResult with the outcome
        """
        home_wins = 0
        away_wins = 0
        total_turns = 0

        # Play multiple games if configured
        for _ in range(self.games_per_match):
            # Create game with home team having slight advantage (goes first)
            game = LudoGame(
                player_colors=["red", "blue"],
                strategies=[home_strategy, away_strategy],
                seed=random.randint(1, 1000000) if self.seed is None else None,
            )

            result = game.play_game()
            total_turns += result.turns_played

            if result.winner == "red":  # Home team
                home_wins += 1
            elif result.winner == "blue":  # Away team
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
            print(f"📊 {len(self.strategies)} teams competing")
            print(f"🎮 {self.games_per_match} game(s) per match")
            print("🏠 Home and away format")
            print("=" * 60)

        total_matches = len(self.strategies) * (len(self.strategies) - 1)
        match_count = 0

        # Round-robin: every team plays every other team home and away
        for home_strategy in self.strategies:
            for away_strategy in self.strategies:
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
        if strategy1 not in self.strategies or strategy2 not in self.strategies:
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
        games_per_match=1,
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


if __name__ == "__main__":
    run_sample_tournament()
