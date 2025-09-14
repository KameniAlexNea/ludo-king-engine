from typing import Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFont

from ludo_engine.core.constants import Colors, LudoConstants
from ludo_engine.core.token import TokenState, Token

# Styling - matching matplotlib colors
COLOR_MAP = {
    "red": "#e74c3c",
    "green": "#2ecc71",
    "blue": "#2e86c1",
    "lightblue": "#a9d0f5",
    "yellow": "#f1c40f",
    "white": "#ffffff",
    "black": "#000000",
    "gray": "#808080",
}

# Convert hex colors to RGB tuples for PIL
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# PIL-compatible color map
PIL_COLOR_MAP = {k: hex_to_rgb(v) for k, v in COLOR_MAP.items()}

FONT = None
try:
    FONT = ImageFont.truetype("DejaVuSans.ttf", 14)
except Exception:
    pass

# Basic geometric layout (15x15 grid)
CELL = 32
GRID = 15
BOARD_SIZE = GRID * CELL


# Canonical 52-cell outer path builder aligned to our 15x15 layout
def _build_path_52() -> List[Tuple[int, int]]:
    seq: List[Tuple[int, int]] = []
    # Up column (6,0)->(6,5)
    for r in range(0, 6):
        seq.append((6, r))
    # Left row (5,6)->(0,6)
    for c in range(5, -1, -1):
        seq.append((c, 6))
    # Down column (0,7)->(0,8)
    for r in range(7, 9):
        seq.append((0, r))
    # Right row (1,8)->(5,8)
    for c in range(1, 6):
        seq.append((c, 8))
    # Down column (6,9)->(6,14)
    for r in range(9, 15):
        seq.append((6, r))
    # Right row (7,14)->(8,14)
    for c in range(7, 9):
        seq.append((c, 14))
    # Up column (8,13)->(8,9)
    for r in range(13, 9, -1):
        seq.append((8, r))
    # Right row (9,8)->(14,8)
    for c in range(9, 15):
        seq.append((c, 8))
    # Up column (14,7)->(14,6)
    for r in range(7, 5, -1):
        seq.append((14, r))
    # Left row (13,6)->(9,6)
    for c in range(13, 9, -1):
        seq.append((c, 6))
    # Up column (8,5)->(8,0)
    for r in range(5, -1, -1):
        seq.append((8, r))
    # Left row end (7,0)
    seq.append((7, 0))
    return seq


# Start cells (colored squares on the outer track)
START_CELLS = {
    Colors.RED: (1, 8),
    Colors.GREEN: (8, 13),
    Colors.YELLOW: (13, 6),
    Colors.BLUE: (6, 1),
}


def _rotate_path_to_start(path: List[Tuple[int, int]], start_coord: Tuple[int, int]) -> List[Tuple[int, int]]:
    if start_coord not in path:
        return path
    idx = path.index(start_coord)
    return path[idx:] + path[:idx]


# Build the path once and rotate so RED start is index 0
_PATH52_RAW = _build_path_52()
PATH_LIST: List[Tuple[int, int]] = _rotate_path_to_start(_PATH52_RAW, START_CELLS[Colors.RED])
PATH_LEN = len(PATH_LIST)

# Compute per-color start indices based on their start cells' positions in PATH_LIST
COLOR_START_INDEX = {color: PATH_LIST.index(coord) for color, coord in START_CELLS.items()}


def _cell_bbox(x: int, y: int):
    """Get bounding box for a cell (PIL coordinates)."""
    x0 = x * CELL
    y0 = y * CELL
    return (x0, y0, x0 + CELL, y0 + CELL)


def _draw_base_cells(d: ImageDraw.ImageDraw):
    """Draw the base 15x15 grid with home quadrants."""
    for x in range(GRID):
        for y in range(GRID):
            color = PIL_COLOR_MAP["white"]
            # four 6 by 6 home squares
            if x < 6 and y >= 9:
                color = PIL_COLOR_MAP["red"]
            elif x >= 9 and y >= 9:
                color = PIL_COLOR_MAP["green"]
            elif x < 6 and y < 6:
                color = PIL_COLOR_MAP["lightblue"]
            elif x >= 9 and y < 6:
                color = PIL_COLOR_MAP["yellow"]

            bbox = _cell_bbox(x, y)
            d.rectangle(bbox, fill=color, outline=PIL_COLOR_MAP["black"], width=1)


