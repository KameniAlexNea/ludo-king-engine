# Ludo Database System - Technical Overview

## Project Goal

Build a **Lichess-style open database for Ludo** that can:
1. Store games from various sources (human play, AI tournaments, etc.)
2. Analyze positions and opening sequences
3. Provide statistics and insights
4. Serve as a training data source for ML models

## Architecture

### Core Components

```
ludo_engine/          # Minimal game engine (already complete)
├── game.py          # Game logic, move generation
├── board.py         # Board state management
├── player.py        # Player and token tracking
└── constants.py     # Game configuration

ludo_database/       # Database notation & storage (NEW)
├── notation.py      # LDN (Ludo Database Notation) - PGN-style format
├── models.py        # Data models (GameRecord, PositionStats)
├── storage.py       # Storage backend (JSON/in-memory)
└── extensions.py    # Game class extensions for serialization

ludo_api/            # REST API web service (NEW)
├── app.py          # FastAPI application
├── schemas.py      # Pydantic request/response models
├── examples.py     # Usage examples
└── README.md       # API documentation

ludo_interface/      # Gradio UI (existing, for visualization)
└── board_viz.py    # Board rendering (used by API for images)
```

## Ludo Database Notation (LDN)

Similar to PGN (Portable Game Notation) for chess:

### FEN-like Position Notation

Format: `<current_player> <token_data_per_player>`

Example:
```
r r:0:-1:0:0,r:1:-1:0:0,r:2:-1:0:0,r:3:-1:0:0 g:0:-1:0:0,g:1:-1:0:0,g:2:-1:0:0,g:3:-1:0:0 ...
```

Token format: `color:index:board_index:steps_taken:finished`
- `board_index = -1`: Token in base (not entered)
- `board_index >= 0`: Token on board at that position
- `finished = 1`: Token completed journey

### Move Notation

Format: `<color><token_index><action>[<dice>][x]`

Examples:
- `r0e`: Red token 0 **e**nters (requires dice=6)
- `g2a5`: Green token 2 **a**dvances 5 steps
- `b3a4x`: Blue token 3 advances 4 and captures (**x** = capture)

### Game Record Format (LDN)

```
[Event "Tournament Round 1"]
[Site "Ludo Engine"]
[Date "2025.12.15"]
[Red "Alice"]
[Green "Bob"]
[Yellow "Charlie"]
[Blue "Diana"]
[Result "red wins"]

6:r0e 3:r0a3 6:g0e 6:g0a6 4:r1e 2:g0a2x ...
```

## API Endpoints

### Board Operations

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/board/empty` | GET | Get empty board image |
| `/api/board` | POST | Get board state + legal moves |
| `/api/board/image` | POST | Get board image with state |
| `/api/move` | POST | Apply move to state |

### Game Database

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/games` | POST | Create game record |
| `/api/games/{id}` | GET | Get specific game |
| `/api/games/query` | POST | Search games |
| `/api/positions/stats` | POST | Get position statistics |
| `/api/stats` | GET | Database summary |

### Configuration

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/colors` | GET | Available player colors |
| `/api/config` | GET | Game configuration |

## Key Features

### 1. Position Serialization
- Convert any game state to/from FEN notation
- Enables position sharing and analysis
- Supports partial game reconstruction

### 2. Move Application
- Given: position (FEN) + dice + move notation
- Returns: new position + validity + metadata
- Core functionality for database API

### 3. Game Storage
- Store complete games with metadata
- Track player names, events, dates
- Compute statistics per position

### 4. Position Analysis
- Track how many times each position reached
- Win rates from specific positions
- Most common moves from each position

### 5. Board Visualization
- Generate PNG images of any position
- Empty board for documentation
- Position-specific board states

## Database Schema

### GameRecord
```python
{
  "game_id": "uuid",
  "event": "Tournament Name",
  "players": {"red": "Alice", "green": "Bob", ...},
  "starting_fen": "...",
  "moves": [
    {
      "move_number": 1,
      "player_color": "red",
      "dice_value": 6,
      "action": "enter",
      "token_index": 0,
      "fen_after": "..."
    },
    ...
  ],
  "result": "red wins",
  "winner_color": "red"
}
```

### PositionStats
```python
{
  "fen": "...",
  "position_hash": "abc123...",
  "times_reached": 42,
  "wins": {"red": 10, "green": 8, ...},
  "moves_played": {"r0e": 15, "g1a4": 12, ...},
  "move_wins": {"r0e": 8, "g1a4": 6, ...}
}
```

## Usage Examples

### Start the API Server
```bash
python -m ludo_api.app
# Visit http://localhost:8000/docs for interactive API docs
```

### Python Client
```python
import requests

