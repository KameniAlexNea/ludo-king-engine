"""
Unit tests for LLM Strategy implementation.
Tests cover LLM integration, response parsing, and fallback behavior.
"""

import json
import unittest
import unittest.mock
from unittest.mock import MagicMock, patch

from ludo_engine.model import (
    AIDecisionContext,
    CurrentSituation,
    OpponentInfo,
    PlayerState,
    StrategicAnalysis,
    ValidMove,
)
from ludo_engine.strategies.llm.prompt import create_prompt
from ludo_engine.strategies.llm.strategy import LLMStrategy


def create_test_decision_context(dice_value=4, valid_moves=None):
    """Create a test AIDecisionContext for LLM strategy testing."""
    if valid_moves is None:
        valid_moves = [
            ValidMove(
                token_id=0,
                current_position=5,
                current_state="active",
                target_position=9,
                move_type="advance_main_board",
                is_safe_move=False,
                captures_opponent=False,
                captured_tokens=[],
                strategic_value=5.0,
                strategic_components={},
            ),
            ValidMove(
                token_id=1,
                current_position=10,
                current_state="active",
                target_position=14,
                move_type="advance_main_board",
                is_safe_move=True,
                captures_opponent=False,
                captured_tokens=[],
                strategic_value=7.0,
                strategic_components={},
            ),
        ]

    return AIDecisionContext(
        current_situation=CurrentSituation(
            player_color="red",
            dice_value=dice_value,
            consecutive_sixes=0,
            turn_count=1,
        ),
        player_state=PlayerState(
            player_id=0,
            color="red",
            start_position=0,
            tokens=[],
            tokens_in_home=4,
            active_tokens=0,
            tokens_in_home_column=0,
            finished_tokens=0,
            has_won=False,
            positions_occupied=[],
        ),
        opponents=[
            OpponentInfo(
                color="blue",
                finished_tokens=0,
                tokens_active=1,
                threat_level=0.2,
                positions_occupied=[10],
            ),
        ],
        valid_moves=valid_moves,
        strategic_analysis=StrategicAnalysis(
            can_capture=False,
            can_finish_token=False,
            can_exit_home=True,
            safe_moves=[],
            risky_moves=[],
            best_strategic_move=None,
        ),
    )


