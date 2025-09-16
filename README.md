# Ludo King Engine

[![CI](https://github.com/KameniAlexNea/ludo-king-engine/actions/workflows/test-ci.yml/badge.svg)](https://github.com/KameniAlexNea/ludo-king-engine/actions/workflows/test-ci.yml)
[![Coverage](https://codecov.io/gh/KameniAlexNea/ludo-king-engine/branch/main/graph/badge.svg)](https://codecov.io/gh/KameniAlexNea/ludo-king-engine)

A comprehensive Python implementation of the classic Ludo board game, featuring sophisticated AI strategies and an interactive web-based interface. This pure Python engine is designed for reinforcement learning, strategy research, and educational gameplay, offering multiple built-in AI strategies alongside modern visualization tools for strategy analysis and comparison.

## ✨ Key Features

- **🐍 Pure Python Implementation** — Zero external dependencies for the core game engine
- **🌐 Interactive Web Interface** — Gradio-powered visualizer for real-time gameplay and analysis
- **🎯 Deterministic Gameplay** — Reproducible game sessions with comprehensive seed support
- **🧠 Extensible AI Framework** — Rich strategy system with 10+ sophisticated AI implementations
- **🏗️ Clean Architecture** — Modular design separating game mechanics from AI strategies
- **📊 Advanced Analytics** — Detailed game state tracking with comprehensive statistics
- **🏆 Tournament System** — Multi-game competition framework featuring league-style tables
- **🎬 Real-time Visualization** — Step-by-step game playback with animated token movement
- **⚔️ Strategy Benchmarking** — Built-in tools for comparing AI performance across multiple metrics

## 🎮 Core Components

### Game Mechanics
- **🎲 Board System** — 56-position game board with strategic safe zones and home columns
- **🔴 Token Management** — Individual game pieces with advanced position and state tracking
- **👤 Player Framework** — Comprehensive player management with token lifecycle and performance statistics
- **⚙️ Game Engine** — Robust game flow controller managing turns, rules, and game state

### AI Strategy Framework
- **🎯 Heuristic Strategies** — Fundamental approaches including Random, Killer, Defensive, and Balanced tactics
- **🧠 Advanced Algorithms** — Sophisticated strategies like Cautious, Optimist, Winner, and multiple Probabilistic variants
- **🤖 LLM Integration** — Extensible framework ready for Large Language Model-driven strategies
- **🏭 Strategy Factory** — Streamlined instantiation and management system for all AI strategies

## 🚀 Quick Start Guide

### Launch the Web Interface

Get started with the interactive web interface in just a few commands:

```bash
# Install optional dependencies for web interface
pip install gradio pillow

# Launch the interactive web application
python main.py
```

The web interface automatically opens at `http://localhost:7860` and provides:

- **🎮 Interactive Gameplay** — Step-by-step game visualization with smooth token animations
- **🎯 Strategy Selection** — Choose from 10+ AI strategies for each player
- **🏆 Tournament Mode** — Automated multi-game competitions with detailed league tables
- **📈 Real-time Analytics** — Live game statistics and comprehensive move history tracking

### Programmatic Usage

Create and run games programmatically with full control over strategies and game flow:

```python
from ludo_engine import LudoGame, StrategyFactory
from ludo_engine.player import PlayerColor

# Initialize a new game with four players
game = LudoGame(
    player_colors=[PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.YELLOW]
)

# Configure AI strategies for each player
strategies = ['random', 'killer', 'defensive', 'balanced']
for i, strategy_name in enumerate(strategies):
    strategy = StrategyFactory.create_strategy(strategy_name)
    game.players[i].set_strategy(strategy)

# Execute a complete game and analyze results
results = game.play_game()
print(f"🏆 Winner: {results['winner']}")
print(f"⏱️ Game Duration: {results['turns_played']} turns")
```

## 🧠 Available AI Strategies

Our comprehensive strategy library includes algorithms ranging from simple heuristics to advanced probabilistic models:

| Strategy | Approach | Description |
|----------|----------|-------------|
| **Random** | Baseline | Randomly selects from all available legal moves |
| **Killer** | Aggressive | Prioritizes capturing opponent tokens above all else |
| **Defensive** | Conservative | Emphasizes safe moves and token protection |
| **Balanced** | Hybrid | Balances offensive and defensive considerations |
| **Cautious** | Risk-Averse | Extremely conservative, minimizes all forms of risk |
| **Optimist** | Risk-Taking | Aggressive approach with calculated risk acceptance |
| **Winner** | Goal-Oriented | Focuses on advancing tokens to finish line efficiently |
| **Probabilistic** | Mathematical | Uses probability calculations for optimal decision making |
| **ProbabilisticV2/V3** | Advanced Math | Enhanced probabilistic models with refined algorithms |
| **WeightedRandom** | Stochastic | Intelligent sampling with strategic weight distributions |
| **HybridProb** | Multi-Method | Combines multiple evaluation techniques for robust decisions |

## 🌐 Web Interface Features

The sophisticated web interface transforms strategy analysis into an interactive experience:

### Core Functionality
- **🎮 Interactive Gameplay** — Step-by-step game visualization with smooth, animated token movement
- **🤖 Strategy Selection** — Choose from 10+ AI strategies for each player with detailed descriptions
- **🏆 Tournament Mode** — Automated multi-game competitions with comprehensive league tables
- **📊 Real-time Statistics** — Live tracking of wins, game duration, and detailed performance metrics

### Advanced Features
- **🔄 Game State Management** — Save and load complete game states for in-depth analysis
- **📈 Move History Analysis** — Review complete game history with detailed move descriptions and reasoning
- **🎲 Automated Gameplay** — Run games automatically with configurable speed and pause controls
- **📱 Responsive Design** — Seamless experience across desktop and mobile browsers

### Getting Started with the Interface

*Launch the interface with `python main.py` to explore these interactive features firsthand.*

## 📊 Tournament Performance Analysis

Our comprehensive tournament system demonstrates the effectiveness of different AI strategies through large-scale competition. The following results showcase performance across 132 matches with 20 games per match in a league format:

### Tournament Configuration
```
🎮 LUDO STRATEGY TOURNAMENT
==================================================
🎛️ Configuration Details:
   Max turns per game: 500
   Games per match: 20
   Competing strategies: 12 different AI algorithms
   Format: Home and away league system
   Total games played: 2,640

🏁 Tournament Results Summary
```

### Final League Standings

| Pos | Strategy        | P   | W   | D   | L   | GF  | GA  | GD   | Pts  | Win%  | Award |
|-----|-----------------|-----|-----|-----|-----|-----|-----|------|------|-------|-------|
| 1   | probabilistic_v2 | 22  | 17  | 4   | 1   | 17  | 1   | +16  | 55   | 77.3% | 🥇    |
| 2   | probabilistic_v3 | 22  | 18  | 1   | 3   | 18  | 3   | +15  | 55   | 81.8% | 🥈    |
| 3   | probabilistic   | 22  | 16  | 4   | 2   | 16  | 2   | +14  | 52   | 72.7% | 🥉    |
| 4   | hybrid_prob     | 22  | 15  | 3   | 4   | 15  | 4   | +11  | 48   | 68.2% |       |
| 5   | killer          | 22  | 13  | 3   | 6   | 13  | 6   | +7   | 42   | 59.1% |       |
| 6   | cautious        | 22  | 12  | 2   | 8   | 12  | 8   | +4   | 38   | 54.5% |       |
| 7   | defensive       | 22  | 9   | 1   | 12  | 9   | 12  | -3   | 28   | 40.9% |       |
| 8   | balanced        | 22  | 8   | 0   | 14  | 8   | 14  | -6   | 24   | 36.4% |       |
| 9   | winner          | 22  | 7   | 1   | 14  | 7   | 14  | -7   | 22   | 31.8% |       |
| 10  | optimist        | 22  | 4   | 1   | 17  | 4   | 17  | -13  | 13   | 18.2% |       |
| 11  | random          | 22  | 1   | 1   | 20  | 1   | 20  | -19  | 4    | 4.5%  |       |
| 12  | weighted_random | 22  | 1   | 1   | 20  | 1   | 20  | -19  | 4    | 4.5%  | 🔻    |

**Legend:** P=Played, W=Won, D=Draw, L=Lost, GF=Goals For, GA=Goals Against, GD=Goal Difference

### Key Tournament Insights

#### 🏆 Champion Analysis
- **Winner:** `probabilistic_v2` with 55 points from 22 games
- **Win Rate:** 77.3% demonstrating exceptional consistency
- **Performance:** Dominated through mathematical optimization

#### � Strategic Performance Tiers

**🥇 Elite Tier (70%+ win rate)**
- **Probabilistic Dominance:** Three probabilistic variants secured the top positions
  - `probabilistic_v2`: 77.3% win rate (Champion)
  - `probabilistic_v3`: 81.8% win rate (Runner-up)
  - `probabilistic`: 72.7% win rate (Third place)

**🥈 Competitive Tier (50-70% win rate)**
- **Hybrid Excellence:** `hybrid_prob` (68.2%) shows strong potential through multi-method evaluation
- **Aggressive Success:** `killer` (59.1%) and `cautious` (54.5%) demonstrate effective specialized approaches

**🥉 Developing Tier (<50% win rate)**
- **Conservative Challenges:** `winner` (31.8%) and `optimist` (18.2%) struggled with risk management
- **Baseline Performance:** Random strategies (`random` and `weighted_random` both at 4.5%) performed as expected

#### 🔍 Statistical Significance
- **Total Matches:** 132 comprehensive matchups ensuring robust statistical validity
- **Draw Rate:** 11 draws (8.3%) indicating decisive strategic differentiation
- **Average Game Length:** 151.6 turns demonstrating balanced game pacing
- **Clear Differentiation:** Results show definitive strategic hierarchy across all performance tiers

## 🎯 Game Rules & Mechanics

### Core Gameplay
- **🎲 Player Count:** Supports 2-4 players with standard Ludo rules
- **🏠 Starting Position:** Each player begins with 4 tokens in their home base
- **🚀 Token Activation:** Roll a 6 to move tokens from home to the starting position
- **🏁 Victory Condition:** First player to move all 4 tokens to the finish area wins
- **📏 Journey Length:** 57 steps required per token (1 to start + 56 around the board)

### Special Rules
- **⚡ Bonus Turns:** Rolling a 6 or capturing an opponent token grants an additional turn
- **🎯 Token Capture:** Land on opponent tokens to send them back to home (except on safe positions)
- **🛡️ Safe Zones:** Designated safe positions where tokens cannot be captured
- **🚫 Six Limit:** Maximum of 3 consecutive sixes before turn automatically ends
- **🏆 Finish Strategy:** Tokens must reach the center finish area to complete the game

## 📚 Code Examples & Usage Patterns

### Basic Game Setup

Start with a simple two-player game to understand the fundamentals:

```python
from ludo_engine import LudoGame, StrategyFactory
from ludo_engine.player import PlayerColor

# Initialize a basic two-player game
game = LudoGame([PlayerColor.RED, PlayerColor.BLUE])

# Configure AI strategies for each player
strategies = ['random', 'killer']
for i, strategy_name in enumerate(strategies):
    strategy = StrategyFactory.create_strategy(strategy_name)
    game.players[i].set_strategy(strategy)

# Execute the game and get results
results = game.play_game()
print(f"🏆 Game completed! Winner: {results.get('winner', 'No winner')}")
```

### Strategy Performance Comparison

Analyze and compare different AI strategies across multiple games:

```python
from ludo_engine import LudoGame, StrategyFactory
from ludo_engine.player import PlayerColor

# Define strategies to compare
strategies = ['random', 'killer', 'defensive', 'balanced']
performance_metrics = {strategy: 0 for strategy in strategies}

# Run 100 games for statistical significance
for game_round in range(100):
    game = LudoGame([PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.YELLOW])
    
    # Assign strategies to players
    for player_index, strategy_name in enumerate(strategies):
        strategy = StrategyFactory.create_strategy(strategy_name)
        game.players[player_index].set_strategy(strategy)
    
    # Play game and record results
    results = game.play_game()
    
    if results.get('winner'):
        # Identify winning strategy
        for player in game.players:
            if player.color.value == results['winner']:
                performance_metrics[player.strategy.name.lower()] += 1
                break

print("📊 Strategy Performance Analysis:")
for strategy, wins in performance_metrics.items():
    win_rate = (wins / 100) * 100
    print(f"   {strategy.capitalize()}: {wins}/100 wins ({win_rate:.1f}%)")
```

### Custom Strategy Development

Create and integrate your own AI strategy:

```python
from ludo_engine.strategies import BaseStrategy
from ludo_engine.player import PlayerColor
from ludo_engine import LudoGame, StrategyFactory

class CustomStrategy(BaseStrategy):
    """Example custom strategy implementation."""
    
    def __init__(self):
        super().__init__("CustomStrategy")
    
    def choose_move(self, movable_tokens, dice_roll, game_state):
        """
        Implement your strategic logic here.
        
        Args:
            movable_tokens: List of tokens that can be moved
            dice_roll: Current dice value
            game_state: Current state of the game
            
        Returns:
            Selected token to move or None if no move possible
        """
        # Example: Prioritize tokens closest to finish
        if movable_tokens:
            return max(movable_tokens, key=lambda token: token.position)
        return None

# Register your custom strategy
StrategyFactory.register_strategy('custom_strategy', CustomStrategy)

# Use your strategy in a game
game = LudoGame([PlayerColor.RED, PlayerColor.BLUE])
strategies = ['custom_strategy', 'balanced']

for i, strategy_name in enumerate(strategies):
    strategy = StrategyFactory.create_strategy(strategy_name)
    game.players[i].set_strategy(strategy)

results = game.play_game()
print(f"🎯 Custom strategy game result: {results.get('winner', 'Draw')}")
```

### Advanced Game Analysis

Monitor game progression with detailed turn-by-turn analysis:

```python
from ludo_engine import LudoGame, StrategyFactory
from ludo_engine.player import PlayerColor

# Setup game for detailed analysis
game = LudoGame([PlayerColor.RED, PlayerColor.BLUE])
strategies = ['balanced', 'probabilistic']

for i, strategy_name in enumerate(strategies):
    strategy = StrategyFactory.create_strategy(strategy_name)
    game.players[i].set_strategy(strategy)

# Initialize game and track progress
game.start_game()
turn_counter = 0

print("🔍 Detailed Game Analysis:")
print("=" * 50)

while not game.is_finished():
    current_player = game.get_current_player()
    turn_result = game.play_turn()
    turn_counter += 1
    
    # Log turn details
    print(f"Turn {turn_counter:3d} | Player {current_player.color.value:6s}: "
          f"Rolled {turn_result.get('dice_roll', 'N/A'):2d} | "
          f"Move: {turn_result.get('move_made', 'No move')}")
    
    # Highlight special events
    if turn_result.get('captured_tokens'):
        captured_count = len(turn_result['captured_tokens'])
        print(f"         🎯 Captured {captured_count} opponent token(s)!")
    
    if turn_result.get('dice_roll') == 6:
        print(f"         🎲 Bonus turn earned!")

# Display final results
final_results = game.get_game_results()
print("=" * 50)
print(f"🏁 Game completed in {turn_counter} turns")
print(f"🏆 Winner: {final_results.get('winner', 'No winner determined')}")
```

## 🎯 Use Cases & Applications

### 🤖 Reinforcement Learning & AI Research
- **🧠 State Representation** — Complete game state available as structured dictionaries for ML models
- **⚡ Action Space** — Clear move choices with intelligent valid action filtering
- **🏆 Reward Engineering** — Rich reward signals including win/loss, captures, and progress tracking
- **🔬 Reproducible Research** — Deterministic gameplay with comprehensive seed support for consistent experiments

### 📊 Strategy Research & Analysis
- **⚖️ A/B Testing Framework** — Systematic comparison of strategy performance across multiple metrics
- **🏆 Tournament Systems** — Large-scale multi-strategy competitions with statistical significance
- **📈 Performance Analytics** — Detailed game statistics and comprehensive performance tracking
- **🔧 Custom Algorithm Development** — Easy implementation and testing of novel strategic approaches

### 🎓 Educational Applications
- **🎲 Game Theory Studies** — Practical exploration of strategic decision making and Nash equilibria
- **📊 Probability & Statistics** — Analysis of dice roll impacts, risk assessment, and outcome prediction
- **💻 AI Development Learning** — Hands-on experience with game AI programming and algorithm design
- **🔍 Algorithm Comparison** — Benchmarking different approaches to understand performance characteristics

## 🏗️ Project Architecture

The project follows a clean, modular architecture separating concerns for maintainability and extensibility:

```
📁 ludo_engine/                    # 🎮 Core game engine (pure Python)
├── 🎯 board.py                    # Game board logic and position management
├── 🔴 token.py                    # Token mechanics and state management  
├── 👤 player.py                   # Player management and statistics
├── ⚙️ game.py                     # Main game engine and turn management
├── 📊 model.py                    # Data models and type definitions
├── 🔧 constants.py                # Game constants and configuration
├── 🏭 strategy.py                 # Strategy factory and base classes
└── 📁 strategies/                 # 🧠 AI strategy implementations
    ├── 🎯 base.py                 # Base strategy class and interfaces
    ├── 🛠️ utils.py                # Strategy utility functions
    ├── 🎲 random_strategy.py      # Random decision making
    ├── ⚖️ balanced.py             # Balanced offensive/defensive approach
    ├── 🛡️ cautious.py             # Risk-averse conservative strategy
    ├── 🔒 defensive.py            # Defensive token protection
    ├── ⚔️ killer.py               # Aggressive capture-focused strategy
    ├── 🚀 optimist.py             # Risk-taking aggressive approach
    ├── 🏆 winner.py               # Goal-oriented finishing strategy
    ├── 📊 probabilistic*.py       # Mathematical probability-based strategies
    ├── 🎯 weighted_random.py      # Intelligent stochastic sampling
    └── 📁 llm/                    # 🤖 LLM-powered strategies
        ├── 💬 prompt.py           # LLM prompt engineering
        └── 🧠 strategy.py         # LLM integration framework

📁 ludo_interface/                 # 🌐 Web interface (optional)
├── 🖥️ app.py                     # Main Gradio application
└── 🎨 board_viz.py               # Board visualization utilities

📁 tests/                         # 🧪 Comprehensive test suite
├── 📋 __init__.py                # Test package initialization
├── 🎯 test_board.py              # Board mechanics validation
├── ⚙️ test_game.py               # Game engine functionality tests
├── 🔗 test_integration.py        # End-to-end integration tests
├── 👤 test_player.py             # Player management verification
├── 🧠 test_strategies.py         # AI strategy validation
├── 🏭 test_strategy.py           # Strategy framework tests
└── 🔴 test_token.py              # Token mechanics verification

📁 examples/                      # 📚 Usage examples and demos
├── ⚙️ config.py                 # Configuration examples and templates
├── 🏆 tournament.py              # Tournament setup and management
└── 🎮 tournament_demo.py         # Interactive tournament demonstration

📄 main.py                        # 🚀 Entry point for web interface
```

### 🔧 Design Principles

- **🎯 Separation of Concerns** — Game mechanics, AI strategies, and interface are cleanly separated
- **🔌 Extensible Framework** — Easy addition of new strategies through factory pattern
- **🧪 Comprehensive Testing** — Full test coverage ensuring reliability and correctness
- **📊 Data-Driven Design** — Rich data models supporting analysis and debugging
- **🌐 Modular Interface** — Optional web interface doesn't impact core engine performance

## 📋 Requirements & Installation

### System Requirements
- **🐍 Python:** Version 3.7 or higher
- **🎮 Core Engine:** Zero external dependencies (pure Python implementation)
- **🌐 Web Interface:** `gradio` and `pillow` (optional for visualization features)

### 🚀 Quick Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/KameniAlexNea/ludo-king-engine.git
   cd ludo-king-engine
   ```

2. **Install Optional Dependencies** (for web interface)
   ```bash
   pip install gradio pillow
   ```

3. **Verify Installation** with comprehensive test suite
   ```bash
   python -m unittest discover -s tests
   ```

4. **Launch Web Interface** 
   ```bash
   python main.py
   ```

5. **Explore Examples** and tutorials
   ```bash
   python examples/tournament_demo.py
   ```

### 🎯 Getting Started Tips

- **Core Engine Only:** No installation required beyond Python 3.7+
- **Full Experience:** Install optional dependencies for complete feature access
- **Development Setup:** Run tests to ensure everything works correctly
- **Learning Path:** Start with examples to understand the framework capabilities

## 🤝 Contributing to the Project

We welcome contributions from the community! Here's how you can get involved:

### 📝 Development Workflow

1. **🍴 Fork the Repository**
   ```bash
   # Create your own fork on GitHub
   ```

2. **🌟 Create a Feature Branch**
   ```bash
   git checkout -b feature/amazing-new-feature
   ```

3. **💻 Implement Your Changes**
   - Follow existing code style and patterns
   - Add comprehensive tests for new functionality
   - Update documentation as needed

4. **✅ Commit Your Changes**
   ```bash
   git commit -m 'Add amazing new feature with comprehensive tests'
   ```

5. **🚀 Push to Your Branch**
   ```bash
   git push origin feature/amazing-new-feature
   ```

6. **🔄 Open a Pull Request**
   - Provide clear description of changes
   - Reference any related issues
   - Ensure all tests pass

### 🎯 Contribution Areas

- **🧠 New AI Strategies:** Implement novel algorithms and strategic approaches
- **🐛 Bug Fixes:** Report and fix issues in the codebase
- **📚 Documentation:** Improve guides, examples, and API documentation
- **🧪 Testing:** Expand test coverage and add edge case validation
- **🌐 Interface Enhancements:** Improve web interface and visualization features

---

## 📄 License

This project is licensed under the **Apache License** - see the [LICENSE](LICENSE) file for complete details.

---

## 🗺️ Development Roadmap

### ✅ Completed Features
- [x] **🌐 Web-based Game Visualization** — Interactive interface with real-time gameplay

### 🚧 In Development
- [ ] **🤖 LLM-powered Strategy Integration** — Advanced AI using large language models
- [ ] **⚡ Multi-threading Tournament Simulations** — Parallel processing for faster competitions
- [ ] **📊 Advanced Statistical Analysis Tools** — Enhanced performance metrics and insights

### 🔮 Future Enhancements
- [ ] **💾 Export/Import Game Replay Functionality** — Save and analyze complete game sessions
- [ ] **🎨 Custom Board Layouts & Rule Variations** — Flexible game configuration options
- [ ] **📱 Enhanced Mobile-Responsive Interface** — Optimized mobile gaming experience
- [ ] **🎓 Strategy Training Mode for Reinforcement Learning** — Dedicated RL training environment

---

*Ready to start playing? Launch the web interface with `python main.py` and explore the fascinating world of AI strategy competition!* 🎮✨
