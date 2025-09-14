"""
Player class representing a game participant.

Each player has 4 tokens, a color, and a strategy for making moves.
The player manages token lifecycle and move decisions.
"""

from typing import List, Optional, TYPE_CHECKING
from .token import Token

if TYPE_CHECKING:
    from ..strategies.base_strategy import BaseStrategy


class Player:
    """
    Represents a player in the Ludo game.
    
    Each player has 4 tokens of their assigned color and uses a strategy
    to make decisions about which moves to make.
    """
    
    def __init__(self, color: str, name: Optional[str] = None, strategy: Optional['BaseStrategy'] = None):
        """
        Initialize a new player.
        
        Args:
            color: Player's color ('red', 'blue', 'green', 'yellow')
            name: Optional player name
            strategy: Strategy to use for move decisions
        """
        self.color = color
        self.name = name or f"Player_{color}"
        self.strategy = strategy
        
        # Create 4 tokens for this player
        self.tokens: List[Token] = [
            Token(token_id=i, color=color) for i in range(4)
        ]
        
        # Game statistics
        self.tokens_finished = 0
        self.tokens_captured = 0
        self.total_moves = 0
        self.sixes_rolled = 0
        
    def get_tokens_at_home(self) -> List[Token]:
        """Get all tokens currently at home."""
        return [token for token in self.tokens if token.is_at_home()]
        
    def get_active_tokens(self) -> List[Token]:
        """Get all tokens currently active on the board."""
        return [token for token in self.tokens if token.is_active()]
        
    def get_finished_tokens(self) -> List[Token]:
        """Get all tokens that have finished."""
        return [token for token in self.tokens if token.is_finished()]
        
    def get_movable_tokens(self, dice_roll: int) -> List[Token]:
        """
        Get all tokens that can move with the given dice roll.
        
        Args:
            dice_roll: The dice roll result (1-6)
            
        Returns:
            List of tokens that can move
        """
        return [token for token in self.tokens if token.can_move(dice_roll)]
        
    def has_won(self) -> bool:
        """Check if this player has won (all 4 tokens finished)."""
        return len(self.get_finished_tokens()) == 4
        
    def can_make_move(self, dice_roll: int) -> bool:
        """Check if player can make any move with the dice roll."""
        return len(self.get_movable_tokens(dice_roll)) > 0
        
    def choose_move(self, dice_roll: int, game_state: dict) -> Optional[Token]:
        """
        Choose which token to move based on strategy.
        
        Args:
            dice_roll: The dice roll result
            game_state: Current game state
            
        Returns:
            Token to move, or None if no move possible
        """
        movable_tokens = self.get_movable_tokens(dice_roll)
        
        if not movable_tokens:
            return None
            
        if self.strategy:
            return self.strategy.choose_move(movable_tokens, dice_roll, game_state)
        else:
            # Default: choose first available token
            return movable_tokens[0]
            
    def set_strategy(self, strategy: 'BaseStrategy'):
        """Set the strategy for this player."""
        self.strategy = strategy
        if hasattr(strategy, 'set_player'):
            strategy.set_player(self)
            
    def update_stats(self, dice_roll: int, move_successful: bool, captured_tokens: List[Token] = None):
        """
        Update player statistics after a move.
        
        Args:
            dice_roll: The dice roll used
            move_successful: Whether the move was successful
            captured_tokens: List of tokens captured by this move
        """
        if dice_roll == 6:
            self.sixes_rolled += 1
            
        if move_successful:
            self.total_moves += 1
            
        if captured_tokens:
            self.tokens_captured += len(captured_tokens)
            
        # Update finished token count
        self.tokens_finished = len(self.get_finished_tokens())
        
    def get_position_summary(self) -> dict:
        """Get a summary of token positions."""
        return {
            'home': len(self.get_tokens_at_home()),
            'active': len(self.get_active_tokens()),
            'finished': len(self.get_finished_tokens()),
            'total': len(self.tokens)
        }
        
    def get_stats(self) -> dict:
        """Get player statistics."""
        return {
            'color': self.color,
            'name': self.name,
            'tokens_finished': self.tokens_finished,
            'tokens_captured': self.tokens_captured,
            'total_moves': self.total_moves,
            'sixes_rolled': self.sixes_rolled,
            'position_summary': self.get_position_summary()
        }
        
    def reset(self):
        """Reset player to initial state."""
        # Reset all tokens
        for token in self.tokens:
            token.send_home()
            
        # Reset statistics
        self.tokens_finished = 0
        self.tokens_captured = 0
        self.total_moves = 0
        self.sixes_rolled = 0
        
    def to_dict(self) -> dict:
        """Convert player to dictionary representation."""
        return {
            'color': self.color,
            'name': self.name,
            'tokens': [token.to_dict() for token in self.tokens],
            'stats': self.get_stats()
        }
        
    @classmethod
    def from_dict(cls, data: dict, strategy: Optional['BaseStrategy'] = None) -> 'Player':
        """Create player from dictionary representation."""
        player = cls(data['color'], data['name'], strategy)
        
        # Restore tokens
        player.tokens = [Token.from_dict(token_data) for token_data in data['tokens']]
        
        # Restore stats
        stats = data.get('stats', {})
        player.tokens_finished = stats.get('tokens_finished', 0)
        player.tokens_captured = stats.get('tokens_captured', 0)
        player.total_moves = stats.get('total_moves', 0)
        player.sixes_rolled = stats.get('sixes_rolled', 0)
        
        return player
        
    def __repr__(self) -> str:
        """String representation of the player."""
        return f"Player({self.name}, {self.color}, tokens_finished={self.tokens_finished})"
        
    def __eq__(self, other) -> bool:
        """Check equality with another player."""
        if not isinstance(other, Player):
            return False
        return self.color == other.color