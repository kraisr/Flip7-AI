"""
RL Environment module for Flip 7 game.

This module provides a Gym-like interface for reinforcement learning agents
to interact with the Flip 7 game environment.
"""

from typing import Tuple, List, Dict, Optional, Any
from game import Flip7Game
from player import Player
from cards import CardType


class Flip7RLEnv:
    """
    Reinforcement Learning environment wrapper for Flip 7 game.
    
    Provides a standard RL interface (reset, step, get_state, get_reward)
    for training RL agents.
    """
    
    # Action space: 0 = Hit, 1 = Stay
    ACTION_HIT = 0
    ACTION_STAY = 1
    
    def __init__(self, agent_name: str = "RL_Agent", opponent_names: List[str] = None, 
                 target_score: int = 200, agent_index: int = 0, opponent_agents: List = None):
        """
        Initialize the RL environment.
        
        Args:
            agent_name: Name of the RL agent player
            opponent_names: Names of opponent players (default: ["Opponent1", "Opponent2"])
            target_score: Target score to win the game
            agent_index: Index of the agent player (0, 1, or 2)
            opponent_agents: List of agent objects for opponents (optional)
        """
        if opponent_names is None:
            opponent_names = ["Opponent1", "Opponent2"]
        
        if len(opponent_names) != 2:
            raise ValueError("Must provide exactly 2 opponent names")
        
        if agent_index not in [0, 1, 2]:
            raise ValueError("agent_index must be 0, 1, or 2")
        
        self.agent_name = agent_name
        self.agent_index = agent_index
        self.target_score = target_score
        self.opponent_agents = opponent_agents if opponent_agents else [None, None]
        
        # Create player names list with agent at specified index
        player_names = [""] * 3
        player_names[agent_index] = agent_name
        opp_idx = 0
        for i in range(3):
            if i != agent_index:
                player_names[i] = opponent_names[opp_idx]
                opp_idx += 1
        
        self.player_names = player_names
        self.game: Optional[Flip7Game] = None
        
        # Episode statistics
        self.episode_reward = 0.0
        self.episode_round_scores = []
        self.last_action_result = None
    
    def reset(self) -> Tuple[Any, Dict]:
        """
        Reset the environment to start a new episode.
        
        Returns:
            Tuple of (initial_state, info_dict)
        """
        # Create new game
        self.game = Flip7Game(self.player_names, self.target_score)
        
        # Reset episode statistics
        self.episode_reward = 0.0
        self.episode_round_scores = []
        self.last_action_result = None
        
        # Get initial state
        state = self.get_state()
        info = {
            'round_number': self.game.round_number,
            'game_over': False
        }
        
        return state, info
    
    def step(self, action: int) -> Tuple[Any, float, bool, Dict]:
        """
        Execute an action in the environment.
        
        Args:
            action: Action to take (0=Hit, 1=Stay)
            
        Returns:
            Tuple of (next_state, reward, done, info)
        """
        if self.game is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")
        
        if self.game.is_game_over():
            state = self.get_state()
            return state, 0.0, True, {'game_over': True}
        
        # Check if it's the agent's turn
        current_player = self.game.get_current_player()
        agent_player = self.game.players[self.agent_index]
        
        # If it's not the agent's turn, simulate opponent actions until agent's turn or game ends
        if current_player != agent_player:
            # Simulate ONE opponent turn (the environment will be called again if needed)
            self._simulate_opponent_turn()
            
            # Check if round ended after opponent's action
            round_ended = not self.game.round_active
            if round_ended and not self.game.is_game_over():
                # Start new round
                self.game.start_new_round()
            
            state = self.get_state()
            reward = 0.0
            done = self.game.is_game_over()
            info = {
                'round_number': self.game.round_number,
                'round_active': self.game.round_active,
                'round_ended': round_ended,
                'game_over': done
            }
            return state, reward, done, info
        
        # Check if agent has already ended their turn
        if agent_player.has_stayed or agent_player.is_busted:
            # Agent has already ended turn - check if round should end
            # Force check round end conditions
            self.game._check_round_end_conditions()
            
            # If round ended, handle it
            round_ended = not self.game.round_active
            if round_ended and not self.game.is_game_over():
                self.game.start_new_round()
            
            state = self.get_state()
            reward = 0.0
            done = self.game.is_game_over()
            info = {
                'round_number': self.game.round_number,
                'round_active': self.game.round_active,
                'round_ended': round_ended,
                'game_over': done,
                'message': 'Agent already ended turn'
            }
            return state, reward, done, info
        
        # Agent's turn - execute action
        if action == self.ACTION_HIT:
            success, message = self.game.hit()
            self.last_action_result = message
        elif action == self.ACTION_STAY:
            success, message = self.game.stay()
            self.last_action_result = message
        else:
            raise ValueError(f"Invalid action: {action}. Must be 0 (Hit) or 1 (Stay).")
        
        if not success:
            # Invalid action - check if we should end round or advance turn
            # This might happen if action failed but round should end
            self.game._check_round_end_conditions()
            
            round_ended = not self.game.round_active
            if round_ended and not self.game.is_game_over():
                self.game.start_new_round()
            
            state = self.get_state()
            reward = -1.0
            done = self.game.is_game_over()
            info = {'error': message, 'game_over': done, 'round_ended': round_ended}
            return state, reward, done, info
        
        # Calculate reward
        reward = self.get_reward()
        self.episode_reward += reward
        
        # Check if round ended
        round_ended = not self.game.round_active
        if round_ended and not self.game.is_game_over():
            # Start new round
            self.game.start_new_round()
            # Record round score
            agent_player = self.game.players[self.agent_index]
            self.episode_round_scores.append(agent_player.round_score)
        
        # Get next state
        state = self.get_state()
        done = self.game.is_game_over()
        
        info = {
            'round_number': self.game.round_number,
            'round_active': self.game.round_active,
            'round_ended': round_ended,
            'game_over': done,
            'action_result': message
        }
        
        if done:
            info['winner'] = self.game.get_winner().name if self.game.get_winner() else None
            info['episode_reward'] = self.episode_reward
            info['round_scores'] = self.episode_round_scores
        
        return state, reward, done, info
    
    def _simulate_opponent_turn(self):
        """
        Simulate opponent turns until it's the agent's turn or the round/game ends.
        
        This function will continue simulating opponent actions until:
        - It's the agent's turn
        - The round ends (all players have stayed/busted)
        - The game ends
        """
        max_iterations = 20  # Safety limit to prevent infinite loops
        iterations = 0
        
        while iterations < max_iterations:
            iterations += 1
            
            # Check if round or game ended
            if not self.game.round_active or self.game.is_game_over():
                break
            
            current_player = self.game.get_current_player()
            current_player_index = self.game.current_player_index
            
            # If it's the agent's turn, we're done
            if current_player_index == self.agent_index:
                break
            
            # If current player has already ended their turn, advance
            if current_player.has_stayed or current_player.is_busted:
                self.game._check_round_end_conditions()
                # After checking round end, it might be agent's turn or round might have ended
                if not self.game.round_active or self.game.is_game_over():
                    break
                if self.game.get_current_player() == self.game.players[self.agent_index]:
                    break
                continue
            
            # Find which opponent this is
            opponent_idx = 0 if current_player_index < self.agent_index else 1
            opponent_agent = self.opponent_agents[opponent_idx] if opponent_idx < len(self.opponent_agents) else None
            
            # Determine valid actions for the current player (opponent)
            valid_actions_for_opponent = [self.ACTION_HIT, self.ACTION_STAY]
            
            if opponent_agent is not None:
                # Use agent to select action
                state = self.get_state()  # This is agent's state, but opponent agents can ignore it
                action = opponent_agent.select_action(state, valid_actions_for_opponent)
                
                if action == self.ACTION_HIT:
                    success, _ = self.game.hit()
                    if not success:
                        # If hit failed, try staying
                        self.game.stay()
                else:
                    success, _ = self.game.stay()
                    if not success:
                        # If stay failed, force advance
                        self.game._check_round_end_conditions()
            else:
                # Simple heuristic: hit if hand value < 15, otherwise stay
                number_cards = [card for card in current_player.hand if card.card_type == CardType.NUMBER]
                hand_value = sum(card.value for card in number_cards)
                
                if hand_value < 15:
                    success, _ = self.game.hit()
                    if not success:
                        self.game.stay()
                else:
                    success, _ = self.game.stay()
                    if not success:
                        # If stay failed, force advance
                        self.game._check_round_end_conditions()
            
            # After opponent action, check if round ended or it's now agent's turn
            if not self.game.round_active or self.game.is_game_over():
                break
            if self.game.get_current_player() == self.game.players[self.agent_index]:
                break
    
    def get_state(self) -> Tuple:
        """
        Get the current state representation for the RL agent.
        
        Returns:
            State tuple (hashable for Q-table lookup)
        """
        if self.game is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")
        
        agent_player = self.game.players[self.agent_index]
        
        # Extract hand features
        number_cards = [card for card in agent_player.hand if card.card_type == CardType.NUMBER]
        modifier_cards = [card for card in agent_player.hand if card.card_type == CardType.MODIFIER]
        
        # Hand features
        num_cards = len(agent_player.hand)
        num_number_cards = len(number_cards)
        hand_sum = sum(card.value for card in number_cards)
        unique_numbers = len(set(card.value for card in number_cards))
        
        # Modifier features (binary)
        has_plus2 = any(card.name == "+2" for card in modifier_cards)
        has_plus4 = any(card.name == "+4" for card in modifier_cards)
        has_plus10 = any(card.name == "+10" for card in modifier_cards)
        has_x2 = any(card.name == "X2" for card in modifier_cards)
        
        # Risk features
        is_busted = 1 if agent_player.is_busted else 0
        has_stayed = 1 if agent_player.has_stayed else 0
        seven_card_bonus = 1 if agent_player.seven_card_bonus else 0
        
        # Game context
        round_num = min(self.game.round_number, 10)  # Cap at 10 for state space
        total_score = min(agent_player.total_score, 500)  # Cap at 500
        
        # Opponent scores (relative)
        opponent_scores = []
        for i, player in enumerate(self.game.players):
            if i != self.agent_index:
                opponent_scores.append(min(player.total_score, 500))
        
        # Score difference
        max_opponent_score = max(opponent_scores) if opponent_scores else 0
        score_diff = total_score - max_opponent_score
        score_diff_binned = max(-50, min(50, score_diff // 10))  # Bin to -5 to +5
        
        # Create state tuple (all values must be hashable)
        state = (
            num_cards,
            num_number_cards,
            min(hand_sum, 100),  # Cap at 100
            unique_numbers,
            int(has_plus2),
            int(has_plus4),
            int(has_plus10),
            int(has_x2),
            is_busted,
            has_stayed,
            seven_card_bonus,
            round_num,
            total_score // 10,  # Bin to reduce state space
            score_diff_binned
        )
        
        return state
    
    def get_valid_actions(self) -> List[int]:
        """
        Get list of valid actions for the current state.
        
        Returns:
            List of valid action indices
        """
        if self.game is None:
            return [self.ACTION_HIT, self.ACTION_STAY]
        
        agent_player = self.game.players[self.agent_index]
        
        # If busted or stayed, no valid actions
        if agent_player.is_busted or agent_player.has_stayed:
            return []
        
        # If not agent's turn, no actions available
        current_player = self.game.get_current_player()
        if current_player != agent_player:
            return []
        
        # Both actions are valid
        return [self.ACTION_HIT, self.ACTION_STAY]
    
    def get_reward(self) -> float:
        """
        Calculate reward for the current state/action.
        
        Returns:
            Reward value
        """
        if self.game is None:
            return 0.0
        
        agent_player = self.game.players[self.agent_index]
        reward = 0.0
        
        # Calculate hand features
        number_cards = [card for card in agent_player.hand if card.card_type == CardType.NUMBER]
        modifier_cards = [card for card in agent_player.hand if card.card_type != CardType.NUMBER]
        hand_value = sum(card.value for card in number_cards)
        unique_numbers = len(set(card.value for card in number_cards))
        num_cards = len(agent_player.hand)
        
        # Immediate rewards for actions (encourage exploration)
        if agent_player.is_busted:
            # Context-aware busting penalty
            # Less penalty if busting with low hand (took a reasonable risk)
            if hand_value <= 15:
                reward -= 10.0  # Smaller penalty for reasonable risk
            else:
                reward -= 20.0  # Larger penalty for risky play with high hand
        elif agent_player.seven_card_bonus:
            reward += 150.0  # Large bonus for seven-card bonus
        elif agent_player.has_stayed:
            # Reward for staying based on hand quality
            if hand_value >= 15:
                reward += 3.0  # Good hand, smart to stay
            elif hand_value >= 10:
                reward += 1.5  # Decent hand
            else:
                reward += 0.2  # Low hand, but stayed (conservative)
        else:
            # Agent is still playing - reward good progress
            # Reward for building toward a good hand
            if hand_value < 15 and not agent_player.is_busted:
                # Reward for hitting when it's safe to do so
                if hand_value < 10:
                    reward += 0.5  # Good to hit with low hand
                elif hand_value < 12:
                    reward += 0.3  # Still reasonable to hit
                # No reward for hitting with high hand (risky)
            
            # Reward for collecting unique cards (progress toward 7-card bonus)
            if unique_numbers >= 5:
                reward += 1.0  # Getting close to 7-card bonus
            elif unique_numbers >= 3:
                reward += 0.3  # Making progress
        
        # Round-end rewards (more informative)
        if not self.game.round_active:
            agent_score = agent_player.round_score
            opponent_scores = [
                self.game.players[i].round_score 
                for i in range(3) if i != self.agent_index
            ]
            max_opponent_score = max(opponent_scores) if opponent_scores else 0
            
            # Score difference reward (more granular)
            score_diff = agent_score - max_opponent_score
            if score_diff > 0:
                # Winning round - reward proportional to margin
                reward += 40.0 + min(score_diff * 2.0, 60.0)  # 40-100 points
            elif score_diff < 0:
                # Losing round - penalty proportional to margin
                reward -= 20.0 + min(abs(score_diff) * 1.0, 40.0)  # -20 to -60 points
            # Tie gives small positive
            else:
                reward += 8.0
        
        # Game-end rewards (scaled)
        if self.game.is_game_over():
            if self.game.get_winner() == agent_player:
                reward += 300.0  # Large bonus for winning game
            else:
                # Penalty based on how close we were
                agent_final_score = agent_player.total_score
                winner_score = self.game.get_winner().total_score if self.game.get_winner() else agent_final_score
                score_gap = winner_score - agent_final_score
                reward -= 60.0 + min(score_gap * 2.0, 120.0)  # -60 to -180 points
        
        # Normalize reward to [-1, 1] range for stable learning
        # Maximum possible reward: ~550 (game win + round win + seven-card bonus)
        # Use 500 as normalization factor to keep rewards in reasonable range
        normalized_reward = reward / 500.0
        # Clip to prevent extreme values
        normalized_reward = max(-1.0, min(1.0, normalized_reward))
        
        return normalized_reward
    
    def state_to_string(self, state: Tuple) -> str:
        """
        Convert state tuple to human-readable string for debugging.
        
        Args:
            state: State tuple
            
        Returns:
            String representation of state
        """
        return (f"State(num_cards={state[0]}, num_numbers={state[1]}, "
                f"hand_sum={state[2]}, unique={state[3]}, "
                f"modifiers=[+2:{state[4]}, +4:{state[5]}, +10:{state[6]}, X2:{state[7]}], "
                f"busted={state[8]}, stayed={state[9]}, seven_bonus={state[10]}, "
                f"round={state[11]}, score={state[12]*10}, score_diff={state[13]*10})")

