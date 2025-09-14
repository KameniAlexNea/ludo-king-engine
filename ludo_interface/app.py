"""
Gradio-based web interface for the Ludo game.

This module provides an interactive web interface for playing Ludo games,
visualizing board states, and comparing different AI strategies.
"""

import base64
import io
import json
import os
import sys
import time
from typing import Dict, List, Optional

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Gradio directories to fix folder creation while saving cache
os.environ.setdefault("GRADIO_TEMP_DIR", os.path.join(os.getcwd(), "gradio_runtime"))
os.environ.setdefault(
    "GRADIO_CACHE_DIR",
    os.path.join(os.getcwd(), "gradio_runtime", "cache"),
)

try:
    import gradio as gr
except ImportError:
    raise ImportError("Gradio is required for the web interface. Install with: pip install gradio")

from ludo_engine import LudoGame, StrategyFactory
from .board_viz import draw_board, tokens_to_dict

# Available strategies for the interface
AI_STRATEGIES = StrategyFactory.get_available_strategies()
DEFAULT_COLORS = ['red', 'blue', 'green', 'yellow']


def _img_to_data_uri(pil_img):
    """Convert PIL image to data URI for inline display."""
    buf = io.BytesIO()
    pil_img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return (
        "<div style='display:flex;justify-content:center;'>"
        f"<img src='data:image/png;base64,{b64}' "
        "style='image-rendering:pixelated;max-width:640px;width:100%;height:auto;' />"
        "</div>"
    )


def _init_game(strategies: List[str]) -> LudoGame:
    """Initialize a new game with the specified strategies."""
    # Filter out None strategies and ensure minimum 2 players
    valid_strategies = [s for s in strategies if s is not None]
    
    if len(valid_strategies) < 2:
        raise ValueError("At least 2 strategies are required to start a game")
    
    # Limit to maximum 4 players
    valid_strategies = valid_strategies[:4]
    n_players = len(valid_strategies)
    
    game = LudoGame(
        player_colors=DEFAULT_COLORS[:n_players],
        strategies=valid_strategies,
        seed=None  # Use random seed for variety
    )
    game.start_game()  # Important: start the game!
    return game


def _serialize_move(turn_result) -> str:
    """Convert turn result to human-readable string."""
    if not turn_result:
        return "No move"
    
    parts = []
    
    # Get player color from turn result (it's a string)
    player_color = getattr(turn_result, 'player', 'Unknown')
    
    # Get dice roll
    dice_roll = getattr(turn_result, 'dice_roll', 0)
    parts.append(f"{player_color} rolled {dice_roll}")
    
    # Check if move was made
    if getattr(turn_result, 'move_made', False):
        token_moved = getattr(turn_result, 'token_moved', None)
        if token_moved:
            token_id = getattr(token_moved, 'id', 'Unknown')
            position = getattr(token_moved, 'position', 'Unknown')
            parts.append(f"moved token {token_id} to position {position}")
        else:
            parts.append("made a move")
    else:
        parts.append("no valid moves")
    
    # Check for captures
    captured_tokens = getattr(turn_result, 'captured_tokens', [])
    if captured_tokens:
        parts.append(f"captured {len(captured_tokens)} token(s)")
    
    # Check if token finished
    finished_tokens = getattr(turn_result, 'finished_tokens', 0)
    if finished_tokens > 0:
        parts.append(f"{finished_tokens} token(s) finished!")
    
    # Check for extra turn
    if getattr(turn_result, 'another_turn', False):
        parts.append("gets extra turn")
    
    return ", ".join(parts)


def _play_step(game: LudoGame) -> tuple:
    """Play one step of the game and return results."""
    if game.is_finished():
        return game, "Game over", tokens_to_dict(game)
    
    # Play one turn
    turn_result = game.play_turn()
    
    # Create description
    desc = _serialize_move(turn_result)
    
    # Check if game is finished
    if game.is_finished():
        winner_color = game.get_winner()  # This returns a string
        desc += f" | GAME OVER - Winner: {winner_color}"
    
    return game, desc, tokens_to_dict(game)


