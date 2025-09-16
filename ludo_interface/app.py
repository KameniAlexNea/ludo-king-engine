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


def _img_to_data_uri(pil_img):
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


def _init_game(strategies: List[str]):
    # Instantiate strategies via factory
    strategy_objs = []
    for _, strat_name in enumerate(strategies):
        strategy = StrategyFactory.create_strategy(strat_name)
        strategy_objs.append(strategy)
    # Build game with chosen strategies
    game = LudoGame(DEFAULT_PLAYERS)
    # Attach strategies
    for player, strat in zip(game.players, strategy_objs):
        player.set_strategy(strat)
    return game


def _game_state_tokens(game: LudoGame) -> Dict[str, List[Token]]:
    token_map: Dict[str, List[Dict]] = {c.value: [] for c in PlayerColor}
    for p in game.players:
        for t in p.tokens:
            token_map[p.color.value].append(t)
    return token_map


def _get_human_strategy(game: LudoGame) -> Optional[HumanStrategy]:
    """Get the human strategy from the current player if it exists."""
    current_player = game.get_current_player()
    if isinstance(current_player.strategy, HumanStrategy):
        return current_player.strategy
    return None


def _is_human_turn(game: LudoGame) -> bool:
    """Check if it's currently a human player's turn."""
    return _get_human_strategy(game) is not None


def _get_human_move_options(game: LudoGame, dice: int) -> List[dict]:
    """Get move options for human player."""
    current_player = game.get_current_player()
    valid_moves = game.get_valid_moves(current_player, dice)
    
    options = []
    for move in valid_moves:
        token = current_player.tokens[move.token_id]
        options.append({
            "token_id": move.token_id,
            "description": f"Token {move.token_id}: {token.state.value} at {token.position} → {move.new_position}",
            "move_type": move.move_type
        })
    
    return options


def _serialize_move(move_result: MoveResult) -> str:
    if not move_result or not move_result.success:
        return "No move"
    parts = [
        f"{move_result.player_color} token {move_result.token_id} -> {move_result.new_position}"
    ]
    if move_result.captured_tokens:
        cap = move_result.captured_tokens
        parts.append(f"captured {len(cap)}")
    if move_result.finished_token:
        parts.append("finished")
    if move_result.extra_turn:
        parts.append("extra turn")
    return ", ".join(parts)
    if not move_result or not move_result.success:
        return "No move"
    parts = [
        f"{move_result.player_color} token {move_result.token_id} -> {move_result.new_position}"
    ]
    if move_result.captured_tokens:
        cap = move_result.captured_tokens
        parts.append(f"captured {len(cap)}")
    if move_result.finished_token:
        parts.append("finished")
    if move_result.extra_turn:
        parts.append("extra turn")
    return ", ".join(parts)


def _play_step(game: LudoGame, human_move_choice: Optional[int] = None):
    if game.game_over:
        return game, "Game over", _game_state_tokens(game), [], False
    
    current_player = game.get_current_player()
    dice = game.roll_dice()
    valid = game.get_valid_moves(current_player, dice)
    
    if not valid:
        # If rolled a 6, player gets another turn even with no moves
        extra_turn = dice == 6
        if not extra_turn:
            game.next_turn()

        # Debug info: show all token positions
        token_positions = []
        for i, token in enumerate(current_player.tokens):
            token_positions.append(f"token {i}: {token.position} ({token.state.value})")
        positions_str = ", ".join(token_positions)

        return (
            game,
            f"{current_player.color.value} rolled {dice} - no moves{' (extra turn)' if extra_turn else ''} | Positions: {positions_str}",
            _game_state_tokens(game),
            [],
            False
        )
    
    # Check if it's a human player's turn
    human_strategy = _get_human_strategy(game)
    if human_strategy and human_move_choice is None:
        # Human player needs to make a choice - return move options
        move_options = _get_human_move_options(game, dice)
        return (
            game,
            f"{current_player.color.value} rolled {dice} - Choose your move:",
            _game_state_tokens(game),
            move_options,
            True  # waiting for human input
        )
    
    # Determine which move to make
    chosen = None
    if human_strategy and human_move_choice is not None:
        # Human player made a choice
        for mv in valid:
            if mv.token_id == human_move_choice:
                chosen = mv
                break
    else:
        # AI player - use strategy
        ctx = game.get_ai_decision_context(dice)
        token_choice = current_player.make_strategic_decision(ctx)
        for mv in valid:
            if mv.token_id == token_choice:
                chosen = mv
                break
    
    if chosen is None:
        chosen = valid[0]
    
    move_res = game.execute_move(current_player, chosen.token_id, dice)
    desc = f"{current_player.color.value} rolled {dice}: {_serialize_move(move_res)}"
    
    if move_res.extra_turn and not game.game_over:
        # do not advance turn
        pass
    else:
        if not game.game_over:
            game.next_turn()
    
    if game.game_over:
        desc += f" | WINNER: {game.winner.color.value}"
    
    return game, desc, _game_state_tokens(game), [], False


