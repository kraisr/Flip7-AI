"""
Baseline agents for Flip 7 game.

This module contains various baseline agents for comparison and as opponents
for RL training.
"""

import random
from typing import List, Tuple, Any
from cards import CardType


class BaseAgent:
    """Base class for all agents."""
    
    def __init__(self, name: str):
        """
        Initialize the agent.
        
        Args:
            name: Name of the agent
        """
        self.name = name
    
    def select_action(self, state: Tuple, valid_actions: List[int]) -> int:
        """
        Select an action based on the current state.
        
        Args:
            state: Current state representation
            valid_actions: List of valid action indices
            
        Returns:
            Selected action index
        """
        raise NotImplementedError("Subclasses must implement select_action")
    
    def __str__(self) -> str:
        return self.name


class RandomAgent(BaseAgent):
    """Agent that randomly selects actions."""
    
    def __init__(self, name: str = "RandomAgent"):
        super().__init__(name)
    
    def select_action(self, state: Tuple, valid_actions: List[int]) -> int:
        """Randomly select from valid actions."""
        if not valid_actions:
            return 0  # Default to hit if no valid actions (shouldn't happen)
        return random.choice(valid_actions)


class HeuristicAgent(BaseAgent):
    """
    Simple heuristic agent that uses rule-based strategy.
    
    Strategy: Hit if hand value < threshold, otherwise stay.
    """
    
    def __init__(self, name: str = "HeuristicAgent", threshold: int = 15):
        """
        Initialize heuristic agent.
        
        Args:
            name: Name of the agent
            threshold: Hand value threshold for staying (default: 15)
        """
        super().__init__(name)
        self.threshold = threshold
    
    def select_action(self, state: Tuple, valid_actions: List[int]) -> int:
        """
        Select action based on hand value.
        
        State format: (num_cards, num_numbers, hand_sum, ...)
        """
        if not valid_actions:
            return 0
        
        # Extract hand sum from state (index 2)
        hand_sum = state[2] if len(state) > 2 else 0
        
        # Hit if hand value is below threshold
        if hand_sum < self.threshold:
            if 0 in valid_actions:  # ACTION_HIT
                return 0
        else:
            if 1 in valid_actions:  # ACTION_STAY
                return 1
        
        # Fallback to random if preferred action not available
        return random.choice(valid_actions)


class ConservativeAgent(BaseAgent):
    """
    Conservative agent that stays early to avoid risk.
    
    Strategy: Stay if hand has any cards or if hand value >= 10.
    """
    
    def __init__(self, name: str = "ConservativeAgent", stay_threshold: int = 10):
        """
        Initialize conservative agent.
        
        Args:
            name: Name of the agent
            stay_threshold: Hand value threshold for staying (default: 10)
        """
        super().__init__(name)
        self.stay_threshold = stay_threshold
    
    def select_action(self, state: Tuple, valid_actions: List[int]) -> int:
        """Select action - prefer staying early."""
        if not valid_actions:
            return 0
        
        # Extract state info
        num_cards = state[0] if len(state) > 0 else 0
        hand_sum = state[2] if len(state) > 2 else 0
        is_busted = state[8] if len(state) > 8 else 0
        
        # Stay if busted (shouldn't happen, but safety check)
        if is_busted:
            if 1 in valid_actions:
                return 1
        
        # Stay if hand value is high enough
        if hand_sum >= self.stay_threshold:
            if 1 in valid_actions:
                return 1
        
        # Otherwise hit
        if 0 in valid_actions:
            return 0
        
        return random.choice(valid_actions)


class AggressiveAgent(BaseAgent):
    """
    Aggressive agent that hits more often to chase seven-card bonus.
    
    Strategy: Hit unless hand value is very high or already has 6+ unique cards.
    """
    
    def __init__(self, name: str = "AggressiveAgent", stay_threshold: int = 25):
        """
        Initialize aggressive agent.
        
        Args:
            name: Name of the agent
            stay_threshold: Hand value threshold for staying (default: 25)
        """
        super().__init__(name)
        self.stay_threshold = stay_threshold
    
    def select_action(self, state: Tuple, valid_actions: List[int]) -> int:
        """Select action - prefer hitting to chase bonus."""
        if not valid_actions:
            return 0
        
        # Extract state info
        hand_sum = state[2] if len(state) > 2 else 0
        unique_numbers = state[3] if len(state) > 3 else 0
        seven_bonus = state[10] if len(state) > 10 else 0
        
        # If already got seven-card bonus, stay
        if seven_bonus:
            if 1 in valid_actions:
                return 1
        
        # Stay only if hand value is very high
        if hand_sum >= self.stay_threshold:
            if 1 in valid_actions:
                return 1
        
        # If close to seven unique cards (6 unique), be more careful
        if unique_numbers >= 6:
            # Still hit if hand value is low
            if hand_sum < 20:
                if 0 in valid_actions:
                    return 0
            else:
                if 1 in valid_actions:
                    return 1
        
        # Otherwise hit
        if 0 in valid_actions:
            return 0
        
        return random.choice(valid_actions)


class SmartHeuristicAgent(BaseAgent):
    """
    Smarter heuristic agent that considers more factors.
    
    Strategy: Considers hand value, unique cards, modifiers, and risk.
    """
    
    def __init__(self, name: str = "SmartHeuristicAgent"):
        super().__init__(name)
    
    def select_action(self, state: Tuple, valid_actions: List[int]) -> int:
        """Select action using smarter heuristics."""
        if not valid_actions:
            return 0
        
        # Extract state info
        num_cards = state[0] if len(state) > 0 else 0
        hand_sum = state[2] if len(state) > 2 else 0
        unique_numbers = state[3] if len(state) > 3 else 0
        has_x2 = state[7] if len(state) > 7 else 0
        is_busted = state[8] if len(state) > 8 else 0
        
        # Can't act if busted
        if is_busted:
            return random.choice(valid_actions)
        
        # If close to seven unique cards, be aggressive
        if unique_numbers >= 6:
            if 0 in valid_actions:
                return 0
        
        # If has X2 modifier, can afford to be more aggressive
        if has_x2 and hand_sum < 20:
            if 0 in valid_actions:
                return 0
        
        # Base decision on hand value
        if hand_sum < 12:
            if 0 in valid_actions:
                return 0
        elif hand_sum > 20:
            if 1 in valid_actions:
                return 1
        else:
            # Middle range - consider risk
            if unique_numbers < 5:
                if 0 in valid_actions:
                    return 0
            else:
                if 1 in valid_actions:
                    return 1
        
        return random.choice(valid_actions)




