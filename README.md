# Ludo King Engine

[![CI](https://github.com/KameniAlexNea/ludo-king-engine/actions/workflows/test-ci.yml/badge.svg)](https://github.com/KameniAlexNea/ludo-king-engine/actions/workflows/test-ci.yml)
[![Coverage](https://codecov.io/gh/KameniAlexNea/ludo-king-engine/branch/main/graph/badge.svg)](https://codecov.io/gh/KameniAlexNea/ludo-king-engine)

A complete Python implementation of the Ludo board game with AI strategies and web-based visualization. Features a pure Python engine built for reinforcement learning, strategy testing, and interactive gameplay. Includes multiple built-in AI strategies and a modern web interface for visualization and strategy comparison.

## Features

- **Pure Python Implementation**: No external dependencies required for core engine
- **Web-Based Interface**: Interactive Gradio-based visualizer for gameplay and analysis
- **Deterministic Gameplay**: Reproducible games with seed support
- **Strategy Framework**: Extensible strategy system with 10+ built-in AI strategies
- **Clean Architecture**: Separated game mechanics from AI strategies
- **Comprehensive Analysis**: Detailed game state tracking and statistics
- **Tournament Support**: Multi-game competition framework with league tables
- **Real-time Visualization**: Step-by-step game playback with token movement
- **Strategy Comparison**: Built-in tools for comparing AI performance

## Core Components

### Game Mechanics
- **Board**: Game board representation with 56 positions and safe zones
- **Token**: Individual game pieces with position and state tracking
- **Player**: Player management with token lifecycle and statistics
- **Game**: Main game flow controller with turn management

### Strategy Framework
- **Heuristic Strategies**: Random, Killer, Defensive, Balanced
- **Advanced Strategies**: Cautious, Optimist, Winner, Probabilistic
- **LLM-Ready**: Extensible framework for LLM-driven strategies
- **Strategy Factory**: Easy instantiation and management of strategies

## Quick Start

### Launch Web Interface
```bash
# Install dependencies
pip install gradio pillow

# Run the web interface
python main.py
```

The web interface will open at http://localhost:7860 with:
- **Interactive Gameplay**: Step-by-step game visualization
- **Strategy Selection**: Choose AI strategies for each player
- **Tournament Mode**: Run multiple games and compare performance
- **Real-time Analysis**: View game statistics and move history

### Programmatic Usage
```python
from ludo_engine import LudoGame, StrategyFactory

# Create a game with different strategies
game = LudoGame(
    player_colors=['red', 'blue', 'green', 'yellow'],
    strategies=['random', 'killer', 'defensive', 'balanced'],
    seed=42  # For reproducible results
)

# Play a complete game
results = game.play_game()
print(f"Winner: {results['winner']}")
print(f"Turns played: {results['turns_played']}")
```

## Available Strategies

| Strategy | Description |
|----------|-------------|
| **Random** | Randomly selects from available moves |
| **Killer** | Prioritizes capturing opponent tokens |
| **Defensive** | Prioritizes safe moves and protecting tokens |
| **Balanced** | Balances offensive and defensive considerations |
| **Cautious** | Very conservative, minimizes risk |
| **Optimist** | Aggressive, takes calculated risks |
| **Winner** | Focuses on getting tokens to finish quickly |
| **Probabilistic** | Uses probability calculations for decisions |
| **ProbabilisticV2/V3** | Advanced probabilistic strategies |
| **WeightedRandom** | Stochastic sampling with strategic heuristics |
| **HybridProb** | Combines multiple evaluation methods |

## Web Interface Features

The built-in web interface provides:

- **🎮 Interactive Gameplay**: Step-by-step game visualization with animated token movement
- **🤖 Strategy Selection**: Choose from 10+ AI strategies for each player
- **🏆 Tournament Mode**: Run multiple games automatically and view league tables
- **📊 Real-time Statistics**: Track wins, game length, and performance metrics
- **🔄 Game Export**: Save and load game states for analysis
- **📈 Move History**: Review complete game history with detailed move descriptions
- **🎲 Auto-Play**: Run games automatically with configurable speed
- **📱 Responsive Design**: Works on desktop and mobile browsers

### Interface Screenshots

*Launch the interface with `python main.py` to see the interactive features in action.*

## Tournament Performance Results

Here's a sample tournament performance showing how different strategies compete in a league format:

```
🎮 LUDO STRATEGY TOURNAMENT
==================================================
🎛️ Configuration loaded from .env file:
   Max turns per game: 200
   Games per match: 10
   Default strategies: random, killer, defensive, balanced, cautious, optimist, winner, probabilistic
   Verbose logging: True

🚀 Starting tournament...
🏆 Ludo Strategy Tournament
📊 8 teams competing
🎮 10 game(s) per match
🏠 Home and away format

🏁 Tournament completed!

🏆 FINAL LEAGUE TABLE
=====================================================================================
Pos Team            P   W   D   L   GF  GA  GD   Pts  Win%  
-------------------------------------------------------------------------------------
1   balanced        14  13  0   1   13  1   +12  39   92.9   🥇
2   probabilistic   14  9   3   2   9   2   +7   30   64.3   🥈
3   cautious        14  9   1   4   9   4   +5   28   64.3   🥉
4   defensive       14  6   2   6   6   6   0    20   42.9   
5   optimist        14  5   2   7   5   7   -2   17   35.7   
6   killer          14  4   0   10  4   10  -6   12   28.6   
7   winner          14  3   1   10  3   10  -7   10   21.4   
8   random          14  2   1   11  2   11  -9   7    14.3   🔻
-------------------------------------------------------------------------------------
Legend: P=Played, W=Won, D=Draw, L=Lost, GF=Goals For, GA=Goals Against, GD=Goal Difference

🏆 CHAMPION: balanced
   📊 39 points from 14 games
   🎯 92.9% win rate

📈 TOURNAMENT STATISTICS:
   🎮 Total matches played: 56
   📊 Draws: 5 (8.9%)
   ⏱️  Average game length: 144.1 turns
```

**Key Insights:**
- **Balanced** strategy dominates with 92.9% win rate
- **Probabilistic** and **Cautious** strategies perform well in 2nd and 3rd
- **Random** strategy has the lowest performance as expected
- Tournament format provides comprehensive strategy comparison

## Game Rules

- Standard Ludo rules with 4 players (2-4 supported)
- Each player has 4 tokens starting at home
- Roll 6 to get tokens out of home
- 57 steps required to finish (1 to start + 56 around board)
- Capture opponent tokens by landing on them (except safe positions)
- Rolling 6 or capturing gives another turn
- Maximum 3 consecutive 6s before turn ends
- First player to get all 4 tokens finished wins

## Examples

### Basic Game
```python
from ludo_engine import LudoGame

# Simple 2-player game
game = LudoGame(['red', 'blue'], ['random', 'killer'])
results = game.play_game()
```

### Strategy Comparison
```python
# Compare different strategies
strategies = ['random', 'killer', 'defensive', 'balanced']
wins = {s: 0 for s in strategies}

for i in range(100):  # Play 100 games
    game = LudoGame(['red', 'blue', 'green', 'yellow'], strategies)
    results = game.play_game()
    
    if results['winner']:
        # Find winning strategy
        for player in game.players:
            if player.color == results['winner']:
                wins[player.strategy.name.lower()] += 1
                break

print("Win rates:", wins)
```

### Custom Strategy
```python
from ludo_engine.strategies import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("MyStrategy")
    
    def choose_move(self, movable_tokens, dice_roll, game_state):
        # Implement your strategy logic here
        return movable_tokens[0] if movable_tokens else None

# Register and use your strategy
from ludo_engine.strategies import StrategyFactory
StrategyFactory.register_strategy('my_strategy', MyStrategy)

game = LudoGame(['red', 'blue'], ['my_strategy', 'balanced'])
```

### Game Analysis
```python
# Detailed game analysis
game = LudoGame(['red', 'blue'], ['balanced', 'probabilistic'])
game.start_game()

while not game.is_finished():
    current_player = game.get_current_player()
    turn_result = game.play_turn()
    
    print(f"Player {current_player.color}: "
          f"Rolled {turn_result['dice_roll']}, "
          f"Move: {turn_result['move_made']}")
    
    if turn_result['captured_tokens']:
        print(f"  Captured {len(turn_result['captured_tokens'])} tokens!")

final_results = game.get_game_results()
```

## Use Cases

### Reinforcement Learning
- **State Representation**: Complete game state available as dictionaries
- **Action Space**: Clear move choices with valid action filtering
- **Reward Signals**: Win/loss, captures, progress tracking
- **Deterministic**: Reproducible training with seeds

### Strategy Research
- **A/B Testing**: Compare strategy performance
- **Tournament Mode**: Multi-strategy competitions
- **Statistical Analysis**: Detailed game statistics
- **Custom Strategies**: Easy to implement and test new approaches

### Educational
- **Game Theory**: Study strategic decision making
- **Probability**: Analyze dice roll impacts and risk assessment
- **AI Development**: Learn game AI programming
- **Algorithm Comparison**: Benchmark different approaches

## Architecture

```
ludo_engine/           # Core game engine (pure Python)
├── board.py           # Game board logic and position management
├── token.py           # Token mechanics and state management
├── player.py          # Player management and statistics
├── game.py            # Main game engine and turn management
├── model.py           # Data models and type definitions
├── constants.py       # Game constants and configuration
├── strategy.py        # Strategy factory and base classes
└── strategies/        # AI strategy implementations
    ├── base.py        # Base strategy class
    ├── utils.py       # Strategy utility functions
    ├── random_strategy.py
    ├── balanced.py
    ├── cautious.py
    ├── defensive.py
    ├── killer.py
    ├── optimist.py
    ├── winner.py
    ├── probabilistic*.py
    ├── weighted_random.py
    └── llm/           # LLM-powered strategies
        ├── prompt.py
        └── strategy.py

ludo_interface/        # Web interface (optional)
├── app.py             # Main Gradio application
└── board_viz.py       # Board visualization utilities

tests/                 # Comprehensive test suite
├── test_*.py          # Unit tests for all components
└── ...

examples/              # Usage examples and demos
└── ...

main.py                # Entry point for web interface
```

## Requirements

- Python 3.7+
- Core engine: No external dependencies (pure Python)
- Web interface: `gradio`, `pillow` (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/KameniAlexNea/ludo-king-engine.git
cd ludo-king-engine
```

2. Install dependencies (optional, for web interface):
```bash
pip install gradio pillow
```

3. Run tests:
```bash
python -m unittest discover -s tests
```

4. Launch the web interface:
```bash
python main.py
```

5. Try the examples:
```bash
python examples/comprehensive_demo.py
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

- [x] Web-based game visualization
- [ ] LLM-powered strategies integration
- [ ] Multi-threading for tournament simulations
- [ ] Advanced statistical analysis tools
- [ ] Export/import game replay functionality
- [ ] Custom board layouts and rule variations
- [ ] Mobile-responsive web interface
- [ ] Strategy training mode for reinforcement learning
