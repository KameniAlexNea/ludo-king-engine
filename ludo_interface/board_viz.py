"""
Board visualization for the Ludo game using PIL/Pillow.

This module provides functionality to draw the Ludo board and visualize
game states including token positions, player colors, and game progress.
"""

from typing import Dict, List, Tuple

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise ImportError("PIL/Pillow is required for board visualization. Install with: pip install Pillow")

from ludo_engine.core.constants import LudoConstants

# Color scheme
COLOR_MAP = {
    'red': (230, 60, 60),
    'green': (60, 170, 90), 
    'yellow': (245, 205, 55),
    'blue': (65, 100, 210),
}

BG_COLOR = (245, 245, 245)
GRID_LINE = (210, 210, 210)
PATH_COLOR = (255, 255, 255)
SAFE_COLOR = (190, 190, 190)
HOME_SHADE = (235, 235, 235)
CENTER_COLOR = (255, 255, 255)

# Try to load a font, fall back to default if not available
FONT = None
try:
    FONT = ImageFont.truetype("DejaVuSans.ttf", 14)
except (OSError, ImportError):
    try:
        FONT = ImageFont.load_default()
    except:
        FONT = None

# Board layout constants
CELL_SIZE = 32
GRID_SIZE = 15
BOARD_SIZE = GRID_SIZE * CELL_SIZE

def _get_board_position(position: int, color: str) -> Tuple[int, int]:
    """
    Convert a logical game position to board coordinates.
    
    Args:
        position: Logical position in the game
        color: Player color
        
    Returns:
        Tuple of (col, row) coordinates on the board grid
    """
    # For simplicity, we'll create a basic board layout
    # This is a simplified version - in a full implementation you'd have
    # a proper mapping of the 56 positions around the board
    
    start_pos = LudoConstants.START_POSITIONS.get(color, 0)
    adjusted_pos = (position - start_pos) % LudoConstants.BOARD_SIZE
    
    # Create a rough circular layout
    positions_per_side = 14
    
    if adjusted_pos < positions_per_side:  # Top side
        return (1 + adjusted_pos, 6)
    elif adjusted_pos < 2 * positions_per_side:  # Right side
        return (14, 7 + (adjusted_pos - positions_per_side))
    elif adjusted_pos < 3 * positions_per_side:  # Bottom side
        return (13 - (adjusted_pos - 2 * positions_per_side), 14)
    else:  # Left side
        return (0, 13 - (adjusted_pos - 3 * positions_per_side))

def _get_home_position(token_id: int, color: str) -> Tuple[int, int]:
    """Get home position for a token based on color and token ID."""
    # Define home quadrants for each color
    home_positions = {
        'red': [(2, 2), (4, 2), (2, 4), (4, 4)],
        'blue': [(10, 2), (12, 2), (10, 4), (12, 4)],
        'green': [(2, 10), (4, 10), (2, 12), (4, 12)],
        'yellow': [(10, 10), (12, 10), (10, 12), (12, 12)],
    }
    
    positions = home_positions.get(color, home_positions['red'])
    return positions[token_id % len(positions)]

def _get_finish_position(color: str) -> Tuple[int, int]:
    """Get finish position for a color in the center."""
    # Center positions for finished tokens
    center_positions = {
        'red': (6, 6),
        'blue': (8, 6),
        'green': (6, 8),
        'yellow': (8, 8),
    }
    return center_positions.get(color, (7, 7))

