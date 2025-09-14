# Ludo Core Engine

[![CI](https://github.com/KameniAlexNea/ludo-king-engine/actions/workflows/test-ci.yml/badge.svg)](https://github.com/KameniAlexNea/ludo-king-engine/actions/workflows/test-ci.yml)
[![Coverage](https://codecov.io/gh/KameniAlexNea/ludo-king-engine/branch/main/graph/badge.svg)](https://codecov.io/gh/KameniAlexNea/ludo-king-engine)

A pure Python implementation of the Ludo game, built for reinforcement learning and strategy testing. The engine defines deterministic rules, cleanly separates game mechanics from strategies, and requires no external libraries.

## Features

- **Pure Python Implementation**: No external dependencies required
- **Deterministic Gameplay**: Reproducible games with seed support
- **Strategy Framework**: Extensible strategy system with multiple built-in strategies
- **Clean Architecture**: Separated game mechanics from AI strategies
- **Comprehensive Analysis**: Detailed game state tracking and statistics
- **Tournament Support**: Multi-game competition framework

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
ludo_engine/
├── core/
│   ├── board.py      # Game board logic
│   ├── token.py      # Token mechanics
│   ├── player.py     # Player management
│   └── game.py       # Main game engine
├── strategies/
│   ├── base_strategy.py    # Strategy interface
│   ├── heuristic.py        # Basic strategies
│   ├── advanced.py         # Advanced strategies
│   └── factory.py          # Strategy factory
└── utils/
    └── # Utility functions (future expansion)
```

## Requirements

- Python 3.7+
- No external dependencies (pure Python)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/KameniAlexNea/ludo-king-engine.git
cd ludo-king-engine
```

2. Run tests:
```bash
python tests/test_basic.py
python tests/test_completion.py
```

3. Try the examples:
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

- [ ] LLM-powered strategies integration
- [ ] Web-based game visualization
- [ ] Multi-threading for tournament simulations
- [ ] Advanced statistical analysis tools
- [ ] Export/import game replay functionality
- [ ] Custom board layouts and rule variations
