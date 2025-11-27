"""
Training script for Q-Learning agent in Flip 7 game.

This script trains a Q-Learning agent by running multiple episodes
and updating Q-values based on game outcomes.
"""

import argparse
import time
from typing import List, Dict
from rl_env import Flip7RLEnv
from q_learning_agent import QLearningAgent
from agents import RandomAgent, HeuristicAgent, ConservativeAgent, AggressiveAgent


def train_agent(env: Flip7RLEnv, agent: QLearningAgent, num_episodes: int = 1000,
                eval_interval: int = 100, eval_episodes: int = 10,
                opponent_agents: List = None, verbose: bool = True) -> Dict:
    """
    Train Q-Learning agent.
    
    Args:
        env: RL environment
        agent: Q-Learning agent to train
        num_episodes: Number of training episodes
        eval_interval: Evaluate agent every N episodes
        eval_episodes: Number of episodes for evaluation
        opponent_agents: List of opponent agents for evaluation
        verbose: Whether to print progress
        
    Returns:
        Dictionary with training statistics
    """
    training_stats = {
        'episode_rewards': [],
        'episode_lengths': [],
        'win_rates': [],
        'q_table_sizes': [],
        'epsilon_values': []
    }
    
    total_wins = 0
    total_games = 0
    
    if verbose:
        print(f"Starting training for {num_episodes} episodes...")
        print(f"Initial epsilon: {agent.epsilon:.3f}")
        print(f"Learning rate: {agent.learning_rate}, Discount: {agent.discount_factor}")
        print("-" * 60)
    
    start_time = time.time()
    
    for episode in range(num_episodes):
        # Reset environment
        state, info = env.reset()
        episode_reward = 0.0
        episode_length = 0
        done = False
        
        # Store previous state/action for Q-learning update
        prev_state = None
        prev_action = None
        prev_reward = 0.0
        
        while not done:
            # Get valid actions
            valid_actions = env.get_valid_actions()
            
            # If no valid actions, wait for next turn
            if not valid_actions:
                # Simulate opponent turns until agent can act
                while not done and not env.get_valid_actions():
                    state, reward, done, info = env.step(0)  # Dummy action
                    episode_length += 1
                continue
            
            # Select action
            action = agent.select_action(state, valid_actions, training=True)
            
            # Store previous state if this is not first action
            if prev_state is not None:
                # Update Q-value for previous state-action pair
                agent.update_q_value(prev_state, prev_action, prev_reward, state, valid_actions)
            
            # Take step in environment
            next_state, reward, done, info = env.step(action)
            
            episode_reward += reward
            episode_length += 1
            
            # Store for next update
            prev_state = state
            prev_action = action
            prev_reward = reward
            
            state = next_state
        
        # Final Q-update (terminal state)
        if prev_state is not None:
            agent.update_q_value(prev_state, prev_action, prev_reward, state, [])
        
        # Check if agent won
        if info.get('winner') == env.agent_name:
            total_wins += 1
        total_games += 1
        
        # Record statistics
        training_stats['episode_rewards'].append(episode_reward)
        training_stats['episode_lengths'].append(episode_length)
        training_stats['q_table_sizes'].append(len(agent.q_table))
        training_stats['epsilon_values'].append(agent.epsilon)
        
        # Decay epsilon
        agent.decay_epsilon()
        
        # Periodic evaluation
        if (episode + 1) % eval_interval == 0:
            win_rate = evaluate_agent(env, agent, eval_episodes, opponent_agents, verbose=False)
            training_stats['win_rates'].append(win_rate)
            
            if verbose:
                avg_reward = sum(training_stats['episode_rewards'][-eval_interval:]) / eval_interval
                avg_length = sum(training_stats['episode_lengths'][-eval_interval:]) / eval_interval
                print(f"Episode {episode + 1}/{num_episodes}")
                print(f"  Avg Reward: {avg_reward:.2f}, Avg Length: {avg_length:.1f}")
                print(f"  Win Rate: {win_rate:.1%}, Epsilon: {agent.epsilon:.3f}")
                print(f"  Q-table size: {len(agent.q_table)}")
                print(f"  Overall Win Rate: {total_wins/total_games:.1%}" if total_games > 0 else "")
                print("-" * 60)
        
        # Progress update for long training
        elif verbose and (episode + 1) % 100 == 0:
            print(f"Episode {episode + 1}/{num_episodes} - Epsilon: {agent.epsilon:.3f}, "
                  f"Q-table: {len(agent.q_table)} states")
    
    elapsed_time = time.time() - start_time
    
    if verbose:
        print(f"\nTraining completed in {elapsed_time:.1f} seconds")
        print(f"Final epsilon: {agent.epsilon:.3f}")
        print(f"Final Q-table size: {len(agent.q_table)} states")
        print(f"Overall win rate: {total_wins/total_games:.1%}" if total_games > 0 else "")
    
    training_stats['total_episodes'] = num_episodes
    training_stats['total_wins'] = total_wins
    training_stats['total_games'] = total_games
    training_stats['elapsed_time'] = elapsed_time
    
    return training_stats