def _draw_central_triangles(d: ImageDraw.ImageDraw):
    """Draw central triangles inside 3 by 3 center block (cells 6,7,8)."""
    center = (7.5 * CELL, 7.5 * CELL)

    # Bottom triangle (blue) - note: PIL y-coordinates are from top
    tri_bottom = [
        (6 * CELL, 6 * CELL),
        (9 * CELL, 6 * CELL),
        center
    ]
    d.polygon(tri_bottom, fill=PIL_COLOR_MAP["blue"], outline=PIL_COLOR_MAP["black"], width=2)

    # Top triangle (green)
    tri_top = [
        (6 * CELL, 9 * CELL),
        (9 * CELL, 9 * CELL),
        center
    ]
    d.polygon(tri_top, fill=PIL_COLOR_MAP["green"], outline=PIL_COLOR_MAP["black"], width=2)

    # Left triangle (red)
    tri_left = [
        (6 * CELL, 6 * CELL),
        (6 * CELL, 9 * CELL),
        center
    ]
    d.polygon(tri_left, fill=PIL_COLOR_MAP["red"], outline=PIL_COLOR_MAP["black"], width=2)

    # Right triangle (yellow)
    tri_right = [
        (9 * CELL, 6 * CELL),
        (9 * CELL, 9 * CELL),
        center
    ]
    d.polygon(tri_right, fill=PIL_COLOR_MAP["yellow"], outline=PIL_COLOR_MAP["black"], width=2)


def _draw_home_columns(d: ImageDraw.ImageDraw):
    """Draw home columns final lanes."""
    # Red home column
    for x in range(1, 6):
        y = 7
        bbox = _cell_bbox(x, y)
        d.rectangle(bbox, fill=PIL_COLOR_MAP["red"], outline=PIL_COLOR_MAP["black"], width=1)

    # Yellow home column
    for x in range(9, 14):
        y = 7
        bbox = _cell_bbox(x, y)
        d.rectangle(bbox, fill=PIL_COLOR_MAP["yellow"], outline=PIL_COLOR_MAP["black"], width=1)

    # Blue home column
    for y in range(1, 6):
        x = 7
        bbox = _cell_bbox(x, y)
        d.rectangle(bbox, fill=PIL_COLOR_MAP["blue"], outline=PIL_COLOR_MAP["black"], width=1)

    # Green home column
    for y in range(9, 14):
        x = 7
        bbox = _cell_bbox(x, y)
        d.rectangle(bbox, fill=PIL_COLOR_MAP["green"], outline=PIL_COLOR_MAP["black"], width=1)


def _draw_starting_nests(d: ImageDraw.ImageDraw):
    """Draw the four starting nests inside each corner home block as 2 by 2 token spots."""
    nest_offsets = [(1, 1), (4, 1), (1, 4), (4, 4)]  # offsets inside 6 by 6 block

    # Top left red block origin (0,9)
    for ox, oy in nest_offsets:
        cx = (0 + ox + 0.5) * CELL
        cy = (9 + oy + 0.5) * CELL
        radius = int(0.35 * CELL)
        d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                 fill=PIL_COLOR_MAP["red"], outline=PIL_COLOR_MAP["black"], width=2)

    # Top right green block origin (9,9)
    for ox, oy in nest_offsets:
        cx = (9 + ox + 0.5) * CELL
        cy = (9 + oy + 0.5) * CELL
        radius = int(0.35 * CELL)
        d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                 fill=PIL_COLOR_MAP["green"], outline=PIL_COLOR_MAP["black"], width=2)

    # Bottom left blue block origin (0,0)
    for ox, oy in nest_offsets:
        cx = (0 + ox + 0.5) * CELL
        cy = (0 + oy + 0.5) * CELL
        radius = int(0.35 * CELL)
        d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                 fill=PIL_COLOR_MAP["blue"], outline=PIL_COLOR_MAP["black"], width=2)

    # Bottom right yellow block origin (9,0)
    for ox, oy in nest_offsets:
        cx = (9 + ox + 0.5) * CELL
        cy = (0 + oy + 0.5) * CELL
        radius = int(0.35 * CELL)
        d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                 fill=PIL_COLOR_MAP["yellow"], outline=PIL_COLOR_MAP["black"], width=2)


