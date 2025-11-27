"""
Q-Learning agent for Flip 7 game.

This module implements a Q-Learning agent using tabular Q-table.
"""

import random
import json
import pickle
from typing import Dict, Tuple, List, Optional
from collections import defaultdict


class QLearningAgent:
    """
    Q-Learning agent using tabular Q-table.
    
    Uses epsilon-greedy exploration and Q-learning update rule.
    """
    
    def __init__(self, name: str = "QLearningAgent", 
                 learning_rate: float = 0.1,
                 discount_factor: float = 0.95,
                 epsilon: float = 1.0,
                 epsilon_min: float = 0.05,  # Lower minimum for more exploration
                 epsilon_decay: float = 0.998):  # Slower decay for more exploration
        """
        Initialize Q-Learning agent.
        
        Args:
            name: Name of the agent
            learning_rate: Learning rate (alpha) for Q-learning update
            discount_factor: Discount factor (gamma) for future rewards
            epsilon: Initial exploration rate
            epsilon_min: Minimum exploration rate
            epsilon_decay: Epsilon decay rate per episode
        """
        self.name = name
        self.learning_rate = learning_rate
        self.initial_learning_rate = learning_rate  # Store for decay
        self.learning_rate_min = 0.01  # Minimum learning rate
        self.learning_rate_decay = 0.9995  # Decay per episode
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        
        # Q-table: (state, action) -> Q-value
        # Optimistic initialization: start with small positive values
        # This encourages exploration and helps with sparse rewards
        self.optimistic_init_value = 0.1
        self.q_table: Dict[Tuple, Dict[int, float]] = defaultdict(
            lambda: {0: self.optimistic_init_value, 1: self.optimistic_init_value}
        )
        
        # Statistics
        self.total_updates = 0
        self.exploration_count = 0
        self.exploitation_count = 0
    
    def select_action(self, state: Tuple, valid_actions: List[int], training: bool = True) -> int:
        """
        Select action using epsilon-greedy policy.
        
        Args:
            state: Current state tuple
            valid_actions: List of valid action indices
            training: Whether in training mode (affects epsilon)
            
        Returns:
            Selected action index
        """
        if not valid_actions:
            return 0  # Default action
        
        # Epsilon-greedy: explore or exploit
        if training and random.random() < self.epsilon:
            # Explore: random action
            action = random.choice(valid_actions)
            self.exploration_count += 1
        else:
            # Exploit: choose action with highest Q-value
            action = self._get_best_action(state, valid_actions)
            self.exploitation_count += 1
        
        return action
    
    def _get_best_action(self, state: Tuple, valid_actions: List[int]) -> int:
        """
        Get the best action according to Q-table.
        
        Args:
            state: Current state tuple
            valid_actions: List of valid action indices
            
        Returns:
            Best action index
        """
        q_values = self.q_table[state]
        
        # Get Q-values for valid actions only (use optimistic init if not seen)
        valid_q_values = {action: q_values.get(action, self.optimistic_init_value) for action in valid_actions}
        
        # Find action with maximum Q-value
        if not valid_q_values:
            return random.choice(valid_actions)
        
        max_q = max(valid_q_values.values())
        best_actions = [action for action, q_val in valid_q_values.items() if q_val == max_q]
        
        # If tie, choose randomly among best actions
        return random.choice(best_actions)
    
    def update_q_value(self, state: Tuple, action: int, reward: float,
                      next_state: Tuple, next_valid_actions: List[int]) -> None:
        """
        Update Q-value using Q-learning update rule.
        
        Q(s,a) = Q(s,a) + alpha * [r + gamma * max(Q(s',a')) - Q(s,a)]
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state after action
            next_valid_actions: Valid actions in next state
        """
        # Get current Q-value (use optimistic init if not seen)
        current_q = self.q_table[state].get(action, self.optimistic_init_value)
        
        # Calculate max Q-value for next state
        if next_valid_actions:
            next_q_values = self.q_table[next_state]
            max_next_q = max(next_q_values.get(a, self.optimistic_init_value) for a in next_valid_actions)
        else:
            # Terminal state or no valid actions
            max_next_q = 0.0
        
        # Q-learning update
        td_target = reward + self.discount_factor * max_next_q
        td_error = td_target - current_q
        new_q = current_q + self.learning_rate * td_error
        
        # Update Q-table
        self.q_table[state][action] = new_q
        self.total_updates += 1
    
    def get_q_value(self, state: Tuple, action: int) -> float:
        """
        Get Q-value for state-action pair.
        
        Args:
            state: State tuple
            action: Action index
            
        Returns:
            Q-value
        """
        return self.q_table[state].get(action, self.optimistic_init_value)
    
    def decay_epsilon(self) -> None:
        """Decay epsilon for exploration."""
        if self.epsilon > self.epsilon_min:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def decay_learning_rate(self) -> None:
        """Decay learning rate for more stable learning over time."""
        if self.learning_rate > self.learning_rate_min:
            self.learning_rate = max(self.learning_rate_min, 
                                   self.learning_rate * self.learning_rate_decay)
    
    def set_epsilon(self, epsilon: float) -> None:
        """
        Set epsilon value.
        
        Args:
            epsilon: New epsilon value
        """
        self.epsilon = max(self.epsilon_min, min(1.0, epsilon))
    
    def set_learning_rate(self, learning_rate: float) -> None:
        """
        Set learning rate value.
        
        Args:
            learning_rate: New learning rate value
        """
        self.learning_rate = max(self.learning_rate_min, min(1.0, learning_rate))
    
    def disable_learning_rate_decay(self) -> None:
        """Disable learning rate decay by setting decay to 1.0."""
        self.learning_rate_decay = 1.0
    
    def enable_learning_rate_decay(self, decay: float = None) -> None:
        """
        Enable learning rate decay.
        
        Args:
            decay: Decay rate (default: 0.9995)
        """
        if decay is None:
            decay = 0.9995
        self.learning_rate_decay = decay
    
    def get_statistics(self) -> Dict:
        """
        Get agent statistics.
        
        Returns:
            Dictionary with statistics
        """
        total_actions = self.exploration_count + self.exploitation_count
        exploration_rate = self.exploration_count / total_actions if total_actions > 0 else 0.0
        
        return {
            'q_table_size': len(self.q_table),
            'total_updates': self.total_updates,
            'exploration_count': self.exploration_count,
            'exploitation_count': self.exploitation_count,
            'exploration_rate': exploration_rate,
            'epsilon': self.epsilon
        }
    
    def save_q_table(self, filepath: str) -> None:
        """
        Save Q-table to file.
        
        Args:
            filepath: Path to save file
        """
        # Convert defaultdict to regular dict
        q_table_dict = dict(self.q_table)
        
        data = {
            'q_table': q_table_dict,
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor,
            'epsilon': self.epsilon,
            'epsilon_min': self.epsilon_min,
            'epsilon_decay': self.epsilon_decay,
            'total_updates': self.total_updates
        }
        
        # Try pickle first (preserves tuple keys), fallback to JSON
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
        except Exception:
            # Fallback: save as JSON (requires converting tuples to strings)
            q_table_dict_str = {str(k): v for k, v in q_table_dict.items()}
            data['q_table'] = q_table_dict_str
            with open(filepath.replace('.pkl', '.json'), 'w') as f:
                json.dump(data, f, indent=2)
    
    def load_q_table(self, filepath: str) -> None:
        """
        Load Q-table from file.
        
        Args:
            filepath: Path to load file
        """
        try:
            # Try pickle first
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            # Check if keys are strings (from old format) and convert back to tuples
            if data['q_table'] and isinstance(next(iter(data['q_table'].keys())), str):
                # Old format: keys are strings, convert back to tuples
                data['q_table'] = {eval(k): v for k, v in data['q_table'].items()}
        except (FileNotFoundError, ValueError):
            # Try JSON
            json_path = filepath.replace('.pkl', '.json')
            with open(json_path, 'r') as f:
                data = json.load(f)
                # Convert string keys back to tuples
                data['q_table'] = {eval(k): v for k, v in data['q_table'].items()}
        
        # Create defaultdict and populate with loaded data
        self.q_table = defaultdict(lambda: {0: self.optimistic_init_value, 1: self.optimistic_init_value})
        self.q_table.update(data['q_table'])
        self.learning_rate = data.get('learning_rate', self.learning_rate)
        self.discount_factor = data.get('discount_factor', self.discount_factor)
        self.epsilon = data.get('epsilon', self.epsilon)
        self.epsilon_min = data.get('epsilon_min', self.epsilon_min)
        self.epsilon_decay = data.get('epsilon_decay', self.epsilon_decay)
        self.total_updates = data.get('total_updates', 0)
    
    def reset_statistics(self) -> None:
        """Reset exploration/exploitation counters."""
        self.exploration_count = 0
        self.exploitation_count = 0