def evaluate_agent(env: Flip7RLEnv, agent: QLearningAgent, num_episodes: int = 10,
                   opponent_agents: List = None, verbose: bool = True) -> float:
    """
    Evaluate agent performance.
    
    Args:
        env: RL environment
        agent: Agent to evaluate
        num_episodes: Number of evaluation episodes
        opponent_agents: List of opponent agents
        verbose: Whether to print results
        
    Returns:
        Win rate (0.0 to 1.0)
    """
    wins = 0
    
    # Set agent to evaluation mode (no exploration)
    original_epsilon = agent.epsilon
    agent.set_epsilon(0.0)
    
    for episode in range(num_episodes):
        state, info = env.reset()
        done = False
        
        while not done:
            valid_actions = env.get_valid_actions()
            
            if not valid_actions:
                # Wait for turn
                state, _, done, _ = env.step(0)
                continue
            
            action = agent.select_action(state, valid_actions, training=False)
            state, _, done, info = env.step(action)
        
        if info.get('winner') == env.agent_name:
            wins += 1
    
    # Restore epsilon
    agent.set_epsilon(original_epsilon)
    
    win_rate = wins / num_episodes if num_episodes > 0 else 0.0
    
    if verbose:
        print(f"Evaluation: {wins}/{num_episodes} wins ({win_rate:.1%})")
    
    return win_rate


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description="Train Q-Learning agent for Flip 7")
    parser.add_argument('--episodes', type=int, default=1000, help='Number of training episodes')
    parser.add_argument('--eval-interval', type=int, default=100, help='Evaluation interval')
    parser.add_argument('--eval-episodes', type=int, default=10, help='Episodes per evaluation')
    parser.add_argument('--learning-rate', type=float, default=0.1, help='Learning rate (alpha)')
    parser.add_argument('--discount', type=float, default=0.95, help='Discount factor (gamma)')
    parser.add_argument('--epsilon', type=float, default=1.0, help='Initial epsilon')
    parser.add_argument('--epsilon-min', type=float, default=0.1, help='Minimum epsilon')
    parser.add_argument('--epsilon-decay', type=float, default=0.995, help='Epsilon decay rate')
    parser.add_argument('--target-score', type=int, default=200, help='Target score to win')
    parser.add_argument('--opponent', type=str, default='heuristic',
                       choices=['random', 'heuristic', 'conservative', 'aggressive'],
                       help='Opponent agent type')
    parser.add_argument('--save', type=str, default='q_table.pkl', help='Path to save Q-table')
    parser.add_argument('--load', type=str, default=None, help='Path to load Q-table')
    parser.add_argument('--verbose', action='store_true', default=True, help='Print progress')
    
    args = parser.parse_args()
    
    # Create opponent agents
    opponent_agent_map = {
        'random': RandomAgent(),
        'heuristic': HeuristicAgent(),
        'conservative': ConservativeAgent(),
        'aggressive': AggressiveAgent()
    }
    opponent_agent = opponent_agent_map[args.opponent]
    
    # Create environment
    env = Flip7RLEnv(
        agent_name="QLearningAgent",
        opponent_names=["Opponent1", "Opponent2"],
        target_score=args.target_score,
        agent_index=0,
        opponent_agents=[opponent_agent, opponent_agent]
    )
    
    # Create Q-Learning agent
    agent = QLearningAgent(
        name="QLearningAgent",
        learning_rate=args.learning_rate,
        discount_factor=args.discount,
        epsilon=args.epsilon,
        epsilon_min=args.epsilon_min,
        epsilon_decay=args.epsilon_decay
    )
    
    # Load existing Q-table if specified
    if args.load:
        try:
            agent.load_q_table(args.load)
            print(f"Loaded Q-table from {args.load}")
        except FileNotFoundError:
            print(f"Warning: Could not load Q-table from {args.load}, starting fresh")
    
    # Train agent
    training_stats = train_agent(
        env, agent,
        num_episodes=args.episodes,
        eval_interval=args.eval_interval,
        eval_episodes=args.eval_episodes,
        opponent_agents=[opponent_agent, opponent_agent],
        verbose=args.verbose
    )
    
    # Save Q-table
    agent.save_q_table(args.save)
    print(f"Saved Q-table to {args.save}")
    
    # Print final statistics
    stats = agent.get_statistics()
    print("\nAgent Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()

