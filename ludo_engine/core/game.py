"""
Main Ludo game engine implementation.

This module contains the core game logic that orchestrates the entire
Ludo game flow, including turn management, rule enforcement, and game state.
"""

import random
from typing import List, Optional

from ..strategies.factory import StrategyFactory
from .board import Board
from .model import GameResults, GameStateData, GameStatus, TokenInfo, TurnResult
from .player import Player


class LudoGame:
    """
    Main Ludo game engine.

    Manages the complete game flow including players, board state,
    turn management, and rule enforcement.
    """

    def __init__(
        self,
        player_colors: List[str] = None,
        strategies: List[str] = None,
        seed: Optional[int] = None,
    ):
        """
        Initialize a new Ludo game.

        Args:
            player_colors: List of colors for players (default: ['red', 'blue', 'green', 'yellow'])
            strategies: List of strategy names for each player (default: all 'random')
            seed: Random seed for deterministic gameplay
        """
        # Set random seed for deterministic gameplay
        if seed is not None:
            random.seed(seed)

        # Default player setup
        if player_colors is None:
            player_colors = ["red", "blue", "green", "yellow"]
        if strategies is None:
            strategies = ["random"] * len(player_colors)

        # Validate inputs
        if len(player_colors) != len(strategies):
            raise ValueError("Number of players and strategies must match")
        if len(player_colors) < 2 or len(player_colors) > 4:
            raise ValueError("Game supports 2-4 players")

        # Initialize game components
        self.board = Board()
        self.players = self._create_players(player_colors, strategies)
        self.current_player_index = 0
        self.game_state = GameStatus.NOT_STARTED

        # Game statistics
        self.turn_count = 0
        self.total_moves = 0
        self.game_history = []
        self.dice_rolls = []

        # Game rules
        self.max_consecutive_sixes = 3
        self.sixes_in_row = 0

    def _create_players(
        self, colors: List[str], strategy_names: List[str]
    ) -> List[Player]:
        """Create player instances with strategies."""
        players = []
        for i, (color, strategy_name) in enumerate(zip(colors, strategy_names)):
            strategy = StrategyFactory.create_strategy(strategy_name)
            if strategy is None:
                strategy = StrategyFactory.create_strategy("random")
            player = Player(color, f"Player_{i + 1}", strategy)
            players.append(player)
        return players

    def start_game(self):
        """Start the game."""
        if self.game_state != GameStatus.NOT_STARTED:
            raise RuntimeError("Game has already been started")

        self.game_state = GameStatus.IN_PROGRESS
        self._place_all_tokens()

    def _place_all_tokens(self):
        """Place all player tokens in their initial positions."""
        for player in self.players:
            for token in player.tokens:
                # Tokens start at home (position -1, not on board)
                token.send_home()

    def get_current_player(self) -> Player:
        """Get the player whose turn it is."""
        return self.players[self.current_player_index]

    def roll_dice(self) -> int:
        """Roll the dice and return result."""
        dice_result = random.randint(1, 6)
        self.dice_rolls.append(dice_result)
        return dice_result

    def play_turn(self) -> TurnResult:
        """
        Play a complete turn for the current player.

        Returns:
            TurnResult containing turn results
        """
        if self.game_state != GameStatus.IN_PROGRESS:
            raise RuntimeError("Game is not in progress")

        current_player = self.get_current_player()
        turn_result = TurnResult(
            player=current_player.color,
            dice_roll=None,
            move_made=False,
            token_moved=None,
            captured_tokens=[],
            finished_tokens=0,
            another_turn=False,
            game_finished=False,
            winner=None,
        )

        # Roll dice
        dice_roll = self.roll_dice()
        turn_result.dice_roll = dice_roll

        # Handle consecutive sixes
        if dice_roll == 6:
            self.sixes_in_row += 1
        else:
            self.sixes_in_row = 0

        # Check for max consecutive sixes rule
        if self.sixes_in_row >= self.max_consecutive_sixes:
            self.sixes_in_row = 0
            self._next_player()
            return turn_result

        # Check if player can make a move
        if not current_player.can_make_move(dice_roll):
            # No valid moves, turn ends
            if dice_roll != 6:
                self._next_player()
            return turn_result

        # Let player choose a move
        game_state = self.get_game_state()
        chosen_token = current_player.choose_move(dice_roll, game_state)

        if chosen_token:
            # Execute the move
            success, captured_tokens = self.board.move_token(chosen_token, dice_roll)

            if success:
                turn_result.move_made = True
                # Create TokenInfo directly from token attributes
                turn_result.token_moved = TokenInfo(
                    id=chosen_token.token_id,
                    color=chosen_token.color,
                    position=chosen_token.position,
                    steps_taken=chosen_token.steps_taken,
                    is_finished=chosen_token.state.value == "finished",
                    is_at_home=chosen_token.state.value == "home",
                )
                turn_result.captured_tokens = []
                for captured_token in captured_tokens:
                    turn_result.captured_tokens.append(
                        TokenInfo(
                            id=captured_token.token_id,
                            color=captured_token.color,
                            position=captured_token.position,
                            steps_taken=captured_token.steps_taken,
                            is_finished=captured_token.state.value == "finished",
                            is_at_home=captured_token.state.value == "home",
                        )
                    )

                # Update player statistics
                current_player.update_stats(dice_roll, True, captured_tokens)
                self.total_moves += 1

                # Check if any tokens finished
                finished_count = len(current_player.get_finished_tokens())
                turn_result.finished_tokens = finished_count

                # Check for game end
                if current_player.has_won():
                    self.game_state = GameStatus.FINISHED
                    turn_result.game_finished = True
                    turn_result.winner = current_player.color

        # Determine if player gets another turn (rolled 6 or captured token)
        another_turn = dice_roll == 6 or len(turn_result.captured_tokens) > 0
        turn_result.another_turn = another_turn

        if not another_turn:
            self._next_player()

        # Record turn in history
        self.game_history.append(turn_result)
        self.turn_count += 1

        return turn_result

    def _next_player(self):
        """Move to the next player's turn."""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def play_game(self, max_turns: Optional[int] = None) -> GameResults:
        """
        Play a complete game until finished or max turns reached.

        Args:
            max_turns: Maximum number of turns to play (None for no limit)

        Returns:
            GameResults containing final game results
        """
        if self.game_state == GameStatus.NOT_STARTED:
            self.start_game()

        turns_played = 0

        while self.game_state == GameStatus.IN_PROGRESS and (
            max_turns is None or turns_played < max_turns
        ):
            turn_result = self.play_turn()
            turns_played += 1

            if turn_result.game_finished:
                break

        return self.get_game_results()

    def get_game_state(self) -> GameStateData:
        """Get the current complete game state."""
        return GameStateData(
            board=self.board.get_board_state(),
            players=[player.get_stats() for player in self.players],
            current_player=self.current_player_index,
            turn_count=self.turn_count,
            game_status=self.game_state,
            sixes_in_row=self.sixes_in_row,
        )

    def get_game_results(self) -> GameResults:
        """Get final game results and statistics."""
        from .model import FinalPosition

        results = GameResults(
            winner=self.board.get_winner(),
            game_status=self.game_state,
            turns_played=self.turn_count,
            total_moves=self.total_moves,
            dice_rolls=len(self.dice_rolls),
            player_stats=[player.get_stats() for player in self.players],
            final_positions={},
        )

        # Calculate final positions
        for i, player in enumerate(self.players):
            finished_tokens = len(player.get_finished_tokens())
            results.final_positions[player.color] = FinalPosition(
                rank=i + 1,  # Will be updated based on finished tokens
                tokens_finished=finished_tokens,
                total_moves=player.total_moves,
            )

        return results

    def reset_game(self):
        """Reset the game to initial state."""
        self.board = Board()
        self.current_player_index = 0
        self.game_state = GameStatus.NOT_STARTED
        self.turn_count = 0
        self.total_moves = 0
        self.game_history = []
        self.dice_rolls = []
        self.sixes_in_row = 0

        # Reset all players
        for player in self.players:
            player.reset()

    def is_finished(self) -> bool:
        """Check if the game is finished."""
        return self.game_state == GameStatus.FINISHED

    def get_winner(self) -> Optional[str]:
        """Get the winner of the game."""
        if self.is_finished():
            return self.board.get_winner()
        return None

    def __repr__(self) -> str:
        """String representation of the game."""
        return (
            f"LudoGame(players={len(self.players)}, "
            f"state={self.game_state.value}, "
            f"turn={self.turn_count})"
        )