class TestLLMStrategy(unittest.TestCase):
    """Test cases for LLMStrategy."""

    def setUp(self):
        """Set up test fixtures."""
        self.context = create_test_decision_context()

    @unittest.skip("Requires langchain dependencies")
    def test_initialization_ollama(self):
        """Test LLM strategy initialization with Ollama provider."""
        pass

    @unittest.skip("Requires langchain dependencies")
    def test_initialization_groq(self):
        """Test LLM strategy initialization with Groq provider."""
        pass

    @unittest.skip("Requires langchain dependencies")
    def test_initialization_groq_no_api_key(self):
        """Test LLM strategy initialization fails gracefully without API key."""
        pass

    def test_fallback_when_no_llm(self):
        """Test that strategy falls back to random when LLM is not available."""
        with patch("ludo_engine.strategies.llm.strategy.LLMStrategy._initialize_llm"):
            strategy = LLMStrategy()
            strategy.llm = None

        with patch.object(
            strategy.fallback_strategy, "decide", return_value=1
        ) as mock_fallback:
            decision = strategy.decide(self.context)
            self.assertEqual(decision, 1)
            mock_fallback.assert_called_once_with(self.context)

    @unittest.skip("Requires langchain dependencies")
    def test_successful_ollama_response(self):
        """Test successful decision making with Ollama response."""
        pass

    @unittest.skip("Requires langchain dependencies")
    def test_successful_groq_response(self):
        """Test successful decision making with Groq response."""
        pass

    def test_response_parsing_various_formats(self):
        """Test parsing of various LLM response formats."""
        with patch("ludo_engine.strategies.llm.strategy.LLMStrategy._initialize_llm"):
            strategy = LLMStrategy()
            strategy.llm = MagicMock()  # Mock to avoid actual LLM calls

        test_cases = [
            ("I choose token 1", 1),
            ("Decision: 0", 0),
            ("Move token 0", 0),
            ("Select 1", 1),
            ("Choose token id 1", 1),
            ("Token 0 is best", 0),
            ("{token_id: 0}", 0),
            ("decision is token 1", 1),
        ]

        for response_text, expected_token in test_cases:
            with self.subTest(response=response_text):
                token_id = strategy._parse_response(response_text, self.context)
                self.assertEqual(token_id, expected_token)

    def test_response_parsing_invalid_token(self):
        """Test that invalid token IDs are rejected."""
        with patch("ludo_engine.strategies.llm.strategy.LLMStrategy._initialize_llm"):
            strategy = LLMStrategy()
            strategy.llm = MagicMock()

        # Token 5 is not valid (only 0-1 available in test context)
        response_text = "Choose token 5"
        token_id = strategy._parse_response(response_text, self.context)
        self.assertIsNone(token_id)

    def test_response_parsing_empty_or_invalid(self):
        """Test parsing of empty or invalid responses."""
        with patch("ludo_engine.strategies.llm.strategy.LLMStrategy._initialize_llm"):
            strategy = LLMStrategy()
            strategy.llm = MagicMock()

        invalid_responses = [
            "",
            "   ",
            "I don't know",
            "Choose token 99",
            "Invalid response",
        ]

        for response_text in invalid_responses:
            with self.subTest(response=response_text):
                token_id = strategy._parse_response(response_text, self.context)
                self.assertIsNone(token_id)

    @unittest.skip("Requires langchain dependencies")
    def test_llm_exception_handling(self):
        """Test that exceptions during LLM calls are handled gracefully."""
        pass

    def test_thinking_removal(self):
        """Test that <think> tags are properly removed from responses."""
        with patch("ludo_engine.strategies.llm.strategy.LLMStrategy._initialize_llm"):
            strategy = LLMStrategy()
            strategy.llm = MagicMock()

        response_with_thinking = """
        <think>
        Let me analyze this carefully...
        I need to consider the strategic value...
        </think>
        Based on my analysis, I choose token 1
        """

        token_id = strategy._parse_response(response_with_thinking, self.context)
        self.assertEqual(token_id, 1)

    def test_case_insensitive_parsing(self):
        """Test that response parsing is case insensitive."""
        with patch("ludo_engine.strategies.llm.strategy.LLMStrategy._initialize_llm"):
            strategy = LLMStrategy()
            strategy.llm = MagicMock()

        responses = [
            "TOKEN 0",
            "Token 0",
            "token 0",
            "CHOOSE 1",
            "Choose 1",
            "choose 1",
        ]

        for response in responses:
            with self.subTest(response=response):
                token_id = strategy._parse_response(response, self.context)
                expected = 0 if "0" in response else 1
                self.assertEqual(token_id, expected)

    def test_json_response_parsing(self):
        """Test parsing of JSON-like responses."""
        with patch("ludo_engine.strategies.llm.strategy.LLMStrategy._initialize_llm"):
            strategy = LLMStrategy()
            strategy.llm = MagicMock()

        json_responses = [
            '{"token_id": 0}',
            '{"token": 1}',
        ]

        for response in json_responses:
            with self.subTest(response=response):
                token_id = strategy._parse_response(response, self.context)
                # Extract expected token from JSON

                expected = json.loads(response)
                expected_token = expected.get(
                    "token_id",
                    expected.get(
                        "token", expected.get("move", expected.get("decision"))
                    ),
                )
                self.assertEqual(token_id, expected_token)

    def test_create_prompt_functionality(self):
        """Test that create_prompt generates correct prompt structure."""
        context = create_test_decision_context()

        # Test with the default valid moves
        prompt = create_prompt(context, context.valid_moves)

        # Verify prompt contains expected sections
        self.assertIn("You are playing Ludo", prompt)
        self.assertIn("GAME SITUATION", prompt)
        self.assertIn("AVAILABLE MOVES", prompt)
        self.assertIn("DECISION:", prompt)

        # Verify player state information is filled correctly
        self.assertIn("My progress: 0/4 tokens finished", prompt)
        self.assertIn("4 at home", prompt)  # Should be filled with actual value
        self.assertIn("0 active", prompt)  # Should be filled with actual value

        # Verify moves are listed
        self.assertIn("Token 0:", prompt)
        self.assertIn("Token 1:", prompt)
        self.assertIn("advance_main_board", prompt)

        # Verify strategic information
        self.assertIn("value: 5.00", prompt)
        self.assertIn("value: 7.00", prompt)
        self.assertIn("[SAFE]", prompt)
        self.assertIn("[RISKY]", prompt)

    def test_create_prompt_with_capture_move(self):
        """Test create_prompt with a move that captures opponent."""
        capture_move = ValidMove(
            token_id=0,
            current_position=5,
            current_state="active",
            target_position=10,
            move_type="advance_main_board",
            is_safe_move=False,
            captures_opponent=True,
            captured_tokens=[],
            strategic_value=15.0,
            strategic_components={},
        )

        context = create_test_decision_context(valid_moves=[capture_move])
        prompt = create_prompt(context, [capture_move])

        # Verify capture information is included
        self.assertIn("[CAPTURES OPPONENT]", prompt)
        self.assertIn("value: 15.00", prompt)

    def test_create_prompt_with_home_column_move(self):
        """Test create_prompt with home column advancement."""
        home_move = ValidMove(
            token_id=0,
            current_position=100,
            current_state="home_column",
            target_position=102,
            move_type="advance_home_column",
            is_safe_move=True,
            captures_opponent=False,
            captured_tokens=[],
            strategic_value=12.0,
            strategic_components={},
        )

        context = create_test_decision_context(valid_moves=[home_move])
        prompt = create_prompt(context, [home_move])

        # Verify home column move type is included
        self.assertIn("advance_home_column", prompt)
        self.assertIn("value: 12.00", prompt)
        self.assertIn("[SAFE]", prompt)


if __name__ == "__main__":
    unittest.main()
