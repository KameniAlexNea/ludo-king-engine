"""
GPT Strategy - Uses OpenAI GPT models for decision making.
"""

import os
from typing import Dict, Optional
from .base import Strategy
from .random_strategy import RandomStrategy


class GPTStrategy(Strategy):
    """Strategy using OpenAI GPT models."""
    
    def __init__(self, model: str = "gpt-4"):
        super().__init__(
            f"GPT-{model}",
            f"Uses OpenAI {model} model for strategic decisions"
        )
        self.model = model
        self.fallback_strategy = RandomStrategy()
        self.client = None
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize OpenAI client."""
        try:
            import openai
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = openai.OpenAI(api_key=api_key)
            else:
                print("OPENAI_API_KEY not found, falling back to random strategy")
        except ImportError:
            print("OpenAI library not found, falling back to random strategy")
            
    def decide(self, game_context: Dict) -> int:
        """Make a decision using GPT."""
        if not self.client:
            return self.fallback_strategy.decide(game_context)
            
        try:
            valid_moves = self._get_valid_moves(game_context)
            prompt = self._create_prompt(game_context, valid_moves)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.1
            )
            
            response_text = response.choices[0].message.content
            token_id = self._parse_response(response_text, valid_moves)
            if token_id is not None:
                return token_id
                
        except Exception as e:
            print(f"GPT strategy error: {e}")
            
        return self.fallback_strategy.decide(game_context)
        
    def _get_system_prompt(self) -> str:
        """Get system prompt for GPT."""
        return """You are an expert Ludo player. Your goal is to win by getting all tokens to finish first.

Key strategies:
1. Get tokens out of home when you roll a 6
2. Prioritize advancing tokens closest to finishing
3. Capture opponent tokens when possible for extra turns
4. Keep tokens in safe positions when threatened
5. Balance aggressive play with defensive positioning

Analyze the game state and respond with just the token number (0, 1, 2, or 3) to move."""
        
    def _create_prompt(self, game_context: Dict, valid_moves: list) -> str:
        """Create prompt describing current game state."""
        dice_roll = game_context.get("dice_roll", 6)
        current_player = game_context.get("current_player", {})
        
        prompt = f"You rolled {dice_roll}. Available moves:\n"
        
        for i, move in enumerate(valid_moves):
            token_id = move["token_id"]
            move_type = move["move_type"]
            captures = move.get("captures_opponent", False)
            safe = move.get("is_safe_move", True)
            
            prompt += f"Token {token_id}: {move_type}"
            if captures:
                prompt += " (captures opponent!)"
            if not safe:
                prompt += " (risky)"
            prompt += "\n"
            
        prompt += "\nWhich token should you move? Respond with just the number."
        return prompt
        
    def _parse_response(self, response: str, valid_moves: list) -> Optional[int]:
        """Parse GPT response to extract token ID."""
        if not response:
            return None
            
        valid_token_ids = [move["token_id"] for move in valid_moves]
        
        # Extract digits from response
        import re
        digits = re.findall(r'\d+', response)
        
        for digit in digits:
            try:
                token_id = int(digit)
                if token_id in valid_token_ids:
                    return token_id
            except ValueError:
                continue
                
        return None