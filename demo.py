#!/usr/bin/env python3
"""
Simple example demonstrating the Ludo engine in action.
Run this script to see a basic game between AI players.
"""

import random
from ludo.game import LudoGame
from ludo.player import PlayerColor
from ludo.strategy import StrategyFactory

def main():
    """Run a demonstration game."""
    print("🎲 Ludo Engine Demonstration")
    print("=" * 40)
    
    # Set seed for reproducible demo
    random.seed(123)
    
    # Create a game with 4 players using different strategies
    game = LudoGame(player_colors=[PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.YELLOW])
    
    # Assign different strategies to each player
    strategies = ['killer', 'defensive', 'balanced', 'random']
    print("Players and their strategies:")
    for i, strategy_name in enumerate(strategies):
        game.players[i].strategy = StrategyFactory.create_strategy(strategy_name)
        print(f"  Player {game.players[i].color.value}: {strategy_name}")
    
    print("\nStarting game...\n")
    
    # Play game with limited turns for demo
    turn_count = 0
    max_turns = 30
    
    while not game.game_over and turn_count < max_turns:
        current_player = game.get_current_player()
        dice_value = game.roll_dice()
        
        print(f"Turn {turn_count + 1}: {current_player.color.value} rolled {dice_value}")
        
        # Get valid moves
        valid_moves = game.get_valid_moves(current_player, dice_value)
        
        if valid_moves:
            # Get AI decision context and let strategy decide
            context = game.get_ai_decision_context(dice_value)
            token_id = current_player.strategy.decide(context)
            
            # Execute the move
            result = game.execute_move(current_player, token_id, dice_value)
            
            if result['success']:
                print(f"  → Moved token {token_id} from {result['old_position']} to {result['new_position']}")
                if result.get('captured_tokens'):
                    print(f"  💥 Captured: {result['captured_tokens']}")
                if result.get('token_finished'):
                    print(f"  🏁 Token {token_id} finished!")
                if result.get('extra_turn'):
                    print(f"  🎲 Extra turn!")
            
            # Check for next turn
            if not result.get('extra_turn', False):
                game.next_turn()
        else:
            print(f"  ⏭️ No valid moves available")
            game.next_turn()
        
        turn_count += 1
        print()  # Empty line for readability
    
    # Show final status
    print("=" * 40)
    if game.game_over:
        print(f"🏆 Game Over! Winner: {game.winner.color.value}")
    else:
        print(f"Demo completed after {max_turns} turns")
        print("Current standings:")
        for player in game.players:
            finished_count = player.get_finished_tokens_count()
            active_count = sum(1 for token in player.tokens if token.is_active())
            print(f"  {player.color.value}: {finished_count} finished, {active_count} active")

if __name__ == "__main__":
    main()