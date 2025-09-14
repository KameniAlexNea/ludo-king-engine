"""
Heuristic strategy implementations for Ludo.

This module contains basic strategy implementations that use simple
heuristics to make move decisions.
"""

import random
from typing import List, Optional
from .base_strategy import BaseStrategy
from ..core.token import Token


class RandomStrategy(BaseStrategy):
    """Randomly selects from available moves."""
    
    def __init__(self):
        super().__init__("Random")
        
    def choose_move(self, movable_tokens: List[Token], dice_roll: int, game_state: dict) -> Optional[Token]:
        """Randomly choose from available tokens."""
        if not movable_tokens:
            return None
        return random.choice(movable_tokens)


class KillerStrategy(BaseStrategy):
    """Prioritizes capturing opponent tokens."""
    
    def __init__(self):
        super().__init__("Killer")
        
    def choose_move(self, movable_tokens: List[Token], dice_roll: int, game_state: dict) -> Optional[Token]:
        """Choose move that captures opponents, or best alternative."""
        if not movable_tokens:
            return None
            
        # Prioritize moves that can capture opponents
        capture_moves = []
        for token in movable_tokens:
            opponent_tokens = self.get_opponent_tokens_in_range(token, dice_roll, game_state)
            if opponent_tokens:
                capture_moves.append((token, len(opponent_tokens)))
                
        if capture_moves:
            # Choose move that captures the most tokens
            capture_moves.sort(key=lambda x: x[1], reverse=True)
            return capture_moves[0][0]
            
        # No captures possible, choose move that advances furthest
        return max(movable_tokens, key=lambda t: t.steps_taken + dice_roll)


class DefensiveStrategy(BaseStrategy):
    """Prioritizes safe moves and protecting tokens."""
    
    def __init__(self):
        super().__init__("Defensive")
        
    def choose_move(self, movable_tokens: List[Token], dice_roll: int, game_state: dict) -> Optional[Token]:
        """Choose safest move available."""
        if not movable_tokens:
            return None
            
        # Prioritize safe moves
        safe_moves = []
        for token in movable_tokens:
            if self.is_move_safe(token, dice_roll, game_state):
                safe_moves.append(token)
                
        if safe_moves:
            # Among safe moves, choose the one that advances furthest
            return max(safe_moves, key=lambda t: t.steps_taken + dice_roll)
            
        # No safe moves, choose move that advances least-advanced token
        return min(movable_tokens, key=lambda t: t.steps_taken)


class BalancedStrategy(BaseStrategy):
    """Balances offensive and defensive considerations."""
    
    def __init__(self):
        super().__init__("Balanced")
        
    def choose_move(self, movable_tokens: List[Token], dice_roll: int, game_state: dict) -> Optional[Token]:
        """Choose move based on balanced scoring."""
        if not movable_tokens:
            return None
            
        # Score each possible move
        scored_moves = []
        for token in movable_tokens:
            score = self.evaluate_move(token, dice_roll, game_state)
            scored_moves.append((token, score))
            
        # Choose highest scoring move
        scored_moves.sort(key=lambda x: x[1], reverse=True)
        return scored_moves[0][0]
        
    def evaluate_move(self, token: Token, dice_roll: int, game_state: dict) -> float:
        """Evaluate move considering multiple factors."""
        score = 0.0
        
        # Base score for advancing
        score += (token.steps_taken + dice_roll) * 0.1
        
        # Bonus for captures
        opponent_tokens = self.get_opponent_tokens_in_range(token, dice_roll, game_state)
        score += len(opponent_tokens) * 10.0
        
        # Bonus for safe moves
        if self.is_move_safe(token, dice_roll, game_state):
            score += 5.0
            
        # Bonus for getting out of home
        if token.is_at_home() and dice_roll == 6:
            score += 15.0
            
        # Bonus for reaching finish
        if token.steps_taken + dice_roll >= 56:
            score += 20.0
            
        # Penalty for leaving token vulnerable
        # (Simple check - could be improved with more sophisticated analysis)
        if not self.is_move_safe(token, dice_roll, game_state):
            score -= 2.0
            
        return score