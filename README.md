# Ludo King Engine

Pure Python implementation of the Ludo board game engine extracted from [KameniAlexNea/ludo-king-ai](https://github.com/KameniAlexNea/ludo-king-ai).

## Overview

This repository contains a complete, self-contained Ludo game engine with:

- **Deterministic game mechanics**: Board logic, token movement, capture resolution
- **Strategy framework**: Extensible system supporting multiple AI strategies
- **Clean architecture**: Separation of game mechanics and strategy implementation
- **Minimal dependencies**: Standard library focused with optional extensions

## Features

- ✅ Complete Ludo game implementation following standard rules
- ✅ Multiple built-in AI strategies (random, killer, defensive, balanced, etc.)
- ✅ Extensible strategy system for custom AI implementations
- ✅ LLM strategy support (optional dependency)
- ✅ RL environment compatibility (optional dependency)
- ✅ Comprehensive game state tracking and history
- ✅ Support for 2-4 players

## Quick Start

### Installation

```bash
# Basic installation
pip install -e .

# With LLM strategy support
pip install -e ".[llm]"

# With RL environment support
pip install -e ".[rl]"

# Full installation with all optional dependencies
pip install -e ".[all]"
```

### Basic Usage

```python
from ludo.game import LudoGame
from ludo.player import PlayerColor
from ludo.strategy import StrategyFactory

# Create a game with 4 players
game = LudoGame(player_colors=[PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.YELLOW])

# Set different strategies for each player
strategies = ['killer', 'defensive', 'balanced', 'random']
for i, strategy_name in enumerate(strategies):
    game.players[i].strategy = StrategyFactory.create_strategy(strategy_name)

# Play the game
while not game.game_over:
    # Get current player and dice roll
    current_player = game.get_current_player()
    dice_value = game.roll_dice()
    
    # Get valid moves
    valid_moves = game.get_valid_moves(current_player, dice_value)
    
    # Strategy decides the move
    if valid_moves:
        # Get AI decision context
        context = game.get_ai_decision_context(dice_value)
        token_id = current_player.strategy.decide(context)
        
        # Execute the move
        result = game.execute_move(current_player, token_id, dice_value)
        print(f"Player {current_player.color.value} moved token {token_id}")
        
        # Check for extra turn
        if not result.get('extra_turn', False):
            game.next_turn()
    else:
        # No valid moves, next player's turn
        game.next_turn()

print(f"Game over! Winner: {game.winner.color.value if game.winner else 'None'}")
```

## Architecture

The engine is organized into clean, modular components:

### Core Components

- **`ludo/game.py`**: Main game orchestration and flow control
- **`ludo/board.py`**: Board logic and spatial rules
- **`ludo/player.py`**: Player state and token management
- **`ludo/token.py`**: Individual token state and movement
- **`ludo/constants.py`**: Game constants and configuration

### Strategy System

- **`ludo/strategy.py`**: Strategy factory and registry
- **`ludo/strategies/base.py`**: Base strategy interface
- **`ludo/strategies/`**: Built-in strategy implementations

Available strategies:
- `random`: Random valid move selection
- `killer`: Aggressive capture-focused strategy
- `defensive`: Safety and risk avoidance
- `balanced`: Mixed risk/reward approach
- `cautious`: Minimal exposure strategy
- `optimist`: Progress and finishing emphasis
- `winner`: Finishing acceleration
- `probabilistic*`: Experimental probability-based strategies
- `llm_strategy`: LLM-powered decision making (requires LLM dependencies)

## Documentation

For detailed documentation about the game engine, see [ludo/README.md](ludo/README.md).

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Credits

This engine was extracted from the [ludo-king-ai](https://github.com/KameniAlexNea/ludo-king-ai) project by KameniAlexNea.