def _draw_arrow_cell(d: ImageDraw.ImageDraw, cell_x: int, cell_y: int, direction: str):
    """Draw entry arrows in white."""
    x = cell_x * CELL
    y = cell_y * CELL

    if direction == "left":
        pts = [(x + 0.75*CELL, y + 0.2*CELL),
               (x + 0.75*CELL, y + 0.8*CELL),
               (x + 0.25*CELL, y + 0.5*CELL)]
    elif direction == "right":
        pts = [(x + 0.25*CELL, y + 0.2*CELL),
               (x + 0.25*CELL, y + 0.8*CELL),
               (x + 0.75*CELL, y + 0.5*CELL)]
    elif direction == "up":
        pts = [(x + 0.2*CELL, y + 0.25*CELL),
               (x + 0.8*CELL, y + 0.25*CELL),
               (x + 0.5*CELL, y + 0.75*CELL)]
    else:  # down
        pts = [(x + 0.2*CELL, y + 0.75*CELL),
               (x + 0.8*CELL, y + 0.75*CELL),
               (x + 0.5*CELL, y + 0.25*CELL)]

    d.polygon(pts, fill=PIL_COLOR_MAP["white"], outline=PIL_COLOR_MAP["black"], width=2)


def _draw_special_squares(d: ImageDraw.ImageDraw):
    """Draw special squares: stars and starting positions."""
    # Mark starting squares on the outer track for each color
    stars = [(6, 11), (11, 8), (8, 3), (3, 6)]
    for sx, sy in stars:
        bbox = _cell_bbox(sx, sy)
        d.rectangle(bbox, fill=PIL_COLOR_MAP["gray"], outline=PIL_COLOR_MAP["black"], width=2)

    # Starting home squares
    start_home = {
        "red": (1, 8),
        "green": (8, 13),
        "yellow": (13, 6),
        "blue": (6, 1),
    }
    for col, (sx, sy) in start_home.items():
        bbox = _cell_bbox(sx, sy)
        d.rectangle(bbox, fill=PIL_COLOR_MAP[col], outline=PIL_COLOR_MAP["black"], width=3)

    # Stars on special safe cells
    star_cells = [(1, 7), (7, 13), (13, 7), (7, 1)]
    for sx, sy in star_cells:
        cx = (sx + 0.5) * CELL
        cy = (sy + 0.5) * CELL
        # Draw a star symbol (simplified as text)
        if FONT:
            d.text((cx - 8, cy - 10), "★", fill=PIL_COLOR_MAP["black"], font=FONT)


