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
        
        # Safety limit to prevent infinite loops
        # Note: Full games can take 500-2000 steps depending on target score
        max_steps_per_episode = 2000
        step_count = 0
        
        while not done and step_count < max_steps_per_episode:
            step_count += 1
            
            # Get valid actions for the agent's current turn
            valid_actions = env.get_valid_actions()
            
            # Handle no valid actions (e.g., it's opponents' turns or agent has ended turn)
            if not valid_actions:
                # Check if game is actually over
                if env.game.is_game_over():
                    done = True
                    break
                
                # Advance one environment step (will simulate opponent turns until agent's turn)
                state, reward, done, info = env.step(0)  # Dummy/pass/advance action
                episode_reward += reward
                episode_length += 1
                
                # Double-check done flag
                if env.game.is_game_over():
                    done = True
                
                if done:
                    break  # Episode finished
                    
                continue  # Re-check valid_actions for the agent
            
            # Select action with epsilon-greedy policy
            action = agent.select_action(state, valid_actions, training=True)
            
            # Take step in environment
            next_state, reward, done, info = env.step(action)
            
            # Get valid actions for next state (if not terminal)
            next_valid_actions = env.get_valid_actions() if not done else []
            
            # Q-learning update using CORRECT transition (s, a, r, s')
            agent.update_q_value(state, action, reward, next_state, next_valid_actions)
            
            # Update episode statistics
            episode_reward += reward
            episode_length += 1
            
            # Transition to next state
            state = next_state
        
        # Safety check for infinite loops
        if step_count >= max_steps_per_episode:
            if verbose:
                print(f"Warning: Episode {episode + 1} hit step limit ({max_steps_per_episode})")
                print(f"  Final state: Round {env.game.round_number}, "
                      f"Agent score: {env.game.players[env.agent_index].total_score}, "
                      f"Game over: {env.game.is_game_over()}")
            done = True
        
        # Debug: Print episode completion (helpful for diagnosing hangs)
        if verbose and (episode + 1) % 10 == 0:
            print(f"Finished episode {episode + 1} | reward={episode_reward:.2f}, length={episode_length}")
        
        # Check if agent won
        if info.get('winner') == env.agent_name:
            total_wins += 1
        total_games += 1
        
        # Record statistics
        training_stats['episode_rewards'].append(episode_reward)
        training_stats['episode_lengths'].append(episode_length)
        training_stats['q_table_sizes'].append(len(agent.q_table))
        training_stats['epsilon_values'].append(agent.epsilon)
        
        # Decay epsilon and learning rate
        agent.decay_epsilon()
        agent.decay_learning_rate()
        
        # Periodic evaluation
        if (episode + 1) % eval_interval == 0:
            win_rate = evaluate_agent(env, agent, eval_episodes, opponent_agents, verbose=verbose)
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
    total_rewards = 0.0
    q_value_stats = {'hit': [], 'stay': []}
    unknown_states = 0
    total_decisions = 0
    
    # Update environment's opponent agents if provided
    if opponent_agents is not None:
        env.opponent_agents = opponent_agents
    
    # Set agent to evaluation mode (no exploration)
    original_epsilon = agent.epsilon
    agent.set_epsilon(0.0)
    
    for episode in range(num_episodes):
        state, info = env.reset()
        done = False
        episode_reward = 0.0
        step_count = 0
        max_steps_per_episode = 1000  # Safety limit for evaluation
        
        while not done and step_count < max_steps_per_episode:
            valid_actions = env.get_valid_actions()
            
            if not valid_actions:
                # Wait for turn - but limit how long we wait
                state, reward, done, info = env.step(0)
                episode_reward += reward
                step_count += 1
                # Safety: if we've waited too long, break
                if step_count >= max_steps_per_episode:
                    if verbose:
                        print(f"Warning: Evaluation episode {episode + 1} hit step limit")
                    break
                continue
            
            # Get Q-values for debugging (first episode only)
            if episode == 0 and verbose:
                q_hit = agent.get_q_value(state, 0)
                q_stay = agent.get_q_value(state, 1)
                q_value_stats['hit'].append(q_hit)
                q_value_stats['stay'].append(q_stay)
                
                # Check if state is unknown (both Q-values are 0.0)
                if q_hit == 0.0 and q_stay == 0.0:
                    unknown_states += 1
                total_decisions += 1
            
            action = agent.select_action(state, valid_actions, training=False)
            state, reward, done, info = env.step(action)
            episode_reward += reward
            step_count += 1
        
        total_rewards += episode_reward
        
        if info.get('winner') == env.agent_name:
            wins += 1
    
    # Restore epsilon
    agent.set_epsilon(original_epsilon)
    
    win_rate = wins / num_episodes if num_episodes > 0 else 0.0
    avg_reward = total_rewards / num_episodes if num_episodes > 0 else 0.0
    
    if verbose:
        print(f"Evaluation: {wins}/{num_episodes} wins ({win_rate:.1%})")
        print(f"  Avg Reward: {avg_reward:.2f}")
        if total_decisions > 0:
            unknown_rate = unknown_states / total_decisions
            avg_q_hit = sum(q_value_stats['hit']) / len(q_value_stats['hit']) if q_value_stats['hit'] else 0.0
            avg_q_stay = sum(q_value_stats['stay']) / len(q_value_stats['stay']) if q_value_stats['stay'] else 0.0
            print(f"  Unknown States: {unknown_rate:.1%} ({unknown_states}/{total_decisions})")
            print(f"  Avg Q(HIT): {avg_q_hit:.2f}, Avg Q(STAY): {avg_q_stay:.2f}")
    
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