def launch_app():
    # Preload board template for optimal performance
    print("🚀 Initializing Enhanced Ludo Game...")
    preload_board_template()
    
    with gr.Blocks(title="🎲 Enhanced Ludo AI Visualizer", theme=gr.themes.Soft()) as demo:
        
        
        with gr.Tabs():
            with gr.TabItem("🎮 Play Game"):
                with gr.Row():
                    with gr.Column(scale=2):
                        gr.Markdown("### 👥 Player Configuration")
                        strategy_inputs = []
                        for i, color in enumerate(DEFAULT_PLAYERS):
                            strategy_inputs.append(
                                gr.Dropdown(
                                    choices=AI_STRATEGIES,
                                    value="human" if i == 0 else AI_STRATEGIES[1] if len(AI_STRATEGIES) > 1 else AI_STRATEGIES[0],
                                    label=f"🔴🟢🟡🔵"[i] + f" {color.value.title()} Strategy",
                                    info="Choose 'human' to play yourself!"
                                )
                            )
                    with gr.Column(scale=1):
                        gr.Markdown("### 🎛️ Display Options")
                        show_ids = gr.Checkbox(label="Show Token IDs", value=True)
                        export_btn = gr.Button("📤 Export Game State", size="sm")
                        move_history_btn = gr.Button("📜 Show Move History", size="sm")
                    
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 🎮 Game Controls")
                        init_btn = gr.Button("🆕 Start New Game", variant="primary", size="sm")
                        random_btn = gr.Button("🎲 Random Strategies", size="sm")
                        step_btn = gr.Button("▶️ Play Step", size="sm")
                    with gr.Column(scale=1):
                        gr.Markdown("### ⚙️ Auto Play Settings")
                        auto_steps_n = gr.Number(value=1, label="Steps", minimum=1, maximum=100)
                        auto_delay = gr.Number(value=0.5, label="Delay (s)", minimum=0, maximum=5, step=0.1)
                        run_auto_btn = gr.Button("🔄 Run Auto Steps", size="sm")
                
                # Human player controls (initially hidden)
                with gr.Row(visible=False) as human_controls:
                    with gr.Column():
                        gr.Markdown("### 🤔 Your Turn!")
                        human_moves_display = gr.HTML()
                        move_buttons = []
                        for i in range(4):  # Max 4 tokens
                            btn = gr.Button(f"Move Token {i}", visible=False, variant="secondary", size="sm")
                            move_buttons.append(btn)
                
                with gr.Row(equal_height=True):
                    with gr.Column(scale=3):
                        board_plot = gr.HTML(label="🎯 Game Board")
                    with gr.Column(scale=1):
                        current_player_display = gr.HTML(value="<h3>🎯 Current Player: Game not started</h3>")
                        log = gr.Textbox(label="📝 Last Action", interactive=False, lines=3)
                        history_box = gr.Textbox(label="📚 Move History", lines=8, max_lines=15)
                
                stats_display = gr.JSON(
                    label="📊 Game Statistics",
                    value={"games": 0, "wins": {c.value: 0 for c in DEFAULT_PLAYERS}},
                )
                
            with gr.TabItem("🏆 Simulate Multiple Games"):
                gr.Markdown("### 🤖 AI Tournament Simulation")
                sim_strat_inputs = []
                for color in DEFAULT_PLAYERS:
                    sim_strat_inputs.append(
                        gr.Dropdown(
                            choices=[s for s in AI_STRATEGIES if s != "human"],
                            value=[s for s in AI_STRATEGIES if s != "human"][0],
                            label=f"{color.value.title()} Strategy",
                        )
                    )
                with gr.Row():
                    bulk_games = gr.Slider(
                        10, 2000, value=100, step=10, label="Number of Games"
                    )
                    bulk_run_btn = gr.Button("🚀 Run Simulation", variant="primary")
                bulk_results = gr.Textbox(label="🏆 Simulation Results", lines=10)
        
        # Hidden state components
        export_box = gr.Textbox(label="Game State JSON", lines=6, visible=False)
        gr.Markdown("""
        # 🎲 Enhanced Ludo AI Visualizer
        
        Experience Ludo with beautiful graphics, multiple AI strategies, and human player support!
        
        ## Features:
        - 🤖 **Multiple AI Strategies**: Choose from various AI personalities
        - 👤 **Human Players**: Select "human" strategy to play yourself
        - 🎨 **Enhanced Graphics**: Beautiful board with token stacking visualization
        - 📊 **Game Statistics**: Track wins and performance
        """)
        game_state = gr.State()
        move_history = gr.State([])
        stats_state = gr.State(
            {"games": 0, "wins": {c.value: 0 for c in DEFAULT_PLAYERS}}
        )
        waiting_for_human = gr.State(False)
        human_move_options = gr.State([])

        def _init(*strats):
            game = _init_game(list(strats))
            pil_img = draw_board(_game_state_tokens(game), show_ids=True)
            html = _img_to_data_uri(pil_img)
            
            current_player = game.get_current_player()
            player_html = f"<h3 style='color: {current_player.color.value};'>🎯 Current Player: {current_player.color.value.title()}</h3>"
            
            # Check if any human players
            has_human = any(strat == "human" for strat in strats)
            controls_visible = has_human and _is_human_turn(game)
            
            return (
                game,
                html,
                "🎮 Game initialized! Roll the dice to start.",
                [],
                {"games": 0, "wins": {c.value: 0 for c in DEFAULT_PLAYERS}},
                player_html,
                gr.update(visible=controls_visible),
                "",
                gr.update(visible=False),
                gr.update(visible=False), 
                gr.update(visible=False), 
                gr.update(visible=False),
                []
            )

        def _random_strategies():
            """Return random strategies for all 4 players."""
            import random
            strategies = [s for s in AI_STRATEGIES if s != "human"]  # Exclude human for random
            return [random.choice(strategies) for _ in range(4)]

        def _steps(game, history: list[str], show, human_choice=None):
            if game is None:
                return None, None, "No game initialized", history, False, "", "", gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), []
            
            game, desc, tokens, move_opts, waiting = _play_step(game, human_choice)
            history.append(desc)
            if len(history) > 50:
                history = history[-50:]
            
            pil_img = draw_board(tokens, show_ids=show)
            html = _img_to_data_uri(pil_img)
            
            # Update current player display
            if not game.game_over:
                current_player = game.get_current_player()
                player_html = f"<h3 style='color: {current_player.color.value};'>🎯 Current Player: {current_player.color.value.title()}</h3>"
            else:
                player_html = f"<h3>🏆 Winner: {game.winner.color.value.title()}!</h3>"
            
            # Handle human player interface
            if waiting and move_opts:
                moves_html = "<h4>Choose your move:</h4><ul>"
                for opt in move_opts:
                    moves_html += f"<li><strong>Token {opt['token_id']}</strong>: {opt['description']} ({opt['move_type']})</li>"
                moves_html += "</ul>"
                
                # Update button visibility and labels
                btn_updates = []
                for i in range(4):
                    if i < len(move_opts):
                        btn_updates.append(gr.update(visible=True, value=f"Move Token {move_opts[i]['token_id']}"))
                    else:
                        btn_updates.append(gr.update(visible=False))
                
                return (game, html, desc, history, waiting, player_html, moves_html, 
                        gr.update(visible=True), *btn_updates, move_opts)
            else:
                return (game, html, desc, history, False, player_html, "", 
                        gr.update(visible=False), gr.update(visible=False), 
                        gr.update(visible=False), gr.update(visible=False), 
                        gr.update(visible=False), [])

        def _run_auto(n, delay, game: LudoGame, history: list[str], show: bool):
            if game is None:
                return None, None, "No game", history, False, "", ""
            
            desc = ""
            for _ in range(int(n)):
                # Skip auto play if it's human turn
                if _is_human_turn(game):
                    desc = f"Waiting for human player ({game.get_current_player().color.value})"
                    break
                    
                game, step_desc, tokens, _, _ = _play_step(game)
                desc = step_desc
                history.append(step_desc)
                if len(history) > 50:
                    history = history[-50:]
                
                if game.game_over:
                    break
                if delay and delay > 0:
                    time.sleep(float(delay))
            
            pil_img = draw_board(_game_state_tokens(game), show_ids=show)
            html = _img_to_data_uri(pil_img)
            
            # Update current player display
            if not game.game_over:
                current_player = game.get_current_player()
                player_html = f"<h3 style='color: {current_player.color.value};'>🎯 Current Player: {current_player.color.value.title()}</h3>"
            else:
                player_html = f"<h3>🏆 Winner: {game.winner.color.value.title()}!</h3>"
            
            waiting = _is_human_turn(game) and not game.game_over
            controls_visible = waiting
            
            return game, html, desc, history, waiting, player_html, ""

        def _make_human_move(token_id, game, history, show, move_opts):
            """Handle human player move selection."""
            if not move_opts:
                return game, None, "No moves available", history, False, "", "", gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), []
            
            return _steps(game, history, show, token_id)

        def _export(game: LudoGame):
            if not game:
                return "No game"
            state_dict = {
                "current_turn": game.current_player_index,
                "tokens": _game_state_tokens(game),
                "game_over": game.game_over,
                "winner": game.winner.color.value if game.winner else None,
            }
            return json.dumps(state_dict, indent=2)

        def _run_bulk(n_games, *strats):
            # Filter out human strategies for bulk simulation
            ai_strats = [s if s != "human" else "random" for s in strats]
            win_counts = {c.value: 0 for c in DEFAULT_PLAYERS}
            for _ in range(int(n_games)):
                g = _init_game(list(ai_strats))
                while not g.game_over:
                    g, _, _, _, _ = _play_step(g)
                win_counts[g.winner.color.value] += 1
            total = sum(win_counts.values()) or 1
            summary = {
                k: {"wins": v, "win_rate": round(v / total, 3)}
                for k, v in win_counts.items()
            }
            return json.dumps(summary, indent=2)

        def _update_stats(stats, game: LudoGame):
            if game and game.game_over and game.winner:
                stats = dict(stats)
                stats["games"] += 1
                stats["wins"][game.winner.color.value] += 1
            return stats

        # Event handlers
        init_btn.click(
            _init,
            strategy_inputs,
            [game_state, board_plot, log, move_history, stats_state, 
             current_player_display, human_controls, human_moves_display] + move_buttons + [human_move_options],
        )
        
        random_btn.click(
            _random_strategies,
            outputs=strategy_inputs,
        ).then(
            _init,
            strategy_inputs,
            [game_state, board_plot, log, move_history, stats_state, 
             current_player_display, human_controls, human_moves_display] + move_buttons + [human_move_options],
        )
        
        step_btn.click(
            _steps,
            [game_state, move_history, show_ids],
            [game_state, board_plot, log, move_history, waiting_for_human, 
             current_player_display, human_moves_display, human_controls] + move_buttons + [human_move_options],
        ).then(_update_stats, [stats_state, game_state], [stats_state]).then(
            lambda s: s, [stats_state], [stats_display]
        )
        
        # Human move buttons
        for i, btn in enumerate(move_buttons):
            btn.click(
                lambda opts, idx=i: opts[idx]["token_id"] if idx < len(opts) else 0,
                [human_move_options],
                [gr.State()]
            ).then(
                _make_human_move,
                [gr.State(), game_state, move_history, show_ids, human_move_options],
                [game_state, board_plot, log, move_history, waiting_for_human, 
                 current_player_display, human_moves_display, human_controls] + move_buttons + [human_move_options],
            ).then(_update_stats, [stats_state, game_state], [stats_state]).then(
                lambda s: s, [stats_state], [stats_display]
            )
        
        run_auto_btn.click(
            _run_auto,
            [auto_steps_n, auto_delay, game_state, move_history, show_ids],
            [game_state, board_plot, log, move_history, waiting_for_human, current_player_display, human_moves_display],
        ).then(_update_stats, [stats_state, game_state], [stats_state]).then(
            lambda s: s, [stats_state], [stats_display]
        )
        
        move_history_btn.click(
            lambda h: "\n".join(h[-50:]), [move_history], [history_box]
        )
        export_btn.click(_export, [game_state], [export_box])
        bulk_run_btn.click(_run_bulk, [bulk_games] + sim_strat_inputs, [bulk_results])

    return demo


def main():
    """Main entry point for the application."""
    demo = launch_app()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True,
        show_error=True
    )


if __name__ == "__main__":
    launch_app().launch()
