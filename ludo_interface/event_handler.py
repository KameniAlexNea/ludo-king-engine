import json
import random
import time

import gradio as gr

from ludo_engine.game import LudoGame
from ludo_engine.player import PlayerColor
from ludo_interface.board_viz import draw_board

from .game_manager import GameManager
from .utils import Utils


class EventHandler:
    """Handles UI event callbacks and interactions."""

    def __init__(
        self,
        game_manager: GameManager,
        utils: Utils,
        ai_strategies: list[str],
        default_players: list[PlayerColor],
        show_token_ids: bool,
    ):
        self.game_manager = game_manager
        self.utils = utils
        self.ai_strategies = ai_strategies
        self.default_players = default_players
        self.show_token_ids = show_token_ids

    def _ui_init(self, *strats):
        game = self.game_manager.init_game(list(strats))
        pil_img = draw_board(
            self.game_manager.game_state_tokens(game), show_ids=self.show_token_ids
        )
        html = self.utils.img_to_data_uri(pil_img)

        current_player = game.get_current_player()
        player_html = f"<h3 style='color: {current_player.color.value};'>🎯 Current Player: {current_player.color.value.title()}</h3>"

        has_human = any(s == "human" for s in strats)
        controls_visible = has_human and self.game_manager.is_human_turn(game)

        return (
            game,
            html,
            "🎮 Game initialized! Roll the dice to start.",
            [],
            {"games": 0, "wins": {c.value: 0 for c in self.default_players}},
            player_html,
            gr.update(visible=controls_visible),
            "",
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            [],
            None,  # reset pending_dice
            None,  # reset selected_token_id
            0,  # auto_steps_remaining
            0.5,  # auto_delay_state default
        )

    def _ui_random_strategies(self):
        strategies = [s for s in self.ai_strategies if s != "human"]
        return [random.choice(strategies) for _ in range(len(self.default_players))]

    def _ui_steps(
        self, game, history: list[str], show, pending_dice, human_choice=None
    ):
        if game is None:
            return (
                None,
                None,
                "No game initialized",
                history,
                False,
                "",
                "",
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                [],
                None,  # pending_dice
                None,  # selected_token_id
                0,  # auto_steps_remaining
                None,  # auto_delay_state
            )

        game, desc, tokens, move_opts, waiting = self.game_manager.play_step(
            game, human_choice, pending_dice
        )
        history.append(desc)
        if len(history) > 50:
            history = history[-50:]

        pil_img = draw_board(tokens, show_ids=show)
        html = self.utils.img_to_data_uri(pil_img)

        if not game.game_over:
            current_player = game.get_current_player()
            player_html = f"<h3 style='color: {current_player.color.value};'>🎯 Current Player: {current_player.color.value.title()}</h3>"
        else:
            player_html = f"<h3>🏆 Winner: {game.winner.color.value.title()}!</h3>"

        if waiting and move_opts:
            moves_html = (
                "<h4>Choose your move:</h4><ul>"
                + "".join(
                    [
                        f"<li><strong>Token {opt['token_id']}</strong>: {opt['description']} ({opt['move_type']})</li>"
                        for opt in move_opts
                    ]
                )
                + "</ul>"
            )
            btn_updates = [
                gr.update(
                    visible=i < len(move_opts),
                    value=(
                        f"Move Token {move_opts[i]['token_id']}"
                        if i < len(move_opts)
                        else ""
                    ),
                )
                for i in range(4)
            ]
            # keep pending_dice if we're still waiting (it may be provided from auto-play)
            next_pending_dice = pending_dice
            return (
                game,
                html,
                desc,
                history,
                waiting,
                player_html,
                moves_html,
                gr.update(visible=True),
                *btn_updates,
                move_opts,
                next_pending_dice,  # pending_dice
                None,  # selected_token_id
                0,  # auto_steps_remaining (manual step path)
                None,  # auto_delay_state
            )
        else:
            # clear pending_dice and selected_token_id after the turn resolves
            return (
                game,
                html,
                desc,
                history,
                False,
                player_html,
                "",
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                [],
                None,  # pending_dice
                None,  # selected_token_id
                0,  # auto_steps_remaining
                None,  # auto_delay_state
            )

    def _ui_run_auto(self, n, delay, game: LudoGame, history: list[str], show: bool):
        if game is None:
            yield (
                None,
                None,
                "No game",
                history,
                False,
                "",
                "",
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                [],
                None,  # pending_dice
                None,  # selected_token_id
                0,  # auto_steps_remaining
                delay,  # auto_delay_state
            )
            return

        desc = ""
        remaining = int(n)
        for _ in range(int(n)):
            if self.game_manager.is_human_turn(game):
                current_player = game.get_current_player()
                dice = game.roll_dice()
                valid_moves = game.get_valid_moves(current_player, dice)

                if valid_moves:
                    pil_img = draw_board(
                        self.game_manager.game_state_tokens(game), show_ids=show
                    )
                    html = self.utils.img_to_data_uri(pil_img)
                    player_html = f"<h3 style='color: {current_player.color.value};'>🎯 Current Player: {current_player.color.value.title()}</h3>"
                    desc = f"Auto-play paused: {current_player.color.value} rolled {dice} - Choose your move:"
                    history.append(desc)
                    if len(history) > 50:
                        history = history[-50:]

                    move_options = self.game_manager.get_human_move_options(game, dice)
                    moves_html = (
                        "<h4>Choose your move:</h4><ul>"
                        + "".join(
                            [
                                f"<li><strong>Token {opt['token_id']}</strong>: {opt['description']} ({opt['move_type']})</li>"
                                for opt in move_options
                            ]
                        )
                        + "</ul>"
                    )
                    btn_updates = [
                        gr.update(
                            visible=i < len(move_options),
                            value=(
                                f"Move Token {move_options[i]['token_id']}"
                                if i < len(move_options)
                                else ""
                            ),
                        )
                        for i in range(4)
                    ]

                    # set pending_dice to the rolled value and pause for human
                    remaining_after_pause = max(remaining - 1, 0)
                    yield (
                        game,
                        html,
                        desc,
                        history,
                        True,
                        player_html,
                        moves_html,
                        gr.update(visible=True),
                        *btn_updates,
                        move_options,
                        dice,  # pending_dice
                        None,  # selected_token_id
                        remaining_after_pause,  # auto_steps_remaining
                        delay,  # auto_delay_state
                    )
                    return
                else:
                    extra_turn = dice == 6
                    if not extra_turn:
                        game.next_turn()
                    desc = f"{current_player.color.value} rolled {dice} - no moves{' (extra turn)' if extra_turn else ''}"
                    history.append(desc)
                    if len(history) > 50:
                        history = history[-50:]
                    remaining = max(remaining - 1, 0)
            else:
                game, step_desc, _, _, _ = self.game_manager.play_step(game)
                desc = step_desc
                history.append(step_desc)
                if len(history) > 50:
                    history = history[-50:]
                remaining = max(remaining - 1, 0)

            pil_img = draw_board(
                self.game_manager.game_state_tokens(game), show_ids=show
            )
            html = self.utils.img_to_data_uri(pil_img)

            if not game.game_over:
                current_player = game.get_current_player()
                player_html = f"<h3 style='color: {current_player.color.value};'>🎯 Current Player: {current_player.color.value.title()}</h3>"
            else:
                player_html = f"<h3>🏆 Winner: {game.winner.color.value.title()}!</h3>"

            waiting = self.game_manager.is_human_turn(game) and not game.game_over
            # clear pending_dice while continuing auto-play (no human pause)
            yield (
                game,
                html,
                desc,
                history,
                waiting,
                player_html,
                "",
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                [],
                None,  # pending_dice
                None,  # selected_token_id
                remaining,  # auto_steps_remaining
                delay,  # auto_delay_state
            )

            if game.game_over:
                break
            if delay and delay > 0 and not waiting:
                time.sleep(float(delay))

    def _ui_make_human_move(
        self,
        token_id,
        game,
        history,
        show,
        move_opts,
        pending_dice,
        auto_steps_remaining,
        auto_delay_state,
    ):
        if not move_opts:
            return (
                game,
                None,
                "No moves available",
                history,
                False,
                "",
                "",
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                [],
                pending_dice,  # pending_dice
                None,  # selected_token_id
                auto_steps_remaining,  # auto_steps_remaining
                auto_delay_state,  # auto_delay_state
            )
        # Use the pending_dice from auto-play to execute the human's chosen move
        out = list(self._ui_steps(game, history, show, pending_dice, token_id))
        # out shape: [..., move_options, pending_dice, selected_token_id, auto_steps_remaining, auto_delay_state]
        if len(out) >= 17:
            out[-2] = auto_steps_remaining
            out[-1] = auto_delay_state
        return tuple(out)

    def _ui_resume_auto(
        self, remaining, delay, game: LudoGame, history: list[str], show: bool
    ):
        try:
            rem = int(remaining) if remaining is not None else 0
        except Exception:
            rem = 0
        if rem <= 0 or game is None:
            # No resume needed; return a snapshot without changing states
            if game is not None:
                pil_img = draw_board(
                    self.game_manager.game_state_tokens(game), show_ids=show
                )
                html = self.utils.img_to_data_uri(pil_img)
                if not game.game_over:
                    current_player = game.get_current_player()
                    player_html = f"<h3 style='color: {current_player.color.value};'>🎯 Current Player: {current_player.color.value.title()}</h3>"
                else:
                    player_html = (
                        f"<h3>🏆 Winner: {game.winner.color.value.title()}!</h3>"
                    )
            else:
                html = None
                player_html = ""
            return (
                game,
                html,
                "",
                history,
                bool(
                    game
                    and self.game_manager.is_human_turn(game)
                    and not game.game_over
                ),
                player_html,
                "",
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                [],
                None,  # pending_dice
                None,  # selected_token_id
                0,  # auto_steps_remaining
                delay,  # auto_delay_state
            )
        # Resume by delegating to _ui_run_auto
        for out in self._ui_run_auto(rem, delay, game, history, show):
            yield out

    def _ui_export(self, game: LudoGame):
        if not game:
            return "No game"
        state_dict = {
            "current_turn": game.current_player_index,
            "tokens": {
                k: [v.to_dict() for v in vs]
                for k, vs in self.game_manager.game_state_tokens(game).items()
            },
            "game_over": game.game_over,
            "winner": game.winner.color.value if game.winner else None,
        }
        return json.dumps(state_dict, indent=2)

    def _ui_run_bulk(self, n_games, *strats):
        ai_strats = [s if s != "human" else "random" for s in strats]
        win_counts = {c.value: 0 for c in self.default_players}
        for _ in range(int(n_games)):
            g = self.game_manager.init_game(list(ai_strats))
            while not g.game_over:
                g, _, _, _, _ = self.game_manager.play_step(g)
            if g.winner:
                win_counts[g.winner.color.value] += 1
        total = sum(win_counts.values()) or 1
        summary = {
            k: {"wins": v, "win_rate": round(v / total, 3)}
            for k, v in win_counts.items()
        }
        return json.dumps(summary, indent=2)

    def _ui_update_stats(self, stats, game: LudoGame):
        if game and game.game_over and game.winner:
            stats = dict(stats)
            stats["games"] += 1
            stats["wins"][game.winner.color.value] += 1
        return stats