def draw_board(game_state: Dict, show_ids: bool = True) -> Image.Image:
    """
    Draw the Ludo board with current game state.
    
    Args:
        game_state: Dictionary containing game state with player and token information
        show_ids: Whether to show token IDs on the board
        
    Returns:
        PIL Image of the board
    """
    img = Image.new('RGB', (BOARD_SIZE, BOARD_SIZE), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Draw grid
    for i in range(GRID_SIZE + 1):
        # Vertical lines
        draw.line([(i * CELL_SIZE, 0), (i * CELL_SIZE, BOARD_SIZE)], fill=GRID_LINE)
        # Horizontal lines  
        draw.line([(0, i * CELL_SIZE), (BOARD_SIZE, i * CELL_SIZE)], fill=GRID_LINE)
    
    # Draw home areas for each color
    home_areas = {
        'red': (0, 0, 6 * CELL_SIZE, 6 * CELL_SIZE),
        'blue': (9 * CELL_SIZE, 0, BOARD_SIZE, 6 * CELL_SIZE),
        'green': (0, 9 * CELL_SIZE, 6 * CELL_SIZE, BOARD_SIZE),
        'yellow': (9 * CELL_SIZE, 9 * CELL_SIZE, BOARD_SIZE, BOARD_SIZE),
    }
    
    for color, area in home_areas.items():
        # Draw a subtle background for home areas
        draw.rectangle(area, fill=HOME_SHADE, outline=COLOR_MAP[color], width=2)
    
    # Draw the main path (simplified rectangular path)
    path_cells = []
    
    # Top row
    for i in range(6, 9):
        path_cells.append((i, 6))
    
    # Right column
    for i in range(6, 9):
        path_cells.append((8, i))
        
    # Bottom row  
    for i in range(8, 5, -1):
        path_cells.append((i, 8))
        
    # Left column
    for i in range(8, 5, -1):
        path_cells.append((6, i))
    
    # Draw path cells
    for col, row in path_cells:
        x1, y1 = col * CELL_SIZE, row * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        draw.rectangle([x1, y1, x2, y2], fill=PATH_COLOR, outline=GRID_LINE)
    
    # Draw center finish area
    center_x1, center_y1 = 7 * CELL_SIZE, 7 * CELL_SIZE
    center_x2, center_y2 = center_x1 + CELL_SIZE, center_y1 + CELL_SIZE
    draw.rectangle([center_x1, center_y1, center_x2, center_y2], 
                  fill=CENTER_COLOR, outline=(0, 0, 0), width=2)
    
    # Draw tokens
    players = game_state.get('players', [])
    
    for player in players:
        color = player.get('color', 'red')
        tokens = player.get('tokens', [])
        player_color = COLOR_MAP.get(color, COLOR_MAP['red'])
        
        for token in tokens:
            token_id = token.get('token_id', 0)
            position = token.get('position', 0)
            state = token.get('state', 'home')
            
            if state == 'home':
                col, row = _get_home_position(token_id, color)
            elif state == 'finished':
                col, row = _get_finish_position(color)
            else:  # active
                col, row = _get_board_position(position, color)
            
            # Draw token
            x = col * CELL_SIZE + CELL_SIZE // 4
            y = row * CELL_SIZE + CELL_SIZE // 4
            radius = CELL_SIZE // 3
            
            draw.ellipse([x, y, x + radius * 2, y + radius * 2], 
                        fill=player_color, outline=(0, 0, 0), width=2)
            
            # Draw token ID if requested
            if show_ids and FONT:
                text_x = x + radius - 5
                text_y = y + radius - 7
                draw.text((text_x, text_y), str(token_id), fill=(255, 255, 255), font=FONT)
    
    return img


def tokens_to_dict(game) -> Dict:
    """
    Convert game state to dictionary format for visualization.
    
    Args:
        game: LudoGame instance
        
    Returns:
        Dictionary containing game state information
    """
    game_state = {
        'players': []
    }
    
    for player in game.players:
        player_data = {
            'color': player.color,
            'tokens': []
        }
        
        for token in player.tokens:
            # Get the token state properly
            state = token.state.value if hasattr(token.state, 'value') else str(token.state)
            
            token_data = {
                'token_id': token.token_id,
                'position': token.position,
                'state': state
            }
            player_data['tokens'].append(token_data)
        
        game_state['players'].append(player_data)
    
    return game_state