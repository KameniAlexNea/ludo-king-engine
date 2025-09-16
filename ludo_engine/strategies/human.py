"""
Human strategy - allows human player to make decisions through the interface.
"""

from ludo_engine.model import AIDecisionContext
from ludo_engine.strategies.base import Strategy


class HumanStrategy(Strategy):
    """
    Human strategy that waits for user input from the interface.
    """

    def __init__(self):
        super().__init__(
            name="human",
            description="Human player - makes decisions through the interface"
        )
        self.pending_decision = None
        self.waiting_for_input = False
        self.game_context = None

    def decide(self, game_context: AIDecisionContext) -> int:
        """
        For human strategy, this method stores the context and waits for user input.
        The actual decision is made through set_decision() method called from the UI.
        """
        self.game_context = game_context
        self.waiting_for_input = True
        self.pending_decision = None
        
        # Return the first valid move as default - this will be overridden
        # by the interface when the human makes a choice
        valid_moves = self._get_valid_moves(game_context)
        if valid_moves:
            return valid_moves[0].token_id
        return 0

    def set_decision(self, token_id: int) -> None:
        """Set the human player's decision."""
        self.pending_decision = token_id
        self.waiting_for_input = False

    def is_waiting_for_input(self) -> bool:
        """Check if the strategy is waiting for human input."""
        return self.waiting_for_input

    def get_pending_decision(self) -> int:
        """Get the human player's decision."""
        return self.pending_decision

    def get_game_context(self) -> AIDecisionContext:
        """Get the current game context for the human player."""
        return self.game_context

    def reset_decision(self) -> None:
        """Reset the decision state."""
        self.pending_decision = None
        self.waiting_for_input = False
        self.game_context = None