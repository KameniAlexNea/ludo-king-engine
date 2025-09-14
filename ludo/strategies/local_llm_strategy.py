"""
Local LLM Strategy - Uses local LLM models (Ollama, vLLM, etc.) for decision making.
"""

import os
import requests
from typing import Dict, Optional
from .base import Strategy
from .random_strategy import RandomStrategy


class LocalLLMStrategy(Strategy):
    """Strategy using local LLM models (e.g., Ollama, vLLM)."""
    
    def __init__(self, model: str = "llama2", endpoint: str = "http://localhost:11434"):
        super().__init__(
            f"Local-{model}",
            f"Uses local {model} model for strategic decisions"
        )
        self.model = model
        self.endpoint = endpoint
        self.fallback_strategy = RandomStrategy()
        
    def decide(self, game_context: Dict) -> int:
        """Make a decision using local LLM."""
        try:
            valid_moves = self._get_valid_moves(game_context)
            prompt = self._create_prompt(game_context, valid_moves)
            
            # Try Ollama API format first
            response_text = self._query_ollama(prompt)
            if not response_text:
                # Try vLLM/OpenAI-compatible format
                response_text = self._query_openai_compatible(prompt)
                
            if response_text:
                token_id = self._parse_response(response_text, valid_moves)
                if token_id is not None:
                    return token_id
                    
        except Exception as e:
            print(f"Local LLM strategy error: {e}")
            
        return self.fallback_strategy.decide(game_context)
        
    def _query_ollama(self, prompt: str) -> Optional[str]:
        """Query using Ollama API format."""
        try:
            url = f"{self.endpoint}/api/generate"
            data = {
                "model": self.model,
                "prompt": f"{self._get_system_prompt()}\n\n{prompt}",
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 100
                }
            }
            
            response = requests.post(url, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
        except requests.RequestException:
            pass
        return None
        
    def _query_openai_compatible(self, prompt: str) -> Optional[str]:
        """Query using OpenAI-compatible API format (vLLM, etc.)."""
        try:
            url = f"{self.endpoint}/v1/completions"
            data = {
                "model": self.model,
                "prompt": f"{self._get_system_prompt()}\n\n{prompt}",
                "max_tokens": 100,
                "temperature": 0.1,
                "stream": False
            }
            
            response = requests.post(url, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                choices = result.get("choices", [])
                if choices:
                    return choices[0].get("text", "")
        except requests.RequestException:
            pass
        return None
        
    def _get_system_prompt(self) -> str:
        """Get system prompt for local LLM."""
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
        """Parse local LLM response to extract token ID."""
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