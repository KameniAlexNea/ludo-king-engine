# Ludo Tournament Configuration Guide

## Overview

The Ludo tournament system now supports flexible configuration through a `.env` file and environment variables. This allows you to customize tournament behavior without modifying code.

## Configuration File

The `.env` file in the project root contains all configuration settings:

```bash
# Tournament Settings
TOURNAMENT_MAX_TURNS=200          # Maximum turns per game
TOURNAMENT_GAMES_PER_MATCH=1      # Games per match
TOURNAMENT_SEED=None              # Random seed (None for random)

# Strategy Settings
DEFAULT_STRATEGIES=random,killer,defensive,balanced

# Game Settings
GAME_MAX_CONSECUTIVE_SIXES=3      # Max consecutive sixes

# Debug Settings
VERBOSE_LOGGING=true              # Enable verbose output
ENABLE_PROFILING=false            # Enable performance profiling
```

## Usage Methods

### 1. Edit .env File (Recommended)

Simply edit the `.env` file to change default settings:

```bash
# For quick tournaments
TOURNAMENT_MAX_TURNS=50
TOURNAMENT_GAMES_PER_MATCH=1

# For thorough tournaments
TOURNAMENT_MAX_TURNS=500
TOURNAMENT_GAMES_PER_MATCH=3
```

### 2. Environment Variables

Override settings using environment variables:

```bash
# Override max turns
TOURNAMENT_MAX_TURNS=100 python examples/tournament_demo.py

# Multiple overrides
TOURNAMENT_MAX_TURNS=50 TOURNAMENT_GAMES_PER_MATCH=2 python examples/tournament_demo.py
```

### 3. Programmatic Configuration

Override in code for specific tournaments:

```python
from ludo_engine.tournament import LudoTournament

# Use config defaults
tournament = LudoTournament(['random', 'killer'])

# Override specific settings
tournament = LudoTournament(
    strategies=['random', 'killer'],
    max_turns=100,
    games_per_match=3
)
```

## Configuration Priority

Settings are loaded in this order (later overrides earlier):

1. **Default values** (hardcoded in code)
2. **`.env` file** (project root)
3. **Environment variables** (highest priority)
4. **Constructor parameters** (highest priority)

## Available Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `TOURNAMENT_MAX_TURNS` | int/None | 200 | Max turns per game (None = unlimited) |
| `TOURNAMENT_GAMES_PER_MATCH` | int | 1 | Number of games per match |
| `TOURNAMENT_SEED` | int/None | None | Random seed for reproducibility |
| `DEFAULT_STRATEGIES` | list | random,killer,defensive,balanced | Default strategies |
| `GAME_MAX_CONSECUTIVE_SIXES` | int | 3 | Max consecutive sixes allowed |
| `VERBOSE_LOGGING` | bool | true | Enable detailed tournament output |
| `ENABLE_PROFILING` | bool | false | Enable performance profiling |

## Examples

### Quick Testing
```bash
# Edit .env
TOURNAMENT_MAX_TURNS=20
TOURNAMENT_GAMES_PER_MATCH=1

# Run tournament
python examples/tournament_demo.py
```

### Thorough Analysis
```bash
# Environment override
TOURNAMENT_MAX_TURNS=500 TOURNAMENT_GAMES_PER_MATCH=5 python examples/tournament_demo.py
```

### Reproducible Results
```bash
# Fixed seed for consistent results
TOURNAMENT_SEED=42 python examples/tournament_demo.py
```

## Benefits

- **Flexible**: Configure without code changes
- **Environment-aware**: Different settings for different environments
- **Override-capable**: Environment variables override file settings
- **Backward compatible**: Existing code continues to work
- **Well-documented**: Clear configuration options