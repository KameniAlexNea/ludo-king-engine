"""
Main Ludo game implementation.
Manages game flow, rules, and provides interface for AI players.
"""

import random
from typing import List, Optional, Union

from ludo_engine.board import Board
from ludo_engine.constants import GameConstants
from ludo_engine.model import (
    AIDecisionContext,
    CapturedToken,
    CurrentSituation,
    MoveResult,
    OpponentInfo,
    PlayerConfiguration,
    StrategicAnalysis,
    TurnResult,
    ValidMove,
)
from ludo_engine.player import Player, PlayerColor


class LudoGame:
    """
    Main Ludo game class that manages the entire game state and flow.

    This class provides comprehensive game management including:
    - Turn-based gameplay with dice rolling
    - Move validation and execution
    - AI player support with strategic decision making
    - Game state tracking and history
    - Flexible reset options that preserve player configurations
    """

    def __init__(self, player_colors: List[PlayerColor]):
        """
        Initialize a new Ludo game.

        Args:
            player_colors: List of colors for players (2-4 players)
        """
        if len(player_colors) < 2 or len(player_colors) > 4:
            raise ValueError("Ludo requires 2-4 players")

        self.board = Board()
        self.players: List[Player] = []

        # Create players
        for i, color in enumerate(player_colors):
            player = Player(color, i)
            self.players.append(player)

        self.current_player_index = 0
        self.game_over = False
        self.winner: Optional[Player] = None
        self.turn_count = 0

        # Game state tracking
        self.consecutive_sixes = 0
        self.last_dice_value = 0
        self.move_history: List[MoveResult] = []

        # Initialize board with all tokens in home
        self._initialize_board()

    def get_player_from_color(self, color: Union[PlayerColor, str]) -> Player:
        if isinstance(color, PlayerColor):
            color = color.value
        return self._player_map[color]

    def _initialize_board(self):
        """Place all tokens in their starting home positions."""
        for player in self.players:
            for token in player.tokens:
                token.position = GameConstants.HOME_POSITION

        self._player_map = {player.color.value: player for player in self.players}

    def get_current_player(self) -> Player:
        """Get the player whose turn it is."""
        return self.players[self.current_player_index]

    def roll_dice(self) -> int:
        """Roll a six-sided die and return the result."""
        dice_value = random.randint(1, 6)
        self.last_dice_value = dice_value

        # Track consecutive sixes
        if dice_value == 6:
            self.consecutive_sixes += 1
        else:
            self.consecutive_sixes = 0

        return dice_value

    def can_player_move(self, player: Player, dice_value: int) -> bool:
        """Check if a player can make any move with the given dice value."""
        return player.can_move_any_token(dice_value)

    def get_valid_moves(self, player: Player, dice_value: int) -> List[ValidMove]:
        """
        Get all valid moves for a player with the given dice value.

        Returns:
            List[ValidMove]: List of valid moves with detailed information
        """
        if self.consecutive_sixes >= 3:
            # Player loses turn after 3 consecutive sixes
            self.consecutive_sixes = 0
            return []

        possible_moves = player.get_possible_moves(dice_value)
        valid_moves = []

        for move in possible_moves:
            token = player.tokens[move.token_id]
            target_position = move.target_position

            # Check if the move is actually valid on the board
            can_move, tokens_to_capture = self.board.can_move_to_position(
                token, target_position
            )

            if can_move:
                captured_tokens = [
                    CapturedToken(player_color=t.player_color, token_id=t.token_id)
                    for t in tokens_to_capture
                ]

                valid_move = ValidMove(
                    token_id=move.token_id,
                    current_position=move.current_position,
                    current_state=move.current_state,
                    target_position=target_position,
                    move_type=move.move_type,
                    is_safe_move=move.is_safe_move,
                    captures_opponent=len(tokens_to_capture) > 0,
                    captured_tokens=captured_tokens,
                    strategic_value=move.strategic_value,
                    strategic_components=move.strategic_components,
                )
                valid_moves.append(valid_move)

        return valid_moves

    def execute_move(
        self, player: Player, token_id: int, dice_value: int
    ) -> MoveResult:
        """
        Execute a move for a player.

        Args:
            player: The player making the move
            token_id: ID of the token to move (0-3)
            dice_value: The dice value used for the move

        Returns:
            MoveResult: Result of the move including any captures, extra turns, etc.
        """
        if token_id < 0 or token_id >= 4:
            return MoveResult(
                success=False,
                player_color=player.color.value,
                token_id=token_id,
                dice_value=dice_value,
                old_position=-1,
                new_position=-1,
                captured_tokens=[],
                finished_token=False,
                extra_turn=False,
                error="Invalid token ID",
            )

        token = player.tokens[token_id]

        # Check if move is valid
        if not token.can_move(dice_value):
            return MoveResult(
                success=False,
                player_color=player.color.value,
                token_id=token_id,
                dice_value=dice_value,
                old_position=token.position,
                new_position=token.position,
                captured_tokens=[],
                finished_token=False,
                extra_turn=False,
                error="Token cannot move with this dice value",
            )

        old_position = token.position
        target_position = token.get_target_position(dice_value, player.start_position)

        if target_position == token.position:
            return MoveResult(
                success=False,
                player_color=player.color.value,
                token_id=token_id,
                dice_value=dice_value,
                old_position=old_position,
                new_position=old_position,
                captured_tokens=[],
                finished_token=False,
                extra_turn=False,
                error="Invalid target position",
            )

        # Validate board occupancy / capture
        can_move, tokens_to_capture = self.board.can_move_to_position(
            token, target_position
        )
        if not can_move:
            return MoveResult(
                success=False,
                player_color=player.color.value,
                token_id=token_id,
                dice_value=dice_value,
                old_position=old_position,
                new_position=old_position,
                captured_tokens=[],
                finished_token=False,
                extra_turn=False,
                error="Invalid move - position blocked",
            )

        # Apply board side-effects (captures & relocation) first
        captured_tokens = self.board.execute_move(token, old_position, target_position)

        # Now commit token internal state without recomputation
        token.commit_move(target_position, player.start_position)

        # Create move result
        captured_token_objects = [
            CapturedToken(player_color=t.player_color, token_id=t.token_id)
            for t in captured_tokens
        ]

        # Check for extra turn conditions
        extra_turn = False

        # Rolling a 6 gives extra turn
        if dice_value == 6:
            extra_turn = True

        # Capturing opponent gives extra turn
        if captured_tokens:
            extra_turn = True

        # Finishing a token gives extra turn
        if token.is_finished():
            extra_turn = True

        # But not if player rolled 3 sixes in a row
        if self.consecutive_sixes >= 3:
            extra_turn = False

        move_result = MoveResult(
            success=True,
            player_color=player.color.value,
            token_id=token_id,
            dice_value=dice_value,
            old_position=old_position,
            new_position=token.position,
            captured_tokens=captured_token_objects,
            finished_token=token.is_finished(),
            extra_turn=extra_turn,
        )

        # Record move in history
        self.move_history.append(move_result)

        # Check for game over
        if player.has_won():
            self.game_over = True
            self.winner = player
            move_result.game_won = True

        return move_result

    def next_turn(self):
        """Move to the next player's turn."""
        self.consecutive_sixes = 0  # Reset when changing players
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.turn_count += 1

    def play_turn(
        self, token_id: Optional[int] = None, dice_value: Optional[int] = None
    ) -> TurnResult:
        """
        Play a complete turn for the current player.

        Args:
            token_id: If provided, move this specific token. Otherwise, use AI/random selection.

        Returns:
            TurnResult: Complete turn result
        """
        if self.game_over:
            return TurnResult(
                player_color=self.get_current_player().color.value,
                dice_value=0,
                consecutive_sixes=0,
                moves=[],
                extra_turn=False,
                turn_ended=True,
                error="Game is already over",
            )

        current_player = self.get_current_player()
        if dice_value is None:
            dice_value = self.roll_dice()

        turn_result = TurnResult(
            player_color=current_player.color.value,
            dice_value=dice_value,
            consecutive_sixes=self.consecutive_sixes,
            moves=[],
            extra_turn=False,
            turn_ended=False,
        )

        # Check for 3 consecutive sixes
        if self.consecutive_sixes >= 3:
            turn_result.turn_ended = True
            turn_result.reason = "Three consecutive sixes - turn forfeited"
            self.next_turn()
            return turn_result

        # Get valid moves
        valid_moves = self.get_valid_moves(current_player, dice_value)

        if not valid_moves:
            turn_result.turn_ended = dice_value != 6
            turn_result.extra_turn = dice_value == 6
            turn_result.reason = "No valid moves available"
            if dice_value != 6:
                self.next_turn()
            return turn_result

        # Select move (use provided token_id or first available)
        if token_id is not None:
            # Find the move for the specified token
            selected_move = None
            for move in valid_moves:
                if move.token_id == token_id:
                    selected_move = move
                    break

            if not selected_move:
                turn_result.error = f"Token {token_id} cannot move"
                self.next_turn()
                return turn_result
        else:
            # Select first available move (can be enhanced with AI logic)
            selected_move = valid_moves[0]

        # Execute the move
        move_result = self.execute_move(
            current_player, selected_move.token_id, dice_value
        )
        turn_result.moves.append(move_result)

        if not move_result.success:
            turn_result.error = move_result.error
            self.next_turn()
            return turn_result

        # Check if player gets extra turn
        if move_result.extra_turn:
            turn_result.extra_turn = True
        else:
            turn_result.turn_ended = True
            self.next_turn()

        return turn_result

    def play_game(self, max_turns: int):
        """
        Play the game until max_turns or a player wins.

        Yields the TurnResult for each turn played.

        Args:
            max_turns: Maximum number of turns to play

        Yields:
            TurnResult: The result of each turn
        """
        while not self.game_over and self.turn_count < max_turns:
            current_player = self.get_current_player()
            # Use AI strategy to select the best token to move
            dice_value = self.roll_dice()
            valid = self.get_valid_moves(current_player, dice_value)
            if not valid:
                continue
            selected_token_id = current_player.make_strategic_decision(
                self.get_ai_decision_context(dice_value)
            )
            # Play the turn with the selected token
            turn_result = self.play_turn(
                token_id=selected_token_id, dice_value=dice_value
            )
            yield turn_result

    def get_ai_decision_context(self, dice_value: int) -> AIDecisionContext:
        """
        Get context specifically designed for AI decision making.

        Args:
            dice_value: The dice value rolled

        Returns:
            AIDecisionContext: AI decision context
        """
        current_player = self.get_current_player()
        valid_moves = self.get_valid_moves(current_player, dice_value)

        current_situation = CurrentSituation(
            player_color=current_player.color.value,
            dice_value=dice_value,
            consecutive_sixes=self.consecutive_sixes,
            turn_count=self.turn_count,
        )

        player_state = current_player.get_game_state()

        opponents = [
            OpponentInfo(
                color=p.color.value,
                finished_tokens=p.get_finished_tokens_count(),
                tokens_active=sum(1 for t in p.tokens if t.is_active()),
                threat_level=self._calculate_threat_level(p),
                positions_occupied=p.player_positions(),
            )
            for p in self.players
            if p != current_player
        ]

        strategic_analysis = self._analyze_strategic_situation(
            current_player, valid_moves
        )

        return AIDecisionContext(
            current_situation=current_situation,
            player_state=player_state,
            opponents=opponents,
            valid_moves=valid_moves,
            strategic_analysis=strategic_analysis,
        )

    def _calculate_threat_level(self, player: Player) -> float:
        """Calculate how much of a threat a player is (0.0 to 1.0)."""
        finished_tokens = player.get_finished_tokens_count()
        active_tokens = sum(1 for token in player.tokens if not token.is_in_home())

        # Higher threat if more tokens are finished or close to finishing
        threat = (finished_tokens * 0.4) + (active_tokens * 0.1)
        return min(threat, 1.0)

    def _analyze_strategic_situation(
        self, player: Player, valid_moves: List[ValidMove]
    ) -> StrategicAnalysis:
        """Analyze the strategic situation for AI decision making."""
        can_capture = any(move.captures_opponent for move in valid_moves)
        can_finish_token = any(move.move_type == "finish" for move in valid_moves)
        can_exit_home = any(move.move_type == "exit_home" for move in valid_moves)
        safe_moves = [move for move in valid_moves if move.is_safe_move]
        risky_moves = [move for move in valid_moves if not move.is_safe_move]

        best_strategic_move = None
        if valid_moves:
            best_strategic_move = max(valid_moves, key=lambda m: m.strategic_value)

        return StrategicAnalysis(
            can_capture=can_capture,
            can_finish_token=can_finish_token,
            can_exit_home=can_exit_home,
            safe_moves=safe_moves,
            risky_moves=risky_moves,
            best_strategic_move=best_strategic_move,
        )

    def get_player_configurations(self) -> List[PlayerConfiguration]:
        """
        Get current player configurations including strategies.
        Useful for saving and restoring game setups.

        Returns:
            List[PlayerConfiguration]: Player configurations
        """
        configs = []
        for player in self.players:
            config = PlayerConfiguration(
                color=player.color.value,
                player_id=player.player_id,
                strategy_name=player.get_strategy_name(),
                strategy_description=player.get_strategy_description(),
                has_strategy=player.strategy is not None,
                finished_tokens=player.get_finished_tokens_count(),
                tokens_active=sum(1 for t in player.tokens if t.is_active()),
                tokens_in_home=sum(1 for t in player.tokens if t.is_in_home()),
            )
            configs.append(config)
        return configs

    def __str__(self) -> str:
        """String representation of the current game state."""
        current_player = self.get_current_player()
        result = f"Ludo Game - Turn {self.turn_count}\n"
        result += f"Current Player: {current_player.color.value}\n"
        result += f"Game Over: {self.game_over}\n"
        if self.winner:
            result += f"Winner: {self.winner.color.value}\n"
        result += "\nPlayer States:\n"
        for player in self.players:
            result += f"  {player.color.value}: {player.get_finished_tokens_count()}/4 finished\n"
        return result