BASE = "http://localhost:8000"

# Get initial board state
r = requests.post(f"{BASE}/api/board", json={})
fen = r.json()["fen"]

# Apply a move
r = requests.post(f"{BASE}/api/move", json={
    "fen": fen,
    "dice": 6,
    "move": "r0e"
})
print(r.json()["fen_after"])

# Create game record
r = requests.post(f"{BASE}/api/games", json={
    "players": {"red": "Alice", "green": "Bob"},
    "event": "Test Game"
})
game_id = r.json()["game_id"]
```

### JavaScript/TypeScript
```typescript
const BASE_URL = "http://localhost:8000";

// Get board state
const response = await fetch(`${BASE_URL}/api/board`, {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({})
});
const state = await response.json();

// Apply move
const moveResult = await fetch(`${BASE_URL}/api/move`, {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({
    fen: state.fen,
    dice: 6,
    move: "r0e"
  })
});
```

## Future Enhancements

### Phase 2: Advanced Database Features
1. **Opening Explorer**: Analyze first N moves, win rates per opening
2. **Player Statistics**: ELO ratings, win rates, favorite strategies
3. **Position Search**: Find games containing specific positions
4. **Bulk Import**: Import games from various formats

### Phase 3: Machine Learning Integration
1. **Training Data Export**: Convert games to ML-friendly formats
2. **Position Evaluation API**: Endpoint for position scoring
3. **Move Recommendation**: Suggest moves based on database statistics
4. **Strategy Classification**: Identify playing styles from game data

### Phase 4: Production Database
1. **PostgreSQL Backend**: Replace JSON storage
2. **Redis Caching**: Fast position lookups
3. **Full-text Search**: Search game metadata
4. **Compression**: Compact FEN storage for millions of games

### Phase 5: Advanced Features
1. **Live Game Streaming**: WebSocket API for real-time games
2. **Tournament Management**: Multi-round event tracking
3. **Puzzle Generation**: Find interesting positions
4. **Analysis Board**: Interactive position analysis UI

## Comparison to Lichess Database

| Feature | Lichess (Chess) | Ludo Database |
|---------|----------------|---------------|
| Notation | PGN | LDN (Ludo Database Notation) |
| Position | FEN | FEN-like (custom) |
| Move Format | Algebraic | Color+Token+Action |
| API | REST + WebSocket | REST (WebSocket planned) |
| Storage | PostgreSQL | JSON (PostgreSQL planned) |
| Analysis | Engine evaluation | Statistical (engine planned) |
| Scale | Billions of games | Thousands → millions |

## Integration Points

### With Existing Tournament System
```python
from ludo_database.storage import get_database
from ludo_database.models import MoveRecord

# In tournament runner
db = get_database()
game_record = db.create_game(
    players={"red": "Strategy1", "green": "Strategy2"},
    starting_fen=game_to_fen(game)
)

# After each move
db.add_move(game_record.game_id, MoveRecord(...))

# At end of game
db.finish_game(game_record.game_id, winner_color="red")
```

### With Gradio Interface
- Gradio UI already uses `ludo_interface.board_viz` for rendering
- API reuses the same rendering pipeline
- Can embed API calls in Gradio for automatic game recording

## Installation & Dependencies

```bash
# Core dependencies (already installed)
pip install pillow

# API dependencies
pip install fastapi uvicorn pydantic

# Or install all at once
pip install -r requirements-api.txt
```

## Testing

```bash
# Test core functionality
python test_database.py

# Test API (with server running)
python ludo_api/examples.py

# Run full test suite
pytest tests/
```

## License

Same as parent project (see LICENSE file).

---

## Quick Start Checklist

- [x] Design LDN notation system
- [x] Implement FEN serialization/deserialization
- [x] Create FastAPI application
- [x] Add board state endpoints
- [x] Add move application endpoint
- [x] Add board image endpoints
- [x] Design database schema
- [x] Implement in-memory storage
- [x] Add game CRUD endpoints
- [x] Add position statistics
- [ ] Add PostgreSQL backend
- [ ] Add opening explorer
- [ ] Add player statistics
- [ ] Deploy production instance

## Contact & Contributing

For questions or contributions, see the main project README.
