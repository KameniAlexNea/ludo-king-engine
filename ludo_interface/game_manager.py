from __future__ import annotations

from typing import Dict, List, Optional, Sequence

from ludo_engine import Game, Token
from ludo_engine.board import MoveResult
from ludo_engine.constants import CONFIG
from ludo_engine.game import Decision
from ludo_engine.player import Player
from ludo_engine_strategies import build_strategy


class GameManager:
    """Handles core game logic and state management."""

    def __init__(self, default_players: List[str], show_token_ids: bool):
        self.default_players = default_players
        self.show_token_ids = show_token_ids

    def init_game(self, strategies: List[str]) -> Game:
        """Initializes a new game and assigns strategies by player color.

        "human" is treated as an interface-only strategy handled by the UI.
        """
        game = Game(players=[Player(color) for color in self.default_players])

        interface_strategy_names = {
            player.color: strategies[i] if i < len(strategies) else "random"
            for i, player in enumerate(game.players)
        }
        setattr(game, "_interface_strategy_names", interface_strategy_names)

        for player in game.players:
            chosen = interface_strategy_names.get(player.color, "random")
            if chosen == "human":
                continue
            game.strategies[player.color] = build_strategy(chosen, game)

        return game

    def game_state_tokens(self, game: Game) -> Dict[str, List[Token]]:
        """Extracts token information from the game state."""
        token_map: Dict[str, List[Token]] = {c: [] for c in self.default_players}
        for player in game.players:
            token_map.setdefault(player.color, []).extend(player.tokens)
        return token_map

    def is_human_turn(self, game: Game) -> bool:
        names = getattr(game, "_interface_strategy_names", {})
        return names.get(game.current_player.color) == "human"

    def get_human_move_options(self, game: Game, dice: int) -> List[dict]:
        current_player = game.current_player
        moves = game.available_moves(current_player, dice)
        options: List[dict] = []
        for action, token_index in moves:
            token = current_player.tokens[token_index]
            target = self._predict_target_index(
                player_color=current_player.color,
                token=token,
                action=action,
                dice=dice,
            )
            target_text = (
                "finish"
                if target is None and self._would_finish(token, action, dice)
                else target
            )
            options.append(
                {
                    "token_id": token_index,
                    "description": f"Token {token_index}: {action} -> {target_text}",
                    "move_type": action,
                }
            )
        return options

    def _would_finish(self, token: Token, action: str, dice: int) -> bool:
        if action != "advance":
            return False
        return token.steps_taken + dice == CONFIG.total_steps

    def _predict_target_index(
        self, *, player_color: str, token: Token, action: str, dice: int
    ) -> Optional[int]:
        if action == "enter":
            return CONFIG.start_offsets[player_color]
        if action != "advance":
            return None

        target_steps = token.steps_taken + dice
        if target_steps == CONFIG.total_steps:
            return None
        if target_steps >= CONFIG.travel_distance:
            home_offset = target_steps - CONFIG.travel_distance
            return CONFIG.home_index(player_color, home_offset)
        start = CONFIG.start_offsets[player_color]
        return (start + target_steps) % CONFIG.track_size

    def serialize_move(self, move_result: MoveResult) -> str:
        """Serializes a move result into a human-readable string."""
        if not move_result or not move_result.valid:
            return "No move"
        token = move_result.token
        start = move_result.start
        end = move_result.end

        parts = [f"{token.color} token {token.index}"]
        if start is None and end is not None:
            parts.append(f"entered -> {end}")
        elif end is None and move_result.finished:
            parts.append("finished")
        else:
            parts.append(f"{start} -> {end}")

        if move_result.captured is not None:
            parts.append(f"captured {move_result.captured.color}")

        earned_extra_turn = False
        if move_result.valid:
            earned_extra_turn = (
                getattr(self, "_last_roll", None) == 6
                or move_result.captured is not None
                or move_result.finished
            )
        if earned_extra_turn:
            parts.append("extra turn")
        return ", ".join(parts)

    def play_step(
        self,
        game: Game,
        human_move_choice: Optional[int] = None,
        dice: Optional[int] = None,
    ):
        """Plays a single step of the game.

        If `dice` is provided, use it; otherwise roll a new dice value.
        """
        if game.is_finished():
            winner = game.winner()
            winner_text = winner.color if winner else "unknown"
            return (
                game,
                f"Game over (winner: {winner_text})",
                self.game_state_tokens(game),
                [],
                False,
            )

        current_player = game.current_player
        if dice is None:
            dice = game.roll()
        self._last_roll = dice

        if self.is_human_turn(game):
            moves = game.available_moves(current_player, dice)
            if moves and human_move_choice is None:
                setattr(game, "_interface_pending_dice", dice)
                move_options = self.get_human_move_options(game, dice)
                desc = f"{current_player.color} rolled {dice} - Choose your move:"
                return game, desc, self.game_state_tokens(game), move_options, True

            # Resolve the turn using the chosen token (or default) and advance.
            if not moves:
                move_res = game.play_turn(dice)
            else:
                decision = self._pick_decision(moves, human_move_choice)
                move_res = game.execute(current_player, decision, dice)
                game.recalculate_winner()
                self._advance_turn(game, dice, move_res)
        else:
            move_res = game.play_turn(dice)

        # Turn resolved; pending dice no longer applies.
        setattr(game, "_interface_pending_dice", None)

        desc = f"{current_player.color} rolled {dice}: {self.serialize_move(move_res)}"
        if game.is_finished():
            winner = game.winner()
            if winner:
                desc += f" | WINNER: {winner.color}"

        return game, desc, self.game_state_tokens(game), [], False

    def _pick_decision(
        self, moves: Sequence[Decision], token_choice: Optional[int]
    ) -> Decision:
        if token_choice is None:
            return moves[0]
        for decision in moves:
            if decision[1] == token_choice:
                return decision
        return moves[0]

    def _advance_turn(self, game: Game, dice_value: int, result: MoveResult) -> None:
        if not result.valid:
            game.current_player_index = (game.current_player_index + 1) % len(
                game.players
            )
            return

        earned_extra_turn = (
            dice_value == 6 or result.captured is not None or result.finished
        )
        if earned_extra_turn:
            return
        game.current_player_index = (game.current_player_index + 1) % len(game.players)