def _get_token_position(token: Token) -> Tuple[float, float]:
    """Get the visual position for a token based on the matplotlib implementation."""
    pos = token.position
    tid = token.token_id
    color = token.color
    steps = token.steps_taken

    if token.is_at_home():
        # Token in home nest - use the nest positions from matplotlib
        nest_offsets = [(1, 1), (4, 1), (1, 4), (4, 4)]
        if color == Colors.RED:
            ox, oy = nest_offsets[tid]
            return 0 + ox + 0.5, 9 + oy + 0.5
        elif color == Colors.GREEN:
            ox, oy = nest_offsets[tid]
            return 9 + ox + 0.5, 9 + oy + 0.5
        elif color == Colors.BLUE:
            ox, oy = nest_offsets[tid]
            return 0 + ox + 0.5, 0 + oy + 0.5
        elif color == Colors.YELLOW:
            ox, oy = nest_offsets[tid]
            return 9 + ox + 0.5, 0 + oy + 0.5

    elif token.is_active():
        if steps > LudoConstants.BOARD_SIZE:
            # In home column - position based on progress in home column
            home_steps = steps - LudoConstants.BOARD_SIZE
            if color == Colors.RED:
                # Red home column: x positions 1-5, y=7
                x_pos = 1 + home_steps  # 1, 2, 3, 4, 5
                return x_pos + 0.5, 7.5
            elif color == Colors.GREEN:
                # Green home column: x=7, y positions 13-9
                y_pos = 13 - home_steps  # 13, 12, 11, 10, 9
                return 7.5, y_pos + 0.5
            elif color == Colors.YELLOW:
                # Yellow home column: x positions 13-9, y=7
                x_pos = 13 - home_steps  # 13, 12, 11, 10, 9
                return x_pos + 0.5, 7.5
            elif color == Colors.BLUE:
                # Blue home column: x=7, y positions 1-5
                y_pos = 1 + home_steps  # 1, 2, 3, 4, 5
                return 7.5, y_pos + 0.5
        else:
            # Compute path index from steps and color, aligned to PATH_LIST and START_CELLS
            steps_taken = token.steps_taken
            if steps_taken <= 0:
                # Fallback to position if steps not provided
                base_idx = COLOR_START_INDEX.get(color, 0)
                rel = (pos or 0)
                path_idx = (base_idx + rel) % PATH_LEN
            else:
                base_idx = COLOR_START_INDEX.get(color, 0)
                path_idx = (base_idx + (steps_taken - 1)) % PATH_LEN

            cx, cy = PATH_LIST[path_idx]
            return cx + 0.5, cy + 0.5

    elif token.is_finished():
        # Token finished - place in center triangles
        if color == Colors.RED:
            return 6.5, 7.5  # left triangle
        elif color == Colors.GREEN:
            return 7.5, 8.5  # top triangle
        elif color == Colors.YELLOW:
            return 8.5, 7.5  # right triangle
        elif color == Colors.BLUE:
            return 7.5, 6.5  # bottom triangle

    # Default fallback
    return 7.5, 7.5


def draw_board(tokens: Dict[str, List[Token]], show_ids: bool = True) -> Image.Image:
    """Draw the Ludo board with tokens - exact replica of matplotlib version."""
    img = Image.new("RGB", (BOARD_SIZE, BOARD_SIZE), PIL_COLOR_MAP["white"])
    d = ImageDraw.Draw(img)

    # Draw base cells
    _draw_base_cells(d)

    # Draw central triangles
    _draw_central_triangles(d)

    # Draw home columns
    _draw_home_columns(d)

    # Draw grid lines on top
    for i in range(GRID + 1):
        d.line((0, i * CELL, BOARD_SIZE, i * CELL), fill=PIL_COLOR_MAP["black"], width=1)
        d.line((i * CELL, 0, i * CELL, BOARD_SIZE), fill=PIL_COLOR_MAP["black"], width=1)

    # Draw starting nests
    _draw_starting_nests(d)

    # Draw special squares
    _draw_special_squares(d)

    # Draw arrows adjacent to each home column
    arrow_positions = {
        "red": (6, 7, "left"),
        "green": (7, 8, "up"),
        "yellow": (8, 7, "right"),
        "blue": (7, 6, "down"),
    }
    for _, (ax_x, ax_y, direction) in arrow_positions.items():
        _draw_arrow_cell(d, ax_x, ax_y, direction)

    # Draw tokens
    for color_name, token_list in tokens.items():
        for token in token_list:
            x, y = _get_token_position(token)
            cx = x * CELL
            cy = y * CELL
            radius = int(0.35 * CELL)

            # Draw token circle
            d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                     fill=PIL_COLOR_MAP.get(color_name, PIL_COLOR_MAP["black"]),
                     outline=PIL_COLOR_MAP["black"], width=2)

            # Draw token ID
            if show_ids and FONT:
                tid = token.token_id
                d.text((cx - 5, cy - 8), str(tid), fill=PIL_COLOR_MAP["black"], font=FONT)

    return img
