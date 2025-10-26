"""Round-robin tournament runner for the simplified Ludo engine.

This example wires together :mod:`ludo_engine` with the minimal strategy
builders exposed by :mod:`ludo_engine_strategies`. Two strategies face each
other in home/away fixtures (``red`` versus ``green`` by default) and the
tournament tracks both match points and per-game win totals.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Union

from config import TournamentConfig

from ludo_engine.constants import CONFIG
from ludo_engine.game import DecisionFn, Game
from ludo_engine.player import Player
from ludo_engine_strategies import available_strategies, build_strategy

HOME_COLOR, AWAY_COLOR = CONFIG.colors[:2]

StrategyBuilder = Callable[[Game], DecisionFn]
StrategySpec = Union[str, "StrategyEntry"]


@dataclass(frozen=True)
class StrategyEntry:
    """Roster entry describing how to build a strategy for a given game."""

    identifier: str
    display_name: str
    builder: StrategyBuilder

    @staticmethod
    def from_name(
        name: str,
        *,
        display_name: Optional[str] = None,
        **builder_kwargs,
    ) -> "StrategyEntry":
        identifier = name.lower()
        label = display_name or name
        params = dict(builder_kwargs)

        def _builder(game: Game, *, key: str = identifier, options: Dict = params):
            return build_strategy(key, game, **options)

        return StrategyEntry(identifier=identifier, display_name=label, builder=_builder)


@dataclass
class MatchResult:
    """Result of a match (possibly multiple games) between two strategies."""

    home_strategy: str
    away_strategy: str
    home_points: int
    away_points: int
    winner: Optional[str]
    turns_played: int
    is_draw: bool
    home_game_wins: int
    away_game_wins: int
    draw_games: int


@dataclass
class TeamStats:
    """Aggregate standings information for a strategy."""

    strategy_name: str
    games_played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    points: int = 0
    goals_for: int = 0
    goals_against: int = 0
    goal_difference: int = 0

    @property
    def win_percentage(self) -> float:
        if self.games_played == 0:
            return 0.0
        return (self.wins / self.games_played) * 100

    def reset(self) -> None:
        self.games_played = 0
        self.wins = 0
        self.draws = 0
        self.losses = 0
        self.points = 0
        self.goals_for = 0
        self.goals_against = 0
        self.goal_difference = 0

    def update_stats(self, result: MatchResult, is_home: bool) -> None:
        self.games_played += 1

        if is_home:
            points_earned = result.home_points
            games_won = result.home_game_wins
            games_lost = result.away_game_wins
        else:
            points_earned = result.away_points
            games_won = result.away_game_wins
            games_lost = result.home_game_wins

        self.points += points_earned
        self.goals_for += games_won
        self.goals_against += games_lost
        self.goal_difference = self.goals_for - self.goals_against

        if result.is_draw:
            self.draws += 1
        elif points_earned == 3:
            self.wins += 1
        else:
            self.losses += 1


class LudoTournament:
    """Round-robin tournament for decision-function based strategies."""

    def __init__(
        self,
        strategies: Sequence[StrategySpec],
        *,
        config: Optional[TournamentConfig] = None,
        games_per_match: Optional[int] = None,
        max_turns: Optional[int] = None,
        seed: Optional[int] = None,
        player_colors: Optional[Sequence[str]] = None,
    ) -> None:
        if not strategies:
            raise ValueError("At least one strategy required for tournament")

        self.config = config or TournamentConfig()
        self.games_per_match = (
            games_per_match if games_per_match is not None else self.config.games_per_match
        )
        self.max_turns = max_turns if max_turns is not None else self.config.max_turns
        self.seed = seed if seed is not None else self.config.seed

        if self.games_per_match < 1:
            raise ValueError("games_per_match must be at least 1")
        if self.max_turns < 1:
            raise ValueError("max_turns must be at least 1")

        allowed_lookup = {color.lower(): color for color in CONFIG.colors}
        chosen_colors = tuple(player_colors) if player_colors is not None else (
            HOME_COLOR,
            AWAY_COLOR,
        )
        if len(chosen_colors) != 2:
            raise ValueError(
                "Tournament currently supports exactly two player colors per match"
            )

        canonical_colors: List[str] = []
        seen_colors = set()
        for color in chosen_colors:
            key = color.lower()
            if key in seen_colors:
                raise ValueError("Player colors must be unique")
            if key not in allowed_lookup:
                available = ", ".join(CONFIG.colors)
                raise ValueError(f"Unknown player color '{color}'. Choices: {available}")
            seen_colors.add(key)
            canonical_colors.append(allowed_lookup[key])

        self.home_color, self.away_color = canonical_colors

        available_builtin = {name.lower() for name in available_strategies(include_special=True)}
        entries: List[StrategyEntry] = []

        for spec in strategies:
            if isinstance(spec, StrategyEntry):
                entry = spec
            elif isinstance(spec, str):
                key = spec.lower()
                if key not in available_builtin:
                    choices = ", ".join(sorted(available_builtin))
                    raise ValueError(f"Unknown strategy '{spec}'. Available: {choices}")
                entry = StrategyEntry.from_name(spec)
            else:
                raise TypeError(
                    "Strategies must be provided as names or StrategyEntry instances"
                )
            entries.append(entry)

        if len(entries) < 2:
            raise ValueError("At least two strategies required for tournament")

        display_names = [entry.display_name for entry in entries]
        if len(set(display_names)) != len(display_names):
            raise ValueError("Strategy display names must be unique")

        self.strategy_entries: Dict[str, StrategyEntry] = {
            entry.display_name: entry for entry in entries
        }
        self.strategy_names = display_names

        self.team_stats: Dict[str, TeamStats] = {
            name: TeamStats(name) for name in self.strategy_names
        }
        self.match_results: List[MatchResult] = []
        self.completed = False
        self._rng = random.Random(self.seed)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _reset_table(self) -> None:
        self.match_results.clear()
        for stats in self.team_stats.values():
            stats.reset()
        self.completed = False

    def _create_game(
        self,
        home_entry: StrategyEntry,
        away_entry: StrategyEntry,
        *,
        seed: Optional[int],
    ) -> Game:
        game = Game(
            seed=seed,
            players=[Player(self.home_color), Player(self.away_color)],
        )
        game.strategies[self.home_color] = home_entry.builder(game)
        game.strategies[self.away_color] = away_entry.builder(game)
        return game

    def _run_single_game(
        self,
        home_entry: StrategyEntry,
        away_entry: StrategyEntry,
        *,
        seed: Optional[int],
    ) -> Tuple[Optional[str], int]:
        game = self._create_game(home_entry, away_entry, seed=seed)
        turns = 0
        while turns < self.max_turns and not game.is_finished():
            dice_value = game.roll()
            game.play_turn(dice_value)
            turns += 1
        winner = game.winner()
        if winner is None:
            winner = game.recalculate_winner()
        if winner is None:
            return None, turns
        if winner.color == self.home_color:
            return home_entry.display_name, turns
        if winner.color == self.away_color:
            return away_entry.display_name, turns
        return None, turns

    def _play_match(self, home_strategy: str, away_strategy: str) -> MatchResult:
        home_entry = self.strategy_entries[home_strategy]
        away_entry = self.strategy_entries[away_strategy]

        home_game_wins = 0
        away_game_wins = 0
        draw_games = 0
        total_turns = 0

        for _ in range(self.games_per_match):
            game_seed = self._rng.randint(0, 2**31 - 1)
            winner_name, turns = self._run_single_game(
                home_entry, away_entry, seed=game_seed
            )
            total_turns += turns
            if winner_name == home_entry.display_name:
                home_game_wins += 1
            elif winner_name == away_entry.display_name:
                away_game_wins += 1
            else:
                draw_games += 1

        if home_game_wins > away_game_wins:
            winner = home_strategy
            home_points, away_points = 3, 0
            is_draw = False
        elif away_game_wins > home_game_wins:
            winner = away_strategy
            home_points, away_points = 0, 3
            is_draw = False
        else:
            winner = None
            home_points = away_points = 1
            is_draw = True

        average_turns = int(round(total_turns / max(1, self.games_per_match)))

        return MatchResult(
            home_strategy=home_strategy,
            away_strategy=away_strategy,
            home_points=home_points,
            away_points=away_points,
            winner=winner,
            turns_played=average_turns,
            is_draw=is_draw,
            home_game_wins=home_game_wins,
            away_game_wins=away_game_wins,
            draw_games=draw_games,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run_tournament(self, verbose: bool = True) -> Dict[str, TeamStats]:
        self._reset_table()

        if verbose:
            print("🏆 Ludo Strategy Tournament")
            print(f"📊 {len(self.strategy_names)} teams competing")
            print(f"🎮 {self.games_per_match} game(s) per match")
            print("🏠 Home and away format")
            print("=" * 60)

        total_matches = len(self.strategy_names) * (len(self.strategy_names) - 1)
        match_count = 0

        for home_strategy in self.strategy_names:
            for away_strategy in self.strategy_names:
                if home_strategy == away_strategy:
                    continue
                match_count += 1

                if verbose:
                    print(
                        f"Match {match_count}/{total_matches}: {home_strategy} vs {away_strategy}"
                    )

                result = self._play_match(home_strategy, away_strategy)
                self.match_results.append(result)
                self.team_stats[home_strategy].update_stats(result, is_home=True)
                self.team_stats[away_strategy].update_stats(result, is_home=False)

                if verbose:
                    if result.is_draw:
                        print(
                            f"   📊 Draw ({result.home_game_wins}-{result.away_game_wins}"
                            f" with {result.draw_games} draw(s))"
                        )
                    else:
                        print(
                            f"   🏆 {result.winner} wins"
                            f" {result.home_game_wins}-{result.away_game_wins}"
                        )
                    print(f"   ⏱ Average turns: {result.turns_played}")
                    print()

        self.completed = True

        if verbose:
            print("=" * 60)
            print("🏁 Tournament completed!\n")
            self.display_final_table()

        return self.team_stats

    def display_final_table(self) -> None:
        if not self.completed:
            print("⚠️  Tournament not yet completed!")
            return

        sorted_teams = sorted(
            self.team_stats.values(),
            key=lambda x: (x.points, x.goal_difference, x.goals_for, -x.losses),
            reverse=True,
        )

        print("🏆 FINAL LEAGUE TABLE")
        print("=" * 85)
        print(
            f"{'Pos':<3} {'Team':<18} {'P':<3} {'W':<3} {'D':<3} {'L':<3} "
            f"{'GW':<3} {'GL':<3} {'GD':<4} {'Pts':<4} {'Win%':<6}"
        )
        print("-" * 85)

        for pos, team in enumerate(sorted_teams, 1):
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
                f"{pos:<3} {team.strategy_name:<18} {team.games_played:<3} {team.wins:<3} "
                f"{team.draws:<3} {team.losses:<3} {team.goals_for:<3} {team.goals_against:<3} "
                f"{gd_str:<4} {team.points:<4} {team.win_percentage:<6.1f} {position_emoji}"
            )

        print("-" * 85)
        print("Legend: GW/GL=Game Wins/Losses across all matches, GD=Goal Difference")

        champion = sorted_teams[0]
        print(f"\n🏆 CHAMPION: {champion.strategy_name}")
        print(f"   📊 {champion.points} points from {champion.games_played} matches")
        print(f"   🎯 {champion.win_percentage:.1f}% match win rate")

        total_matches = len(self.match_results)
        total_draws = sum(1 for result in self.match_results if result.is_draw)
        total_game_draws = sum(result.draw_games for result in self.match_results)

        print("\n📈 TOURNAMENT STATISTICS:")
        print(f"   🎯 Total matches: {total_matches}")
        print(f"   📊 Match draws: {total_draws}")
        print(f"   🔎 Game-level draws: {total_game_draws}")

        if self.match_results:
            avg_turns = sum(result.turns_played for result in self.match_results) / total_matches
            print(f"   ⏱ Average turns per game: {avg_turns:.1f}")

    def get_head_to_head(
        self, strategy1: str, strategy2: str
    ) -> Dict[str, Union[int, str]]:
        if strategy1 not in self.strategy_names or strategy2 not in self.strategy_names:
            raise ValueError("Both strategies must be in the tournament")

        relevant_matches = [
            result
            for result in self.match_results
            if (result.home_strategy == strategy1 and result.away_strategy == strategy2)
            or (result.home_strategy == strategy2 and result.away_strategy == strategy1)
        ]

        strategy1_match_wins = 0
        strategy2_match_wins = 0
        match_draws = 0
        strategy1_game_wins = 0
        strategy2_game_wins = 0
        game_draws = 0

        for match in relevant_matches:
            if match.is_draw:
                match_draws += 1
            elif match.winner == strategy1:
                strategy1_match_wins += 1
            elif match.winner == strategy2:
                strategy2_match_wins += 1

            if match.home_strategy == strategy1:
                strategy1_game_wins += match.home_game_wins
                strategy2_game_wins += match.away_game_wins
            else:
                strategy1_game_wins += match.away_game_wins
                strategy2_game_wins += match.home_game_wins
            game_draws += match.draw_games

        total_matches = len(relevant_matches)
        total_games = strategy1_game_wins + strategy2_game_wins + game_draws

        return {
            "strategy1": strategy1,
            "strategy2": strategy2,
            "strategy1_match_wins": strategy1_match_wins,
            "strategy2_match_wins": strategy2_match_wins,
            "match_draws": match_draws,
            "strategy1_game_wins": strategy1_game_wins,
            "strategy2_game_wins": strategy2_game_wins,
            "game_draws": game_draws,
            "total_matches": total_matches,
            "total_games": total_games,
        }


def run_sample_tournament() -> LudoTournament:
    """Run a sample tournament with a curated set of strategies."""

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
    print(f"🎯 Strategies: {', '.join(strategies)}\n")

    tournament = LudoTournament(
        strategies=strategies,
        games_per_match=3,
        seed=42,
    )

    tournament.run_tournament(verbose=True)

    print("\n😄 HEAD-TO-HEAD EXAMPLES:")
    h2h = tournament.get_head_to_head("killer", "defensive")
    print(
        f"Killer vs Defensive: {h2h['strategy1_game_wins']} wins / "
        f"{h2h['game_draws']} draws / {h2h['strategy2_game_wins']} losses"
    )

    h2h = tournament.get_head_to_head("probabilistic", "random")
    print(
        f"Probabilistic vs Random: {h2h['strategy1_game_wins']} wins / "
        f"{h2h['game_draws']} draws / {h2h['strategy2_game_wins']} losses"
    )

    return tournament


def run_custom_strategy_tournament() -> LudoTournament:
    """Demonstrate the builder-friendly API with tweaked strategy parameters."""

    weighted_cool = StrategyEntry.from_name(
        "weighted_random",
        display_name="weighted(t=0.5)",
        temperature=0.5,
        epsilon=0.1,
    )
    cautious = StrategyEntry.from_name("cautious")
    killer = StrategyEntry.from_name("killer")
    prob_cool = StrategyEntry.from_name(
        "probabilistic_v2",
        display_name="prob_v2(t=0.7)",
        base_temperature=0.7,
    )

    strategies = [weighted_cool, cautious, killer, prob_cool]

    print("🚀 Running Custom Strategy Tournament")
    print(
        "🎯 Using StrategyEntry objects to tweak builder parameters:\n"
        + ", ".join(entry.display_name for entry in strategies)
    )

    tournament = LudoTournament(
        strategies=strategies,
        games_per_match=5,
        seed=7,
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