def launch_app():
    """Launch the Gradio interface."""
    
    with gr.Blocks(title="Ludo Game Interface") as demo:
        gr.Markdown("# 🎲 Ludo Game Interface")
        gr.Markdown("Play Ludo with different AI strategies and watch the games unfold!")
        
        with gr.Tabs():
            with gr.TabItem("🎮 Play Game"):
                with gr.Row():
                    strategy_inputs = []
                    for i, color in enumerate(DEFAULT_COLORS):
                        strategy_inputs.append(
                            gr.Dropdown(
                                choices=AI_STRATEGIES,
                                value=AI_STRATEGIES[0] if AI_STRATEGIES else 'random',
                                label=f"{color.title()} Strategy"
                            )
                        )
                
                with gr.Row():
                    init_btn = gr.Button("🎯 Start New Game", variant="primary")
                    step_btn = gr.Button("➡️ Play Step")
                    auto_steps = gr.Number(value=10, label="Auto Steps", minimum=1, maximum=100)
                    auto_delay = gr.Number(value=0.5, label="Delay (seconds)", minimum=0.1, maximum=2.0)
                    run_auto_btn = gr.Button("🤖 Run Auto Steps")
                
                with gr.Row():
                    show_ids = gr.Checkbox(label="Show Token IDs", value=True)
                    export_btn = gr.Button("📤 Export Game State")
                    history_btn = gr.Button("📜 Show Move History")
                
                with gr.Row(equal_height=True):
                    with gr.Column(scale=3):
                        board_display = gr.HTML(label="Game Board")
                    with gr.Column(scale=1):
                        last_move = gr.Textbox(label="Last Move", interactive=False)
                        move_history = gr.Textbox(label="Move History", lines=10, interactive=False)
                
                game_stats = gr.JSON(
                    label="Game Statistics",
                    value={"games": 0, "wins": {color: 0 for color in DEFAULT_COLORS}}
                )
            
            with gr.TabItem("🏆 Tournament Mode"):
                with gr.Row():
                    tournament_strategies = []
                    for i, color in enumerate(DEFAULT_COLORS):
                        tournament_strategies.append(
                            gr.Dropdown(
                                choices=AI_STRATEGIES,
                                value=AI_STRATEGIES[i % len(AI_STRATEGIES)] if AI_STRATEGIES else 'random',
                                label=f"{color.title()} Strategy"
                            )
                        )
                
                with gr.Row():
                    num_games = gr.Slider(
                        minimum=10, maximum=1000, value=100, step=10,
                        label="Number of Games"
                    )
                    run_tournament_btn = gr.Button("🏁 Run Tournament", variant="primary")
                
                tournament_results = gr.Textbox(
                    label="Tournament Results", 
                    lines=15, 
                    interactive=False
                )
        
        # Hidden state components
        game_state = gr.State()
        history_state = gr.State([])
        stats_state = gr.State({"games": 0, "wins": {color: 0 for color in DEFAULT_COLORS}})
        export_state = gr.State("")
        
        def init_new_game(*strategies):
            """Initialize a new game with selected strategies."""
            strategies_list = [s for s in strategies if s is not None]
            if len(strategies_list) < 2:
                raise ValueError("At least 2 strategies must be selected to start a game")
            
            game = _init_game(strategies_list)
            game_dict = tokens_to_dict(game)
            board_img = draw_board(game_dict, show_ids=True)
            board_html = _img_to_data_uri(board_img)
            
            return (
                game,
                board_html,
                "Game initialized - Ready to play!",
                [],
                {"games": 0, "wins": {color: 0 for color in DEFAULT_COLORS}}
            )
        
        def play_single_step(game, history, show_token_ids):
            """Play a single step of the game."""
            if game is None:
                return None, None, "No game initialized", history
            
            game, move_desc, game_dict = _play_step(game)
            history = history + [move_desc]
            
            # Keep only last 50 moves
            if len(history) > 50:
                history = history[-50:]
            
            board_img = draw_board(game_dict, show_ids=show_token_ids)
            board_html = _img_to_data_uri(board_img)
            
            return game, board_html, move_desc, history
        
        def run_auto_steps(num_steps, delay, game, history, show_token_ids):
            """Run multiple steps automatically with delay."""
            if game is None:
                return None, None, "No game initialized", history
            
            for _ in range(int(num_steps)):
                game, move_desc, game_dict = _play_step(game)
                history = history + [move_desc]
                
                # Break if game is over
                if "Game over" in move_desc or "GAME OVER" in move_desc:
                    board_img = draw_board(game_dict, show_ids=show_token_ids)
                    board_html = _img_to_data_uri(board_img)
                    yield game, board_html, move_desc, history
                    break
                
                if len(history) > 50:
                    history = history[-50:]
                
                board_img = draw_board(game_dict, show_ids=show_token_ids)
                board_html = _img_to_data_uri(board_img)
                
                yield game, board_html, move_desc, history
                
                if delay > 0:
                    time.sleep(delay)
        
        def export_game_state(game):
            """Export current game state as JSON."""
            if game is None:
                return "No game to export"
            
            try:
                game_dict = tokens_to_dict(game)
                return json.dumps(game_dict, indent=2)
            except Exception as e:
                return f"Error exporting game state: {str(e)}"
        
        def show_move_history(history):
            """Format and return move history."""
            if not history:
                return "No moves yet"
            return "\n".join(f"{i+1}. {move}" for i, move in enumerate(history[-20:]))
        
        def run_tournament(num_games_val, *strategies):
            """Run a tournament with multiple games."""
            # Filter out None strategies and ensure minimum 2 players
            strategies_list = [s for s in strategies if s is not None]
            if len(strategies_list) < 2:
                return "Error: At least 2 strategies must be selected for tournament"
            
            # Limit to maximum 4 players
            strategies_list = strategies_list[:4]
            n_players = len(strategies_list)
            
            # Initialize win counts only for active players
            active_colors = DEFAULT_COLORS[:n_players]
            win_counts = {color: 0 for color in active_colors}
            total_turns = 0
            
            for game_num in range(int(num_games_val)):
                game = _init_game(strategies_list)
                
                # Play game to completion
                turns_in_game = 0
                while not game.is_finished() and turns_in_game < 1000:  # Safety limit
                    game.play_turn()
                    turns_in_game += 1
                
                total_turns += turns_in_game
                
                # Record winner
                if game.is_finished():
                    winner_color = game.get_winner()  # This returns a string
                    if winner_color and winner_color in win_counts:
                        win_counts[winner_color] += 1
            
            # Format results
            total_games = sum(win_counts.values())
            avg_turns = total_turns / max(1, total_games)
            
            results_text = f"🏆 TOURNAMENT RESULTS ({total_games} games)\n"
            results_text += "=" * 50 + "\n\n"
            
            # Sort by wins
            sorted_results = sorted(win_counts.items(), key=lambda x: x[1], reverse=True)
            
            for i, (color, wins) in enumerate(sorted_results):
                win_rate = (wins / max(1, total_games)) * 100
                color_index = active_colors.index(color)
                strategy_name = strategies_list[color_index]
                
                emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "  "
                results_text += f"{emoji} {color.title()} ({strategy_name}): {wins} wins ({win_rate:.1f}%)\n"
            
            results_text += f"\n📊 Average game length: {avg_turns:.1f} turns"
            
            return results_text
        
        def update_stats(stats, game):
            """Update game statistics when a game finishes."""
            if game and game.is_finished():
                stats = dict(stats)
                stats["games"] += 1
                winner_color = game.get_winner()  # This returns a string
                if winner_color and winner_color in stats["wins"]:
                    stats["wins"][winner_color] += 1
            return stats
        
        # Wire up the interface
        init_btn.click(
            init_new_game,
            inputs=strategy_inputs,
            outputs=[game_state, board_display, last_move, history_state, stats_state]
        )
        
        step_btn.click(
            play_single_step,
            inputs=[game_state, history_state, show_ids],
            outputs=[game_state, board_display, last_move, history_state]
        ).then(
            update_stats,
            inputs=[stats_state, game_state],
            outputs=[stats_state]
        ).then(
            lambda stats: stats,
            inputs=[stats_state],
            outputs=[game_stats]
        )
        
        run_auto_btn.click(
            run_auto_steps,
            inputs=[auto_steps, auto_delay, game_state, history_state, show_ids],
            outputs=[game_state, board_display, last_move, history_state]
        ).then(
            update_stats,
            inputs=[stats_state, game_state],
            outputs=[stats_state]
        ).then(
            lambda stats: stats,
            inputs=[stats_state],
            outputs=[game_stats]
        )
        
        export_btn.click(
            export_game_state,
            inputs=[game_state],
            outputs=[export_state]
        ).then(
            lambda state: gr.Textbox(value=state, visible=True),
            inputs=[export_state],
            outputs=[gr.Textbox(label="Exported Game State", lines=10)]
        )
        
        history_btn.click(
            show_move_history,
            inputs=[history_state],
            outputs=[move_history]
        )
        
        run_tournament_btn.click(
            run_tournament,
            inputs=[num_games] + tournament_strategies,
            outputs=[tournament_results]
        )
    
    return demo


def main():
    """Main entry point for the Gradio interface."""
    app = launch_app()
    app.launch(share=False, server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    main()