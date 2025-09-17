from ludo_engine.model import ValidMove, AIDecisionContext

PROMPT = """You are playing Ludo. Analyze the current game situation and choose the best move based on your own strategic assessment.

LUDO RULES & BOARD LAYOUT:
- OBJECTIVE: Move all 4 tokens around the board and into your home column first
- BOARD: 52 positions (0-51) in a circular path
- STARTING: Roll a 6 to move tokens out of home onto your starting square
- MOVEMENT: Move clockwise around the outer path by exact die count

STARTING POSITIONS & HOME ENTRIES:
- Red: Starts at position 1, enters home after position 51
- Green: Starts at position 14, enters home after position 12  
- Yellow: Starts at position 27, enters home after position 25
- Blue: Starts at position 40, enters home after position 38

WRAPAROUND LOGIC:
- After position 51, all colors move to position 0 (except Red who enters home)
- This creates a circular board where 51 connects back to 0

SAFE SQUARES:
- Star squares (safe for everyone): positions 8, 21, 34, 47
- Starting positions (safe for everyone): positions 1, 14, 27, 40
- Home column positions: 100-105 (always safe)

SPECIAL RULES:
- CAPTURING: Landing on opponent's token sends it back to their home (gives extra turn)
- STACKING: Your own tokens can stack together and move as a group (cannot be captured)
- HOME COLUMN: Positions 100-105, move by exact count, finish at position 105
- EXTRA TURNS: Rolling 6, capturing opponent, or getting token home gives extra turn
- WINNING: First to get all 4 tokens to position 105 (finish) wins

GAME SITUATION:
- My progress: {my_progress}/4 tokens finished, {my_home_tokens} at home, {my_active_tokens} active
- Opponents' progress: {opponent_progress} (max: {max_opponent_progress}/4)

AVAILABLE MOVES:
{moves_text}

MOVE TYPES EXPLAINED:
- CAPTURES OPPONENT: This move will send an opponent's token back to their home
- SAFE: This move positions your token in a safe spot where it cannot be captured
- RISKY: This move puts your token in a position where opponents might capture it

Analyze the situation and develop your own strategy (You receive also some strategics values, not always useful).
Consider the current game state, your position relative to opponents, and the potential outcomes of each move.

Choose the token ID (0-3) for your move. Respond with ONLY the token number.

DECISION: """


def create_prompt(game_context: AIDecisionContext, valid_moves: list[ValidMove]) -> str:
    """Create structured prompt for LLM decision making with sanitized data."""
    # valid_moves = self._get_valid_moves(game_context)
    player_state = game_context.player_state
    opponents = game_context.opponents

    # Build moves information safely (data already validated)
    moves_info = []
    for i, move in enumerate(valid_moves):
        token_id = move.token_id
        move_type = move.move_type
        strategic_value = move.strategic_value

        move_desc = f"Token {token_id}: {move_type} (value: {strategic_value:.2f})"  #

        if move.captures_opponent:
            move_desc += " [CAPTURES OPPONENT]"
        if move.is_safe_move:
            move_desc += " [SAFE]"
        else:
            move_desc += " [RISKY]"

        moves_info.append(move_desc)

    # Extract game state data (already validated)
    my_progress = player_state.finished_tokens
    my_home_tokens = player_state.tokens_in_home
    my_active_tokens = max(0, 4 - my_home_tokens - my_progress)

    # Extract opponent data (already validated)
    opponent_progress = [opp.finished_tokens for opp in opponents]
    max_opponent_progress = max(opponent_progress, default=0)

    # Create prompt with validated data
    moves_text = "\n".join(f"{i + 1}. {move}" for i, move in enumerate(moves_info))

    prompt = PROMPT.format(
        my_progress=my_progress,
        my_home_tokens=my_home_tokens,
        my_active_tokens=my_active_tokens,
        opponent_progress=opponent_progress,
        max_opponent_progress=max_opponent_progress,
        moves_text=moves_text,
    )

    return prompt
