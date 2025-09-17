import os
from typing import Dict, List, Optional

os.environ.setdefault("GRADIO_TEMP_DIR", os.path.join(os.getcwd(), "gradio_runtime"))
os.environ.setdefault(
    "GRADIO_CACHE_DIR",
    os.path.join(os.getcwd(), "gradio_runtime", "cache"),
)

import base64
import io
import json
import time
import random

import gradio as gr

from ludo_engine.game import LudoGame
from ludo_engine.token import Token
from ludo_engine.player import PlayerColor
from ludo_engine.strategy import StrategyFactory
from ludo_engine.strategies.human import HumanStrategy
from ludo_interface.board_viz import draw_board, preload_board_template
from ludo_engine.model import MoveResult

AI_STRATEGIES = StrategyFactory.get_available_strategies()
DEFAULT_PLAYERS = [
    PlayerColor.RED,
    PlayerColor.GREEN,
    PlayerColor.YELLOW,
    PlayerColor.BLUE,
]

class LudoApp:
    """Encapsulates the Ludo game application logic and Gradio UI."""

    def __init__(self, players: Optional[List[PlayerColor]] = None, show_token_ids: bool = True):
        """
        Initializes the Ludo application.
        
        Args:
            players (Optional[List[PlayerColor]]): A list of player colors. Defaults to standard four players.
            show_token_ids (bool): Whether to display token IDs on the board.
        """
        self.default_players = players if players is not None else DEFAULT_PLAYERS
        self.show_token_ids = show_token_ids
        self.ai_strategies = StrategyFactory.get_available_strategies()
        
        # Preload assets
        preload_board_template()
        print("🚀 Initializing Enhanced Ludo Game...")

    def _img_to_data_uri(self, pil_img):
        """Return an inline data URI for the PIL image to avoid Gradio temp file folders."""
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return (
            "<div style='display:flex;justify-content:center;'>"
            f"<img src='data:image/png;base64,{b64}' "
            "style='image-rendering:pixelated;max-width:800px;width:100%;height:auto;border-radius:10px;box-shadow:0 4px 8px rgba(0,0,0,0.1);' />"
            "</div>"
        )

    def _init_game(self, strategies: List[str]) -> LudoGame:
        """Initializes a new Ludo game with the given strategies."""
        strategy_objs = [StrategyFactory.create_strategy(name) for name in strategies]
        game = LudoGame(self.default_players)
        for player, strat in zip(game.players, strategy_objs):
            player.set_strategy(strat)
        return game

    def _game_state_tokens(self, game: LudoGame) -> Dict[str, List[Token]]:
        """Extracts token information from the game state."""
        token_map: Dict[str, List[Dict]] = {c.value: [] for c in PlayerColor}
        for p in game.players:
            for t in p.tokens:
                token_map[p.color.value].append(t)
        return token_map

    def _get_human_strategy(self, game: LudoGame) -> Optional[HumanStrategy]:
        """Get the human strategy from the current player if it exists."""
        current_player = game.get_current_player()
        return current_player.strategy if isinstance(current_player.strategy, HumanStrategy) else None

    def _is_human_turn(self, game: LudoGame) -> bool:
        """Check if it's currently a human player's turn."""
        return self._get_human_strategy(game) is not None

    def _get_human_move_options(self, game: LudoGame, dice: int) -> List[dict]:
        """Get move options for a human player."""
        current_player = game.get_current_player()
        valid_moves = game.get_valid_moves(current_player, dice)
        
        options = []
        for move in valid_moves:
            token = current_player.tokens[move.token_id]
            options.append({
                "token_id": move.token_id,
                "description": f"Token {move.token_id}: {token.state.value} at {token.position} -> {move.target_position}",
                "move_type": move.move_type
            })
        return options

    def _serialize_move(self, move_result: MoveResult) -> str:
        """Serializes a move result into a human-readable string."""
        if not move_result or not move_result.success:
            return "No move"
        parts = [f"{move_result.player_color} token {move_result.token_id} -> {move_result.new_position}"]
        if move_result.captured_tokens:
            parts.append(f"captured {len(move_result.captured_tokens)}")
        if move_result.finished_token:
            parts.append("finished")
        if move_result.extra_turn:
            parts.append("extra turn")
        return ", ".join(parts)

    def _play_step(self, game: LudoGame, human_move_choice: Optional[int] = None, dice: Optional[int] = None):
        """Plays a single step of the game.

        If `dice` is provided, use it; otherwise roll a new dice value.
        """
        if game.game_over:
            return game, "Game over", self._game_state_tokens(game), [], False

        current_player = game.get_current_player()
        if dice is None:
            dice = game.roll_dice()
        valid_moves = game.get_valid_moves(current_player, dice)

        if not valid_moves:
            extra_turn = dice == 6
            if not extra_turn:
                game.next_turn()
            
            token_positions = ", ".join([f"token {i}: {t.position} ({t.state.value})" for i, t in enumerate(current_player.tokens)])
            desc = f"{current_player.color.value} rolled {dice} - no moves{' (extra turn)' if extra_turn else ''} | Positions: {token_positions}"
            return game, desc, self._game_state_tokens(game), [], False

        human_strategy = self._get_human_strategy(game)
        if human_strategy and human_move_choice is None:
            move_options = self._get_human_move_options(game, dice)
            desc = f"{current_player.color.value} rolled {dice} - Choose your move:"
            return game, desc, self._game_state_tokens(game), move_options, True

        chosen_move = None
        if human_strategy and human_move_choice is not None:
            chosen_move = next((m for m in valid_moves if m.token_id == human_move_choice), None)
        else:
            ctx = game.get_ai_decision_context(dice)
            token_choice = current_player.make_strategic_decision(ctx)
            chosen_move = next((m for m in valid_moves if m.token_id == token_choice), None)

        if chosen_move is None:
            chosen_move = valid_moves[0]

        move_res = game.execute_move(current_player, chosen_move.token_id, dice)
        desc = f"{current_player.color.value} rolled {dice}: {self._serialize_move(move_res)}"

        if not move_res.extra_turn and not game.game_over:
            game.next_turn()

        if game.game_over:
            desc += f" | WINNER: {game.winner.color.value}"

        return game, desc, self._game_state_tokens(game), [], False

    def create_ui(self):
        """Creates and returns the Gradio UI for the Ludo game."""
        with gr.Blocks(
            title="🎲 Enhanced Ludo AI Visualizer", 
            theme=gr.themes.Soft(),
            css="""
            .board-container {
                max-height: 80vh !important;
                overflow: hidden !important;
            }
            .board-container img {
                max-width: 100% !important;
                max-height: 80vh !important;
                object-fit: contain !important;
            }
            .gradio-accordion {
                margin: 0.25rem 0 !important;
            }
            .gradio-box {
                padding: 0.5rem !important;
                margin: 0.25rem 0 !important;
            }
            """
        ) as demo:
            game_state = gr.State()
            move_history = gr.State([])
            stats_state = gr.State({"games": 0, "wins": {c.value: 0 for c in self.default_players}})
            waiting_for_human = gr.State(False)
            human_move_options = gr.State([])
            # Persist the dice rolled when auto-play pauses for a human turn
            pending_dice = gr.State(None)
            # Holds the token id chosen by the human via a button
            selected_token_id = gr.State(None)
            # Track remaining auto steps and delay to allow resume after human move
            auto_steps_remaining = gr.State(0)
            auto_delay_state = gr.State(0.5)

            with gr.Tabs():
                with gr.TabItem("🎮 Play Game"):
                    self._build_play_game_tab(
                        game_state,
                        move_history,
                        stats_state,
                        waiting_for_human,
                        human_move_options,
                        pending_dice,
                        selected_token_id,
                        auto_steps_remaining,
                        auto_delay_state,
                    )
                with gr.TabItem("🏆 Simulate Multiple Games"):
                    self._build_simulation_tab()
            
            gr.Markdown("""
            ## 🎲 Enhanced Ludo AI Visualizer
            **Features:** 🤖 Multiple AI Strategies • 👤 Human Players • 🎨 Enhanced Graphics • 📊 Statistics
            """)
        return demo

    def _build_play_game_tab(self, game_state, move_history, stats_state, waiting_for_human, human_move_options, pending_dice, selected_token_id, auto_steps_remaining, auto_delay_state):
        """Builds the 'Play Game' tab of the UI."""
        # Main layout: Board dominates the center, controls in compact sidebars
        with gr.Row():
            # Left sidebar: Player config and game controls (compact)
            with gr.Column(scale=1, min_width=280):
                with gr.Accordion("👥 Players", open=True):
                    strategy_inputs = [
                        gr.Dropdown(
                            choices=self.ai_strategies,
                            value="human" if i == 0 else self.ai_strategies[1] if len(self.ai_strategies) > 1 else self.ai_strategies[0],
                            label=f"🔴🟢🟡🔵"[i] + f" {color.value.title()}",
                            container=False,
                            scale=1
                        ) for i, color in enumerate(self.default_players)
                    ]
                
                with gr.Accordion("🎮 Controls", open=True):
                    init_btn = gr.Button("� New Game", variant="primary", size="sm")
                    random_btn = gr.Button("🎲 Random", size="sm")
                    with gr.Row():
                        step_btn = gr.Button("▶️ Step", size="sm", scale=1)
                        auto_steps_n = gr.Number(value=5, minimum=1, maximum=100, container=False, scale=1)
                    with gr.Row():
                        run_auto_btn = gr.Button("🔄 Auto", size="sm", scale=1)
                        auto_delay = gr.Number(value=0.5, minimum=0, maximum=5, step=0.1, container=False, scale=1)
                
                with gr.Accordion("�️ Options", open=False):
                    show_ids = gr.Checkbox(label="Show Token IDs", value=self.show_token_ids, container=False)
                    export_btn = gr.Button("📤 Export", size="sm")
                    move_history_btn = gr.Button("📜 History", size="sm")

            # Center: Main game board (large, no scrolling)
            with gr.Column(scale=3):
                board_plot = gr.HTML(label="🎯 Game Board", elem_classes=["board-container"])
                
                # Human move controls (overlay when needed)
                with gr.Row(visible=False) as human_controls:
                    with gr.Column():
                        human_moves_display = gr.HTML()
                        with gr.Row():
                            move_buttons = [gr.Button(f"Token {i}", visible=False, variant="secondary", size="sm") for i in range(4)]

            # Right sidebar: Game info and stats (compact)
            with gr.Column(scale=1, min_width=280):
                # Current player when not in human turn
                with gr.Row():
                    current_player_display = gr.HTML(value="<h3>🎯 Current Player: Game not started</h3>")
                
                with gr.Accordion("📝 Last Action", open=True):
                    log = gr.Textbox(show_label=False, interactive=False, lines=3, max_lines=4, container=False)
                
                with gr.Accordion("📊 Statistics", open=True):
                    stats_display = gr.JSON(show_label=False, container=False, value={"games": 0, "wins": {c.value: 0 for c in self.default_players}})
                
                with gr.Accordion("📚 History", open=False):
                    history_box = gr.Textbox(show_label=False, lines=6, max_lines=10, container=False)

        # Hidden elements
        export_box = gr.Textbox(label="Game State JSON", lines=6, visible=False)

        # Event Handlers
        init_btn.click(
            self._ui_init, strategy_inputs,
            [
                game_state,
                board_plot,
                log,
                move_history,
                stats_state,
                current_player_display,
                human_controls,
                human_moves_display,
            ]
            + move_buttons
            + [human_move_options, pending_dice, selected_token_id, auto_steps_remaining, auto_delay_state]
        )
        random_btn.click(
            self._ui_random_strategies, outputs=strategy_inputs
        ).then(
            self._ui_init, strategy_inputs,
            [
                game_state,
                board_plot,
                log,
                move_history,
                stats_state,
                current_player_display,
                human_controls,
                human_moves_display,
            ]
            + move_buttons
            + [human_move_options, pending_dice, selected_token_id, auto_steps_remaining, auto_delay_state]
        )
        step_btn.click(
            self._ui_steps, [game_state, move_history, show_ids, pending_dice],
            [
                game_state,
                board_plot,
                log,
                move_history,
                waiting_for_human,
                current_player_display,
                human_moves_display,
                human_controls,
            ]
            + move_buttons
            + [human_move_options, pending_dice, selected_token_id, auto_steps_remaining, auto_delay_state]
        ).then(self._ui_update_stats, [stats_state, game_state], [stats_state]).then(lambda s: s, [stats_state], [stats_display])

        for i, btn in enumerate(move_buttons):
            btn.click(
                lambda opts, idx=i: opts[idx]["token_id"] if idx < len(opts) else None,
                [human_move_options], [selected_token_id]
            ).then(
                self._ui_make_human_move, [selected_token_id, game_state, move_history, show_ids, human_move_options, pending_dice, auto_steps_remaining, auto_delay_state],
                [
                    game_state,
                    board_plot,
                    log,
                    move_history,
                    waiting_for_human,
                    current_player_display,
                    human_moves_display,
                    human_controls,
                ]
                + move_buttons
                + [human_move_options, pending_dice, selected_token_id, auto_steps_remaining, auto_delay_state]
            ).then(self._ui_update_stats, [stats_state, game_state], [stats_state]).then(lambda s: s, [stats_state], [stats_display]).then(
                self._ui_resume_auto,
                [auto_steps_remaining, auto_delay_state, game_state, move_history, show_ids],
                [
                    game_state,
                    board_plot,
                    log,
                    move_history,
                    waiting_for_human,
                    current_player_display,
                    human_moves_display,
                    human_controls,
                ]
                + move_buttons
                + [human_move_options, pending_dice, selected_token_id, auto_steps_remaining, auto_delay_state]
            ).then(self._ui_update_stats, [stats_state, game_state], [stats_state]).then(lambda s: s, [stats_state], [stats_display])

        run_auto_btn.click(
            self._ui_run_auto, [auto_steps_n, auto_delay, game_state, move_history, show_ids],
            [
                game_state,
                board_plot,
                log,
                move_history,
                waiting_for_human,
                current_player_display,
                human_moves_display,
                human_controls,
            ]
            + move_buttons
            + [human_move_options, pending_dice, selected_token_id, auto_steps_remaining, auto_delay_state]
        ).then(self._ui_update_stats, [stats_state, game_state], [stats_state]).then(lambda s: s, [stats_state], [stats_display])

        move_history_btn.click(lambda h: "\n".join(h[-30:]), [move_history], [history_box])
        export_btn.click(self._ui_export, [game_state], [export_box])

    def _build_simulation_tab(self):
        """Builds the 'Simulate Multiple Games' tab of the UI."""
        gr.Markdown("### 🤖 AI Tournament Simulation")
        sim_strat_inputs = [
            gr.Dropdown(
                choices=[s for s in self.ai_strategies if s != "human"],
                value=[s for s in self.ai_strategies if s != "human"][0],
                label=f"{color.value.title()} Strategy",
            ) for color in self.default_players
        ]
        with gr.Row():
            bulk_games = gr.Slider(10, 2000, value=100, step=10, label="Number of Games")
            bulk_run_btn = gr.Button("🚀 Run Simulation", variant="primary")
        bulk_results = gr.Textbox(label="🏆 Simulation Results", lines=10)
        
        bulk_run_btn.click(self._ui_run_bulk, [bulk_games] + sim_strat_inputs, [bulk_results])

    # UI-specific methods (callbacks for Gradio)
    def _ui_init(self, *strats):
        game = self._init_game(list(strats))
        pil_img = draw_board(self._game_state_tokens(game), show_ids=self.show_token_ids)
        html = self._img_to_data_uri(pil_img)
        
        current_player = game.get_current_player()
        player_html = f"<h3 style='color: {current_player.color.value};'>🎯 Current Player: {current_player.color.value.title()}</h3>"
        
        has_human = any(s == "human" for s in strats)
        controls_visible = has_human and self._is_human_turn(game)
        
        return (
            game, html, "🎮 Game initialized! Roll the dice to start.", [],
            {"games": 0, "wins": {c.value: 0 for c in self.default_players}},
            player_html, gr.update(visible=controls_visible), "",
            gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), [],
            None,  # reset pending_dice
            None,  # reset selected_token_id
            0,     # auto_steps_remaining
            0.5    # auto_delay_state default
        )

    def _ui_random_strategies(self):
        strategies = [s for s in self.ai_strategies if s != "human"]
        return [random.choice(strategies) for _ in range(len(self.default_players))]

    def _ui_steps(self, game, history: list[str], show, pending_dice, human_choice=None):
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
                None,   # pending_dice
                None,   # selected_token_id
                0,      # auto_steps_remaining
                None,   # auto_delay_state
            )
        
        game, desc, tokens, move_opts, waiting = self._play_step(game, human_choice, pending_dice)
        history.append(desc)
        if len(history) > 50: history = history[-50:]
        
        pil_img = draw_board(tokens, show_ids=show)
        html = self._img_to_data_uri(pil_img)
        
        if not game.game_over:
            current_player = game.get_current_player()
            player_html = f"<h3 style='color: {current_player.color.value};'>🎯 Current Player: {current_player.color.value.title()}</h3>"
        else:
            player_html = f"<h3>🏆 Winner: {game.winner.color.value.title()}!</h3>"
        
        if waiting and move_opts:
            moves_html = "<h4>Choose your move:</h4><ul>" + "".join([f"<li><strong>Token {opt['token_id']}</strong>: {opt['description']} ({opt['move_type']})</li>" for opt in move_opts]) + "</ul>"
            btn_updates = [gr.update(visible=i < len(move_opts), value=f"Move Token {move_opts[i]['token_id']}" if i < len(move_opts) else "") for i in range(4)]
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
                next_pending_dice,   # pending_dice
                None,                # selected_token_id
                0,                   # auto_steps_remaining (manual step path)
                None,                # auto_delay_state
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
                None,   # pending_dice
                None,   # selected_token_id
                0,      # auto_steps_remaining
                None,   # auto_delay_state
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
                None,   # pending_dice
                None,   # selected_token_id
                0,      # auto_steps_remaining
                delay,  # auto_delay_state
            )
            return
        
        desc = ""
        remaining = int(n)
        for _ in range(int(n)):
            if self._is_human_turn(game):
                current_player = game.get_current_player()
                dice = game.roll_dice()
                valid_moves = game.get_valid_moves(current_player, dice)
                
                if valid_moves:
                    pil_img = draw_board(self._game_state_tokens(game), show_ids=show)
                    html = self._img_to_data_uri(pil_img)
                    player_html = f"<h3 style='color: {current_player.color.value};'>🎯 Current Player: {current_player.color.value.title()}</h3>"
                    desc = f"Auto-play paused: {current_player.color.value} rolled {dice} - Choose your move:"
                    history.append(desc)
                    if len(history) > 50: history = history[-50:]
                    
                    move_options = self._get_human_move_options(game, dice)
                    moves_html = "<h4>Choose your move:</h4><ul>" + "".join([f"<li><strong>Token {opt['token_id']}</strong>: {opt['description']} ({opt['move_type']})</li>" for opt in move_options]) + "</ul>"
                    btn_updates = [gr.update(visible=i < len(move_options), value=f"Move Token {move_options[i]['token_id']}" if i < len(move_options) else "") for i in range(4)]
                    
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
                        dice,                 # pending_dice
                        None,                # selected_token_id
                        remaining_after_pause,  # auto_steps_remaining
                        delay,               # auto_delay_state
                    )
                    return
                else:
                    extra_turn = dice == 6
                    if not extra_turn: game.next_turn()
                    desc = f"{current_player.color.value} rolled {dice} - no moves{' (extra turn)' if extra_turn else ''}"
                    history.append(desc)
                    if len(history) > 50: history = history[-50:]
                    remaining = max(remaining - 1, 0)
            else:
                game, step_desc, _, _, _ = self._play_step(game)
                desc = step_desc
                history.append(step_desc)
                if len(history) > 50: history = history[-50:]
                remaining = max(remaining - 1, 0)
            
            pil_img = draw_board(self._game_state_tokens(game), show_ids=show)
            html = self._img_to_data_uri(pil_img)
            
            if not game.game_over:
                current_player = game.get_current_player()
                player_html = f"<h3 style='color: {current_player.color.value};'>🎯 Current Player: {current_player.color.value.title()}</h3>"
            else:
                player_html = f"<h3>🏆 Winner: {game.winner.color.value.title()}!</h3>"
            
            waiting = self._is_human_turn(game) and not game.game_over
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
                None,      # pending_dice
                None,      # selected_token_id
                remaining, # auto_steps_remaining
                delay,     # auto_delay_state
            )
            
            if game.game_over: break
            if delay and delay > 0 and not waiting: time.sleep(float(delay))

    def _ui_make_human_move(self, token_id, game, history, show, move_opts, pending_dice, auto_steps_remaining, auto_delay_state):
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
                pending_dice,         # pending_dice
                None,                 # selected_token_id
                auto_steps_remaining, # auto_steps_remaining
                auto_delay_state,     # auto_delay_state
            )
        # Use the pending_dice from auto-play to execute the human's chosen move
        out = list(self._ui_steps(game, history, show, pending_dice, token_id))
        # out shape: [..., move_options, pending_dice, selected_token_id, auto_steps_remaining, auto_delay_state]
        if len(out) >= 17:
            out[-2] = auto_steps_remaining
            out[-1] = auto_delay_state
        return tuple(out)

    def _ui_resume_auto(self, remaining, delay, game: LudoGame, history: list[str], show: bool):
        try:
            rem = int(remaining) if remaining is not None else 0
        except Exception:
            rem = 0
        if rem <= 0 or game is None:
            # No resume needed; return a snapshot without changing states
            if game is not None:
                pil_img = draw_board(self._game_state_tokens(game), show_ids=show)
                html = self._img_to_data_uri(pil_img)
                if not game.game_over:
                    current_player = game.get_current_player()
                    player_html = f"<h3 style='color: {current_player.color.value};'>🎯 Current Player: {current_player.color.value.title()}</h3>"
                else:
                    player_html = f"<h3>🏆 Winner: {game.winner.color.value.title()}!</h3>"
            else:
                html = None
                player_html = ""
            return (
                game,
                html,
                "",
                history,
                bool(game and self._is_human_turn(game) and not game.game_over),
                player_html,
                "",
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                [],
                None,   # pending_dice
                None,   # selected_token_id
                0,      # auto_steps_remaining
                delay,  # auto_delay_state
            )
        # Resume by delegating to _ui_run_auto
        for out in self._ui_run_auto(rem, delay, game, history, show):
            yield out

    

    def _ui_export(self, game: LudoGame):
        if not game: return "No game"
        state_dict = {
            "current_turn": game.current_player_index,
            "tokens": {k: [v.to_dict() for v in vs] for k, vs in self._game_state_tokens(game).items()},
            "game_over": game.game_over,
            "winner": game.winner.color.value if game.winner else None,
        }
        return json.dumps(state_dict, indent=2)

    def _ui_run_bulk(self, n_games, *strats):
        ai_strats = [s if s != "human" else "random" for s in strats]
        win_counts = {c.value: 0 for c in self.default_players}
        for _ in range(int(n_games)):
            g = self._init_game(list(ai_strats))
            while not g.game_over:
                g, _, _, _, _ = self._play_step(g)
            if g.winner:
                win_counts[g.winner.color.value] += 1
        total = sum(win_counts.values()) or 1
        summary = {k: {"wins": v, "win_rate": round(v / total, 3)} for k, v in win_counts.items()}
        return json.dumps(summary, indent=2)

    def _ui_update_stats(self, stats, game: LudoGame):
        if game and game.game_over and game.winner:
            stats = dict(stats)
            stats["games"] += 1
            stats["wins"][game.winner.color.value] += 1
        return stats

    def launch(self, server_name="0.0.0.0", server_port=7860, **kwargs):
        """Launches the Gradio application."""
        demo = self.create_ui()
        demo.launch(server_name=server_name, server_port=server_port, **kwargs)


def launch_app():
    """Main entry point for the application."""
    return LudoApp()

if __name__ == "__main__":
    launch_app().launch(share=False, inbrowser=True, show_error=True)
