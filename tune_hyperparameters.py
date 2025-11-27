"""
Hyperparameter tuning script for Q-Learning agent.

Tests different combinations of learning rate and discount factor
to find optimal hyperparameters.
"""

import argparse
import time
from typing import Dict, Tuple
from rl_env import Flip7RLEnv
from q_learning_agent import QLearningAgent
from agents import RandomAgent, HeuristicAgent
from train import train_agent, evaluate_agent


def tune_hyperparameters(num_episodes: int = 2000, eval_episodes: int = 50,
                        quick_test: bool = False) -> Dict:
    """
    Test different hyperparameter combinations.
    
    Args:
        num_episodes: Number of training episodes per configuration
        eval_episodes: Number of evaluation episodes
        quick_test: If True, test fewer combinations (for quick testing)
        
    Returns:
        Dictionary mapping (lr, discount) -> (win_rate, avg_reward)
    """
    # Hyperparameter ranges to test
    if quick_test:
        learning_rates = [0.1, 0.2, 0.3]
        discount_factors = [0.85, 0.90, 0.95]
    else:
        learning_rates = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
        discount_factors = [0.80, 0.85, 0.90, 0.95, 0.99]
    
    opponent_agent = HeuristicAgent()
    results = {}
    
    total_combinations = len(learning_rates) * len(discount_factors)
    current = 0
    
    print("=" * 70)
    print(f"Hyperparameter Tuning: Testing {total_combinations} combinations")
    print(f"Episodes per config: {num_episodes}, Eval episodes: {eval_episodes}")
    print("=" * 70)
    
    for lr in learning_rates:
        for discount in discount_factors:
            current += 1
            print(f"\n[{current}/{total_combinations}] Testing LR={lr:.2f}, Discount={discount:.2f}")
            print("-" * 70)
            
            # Create fresh environment and agent for each test
            env = Flip7RLEnv(
                agent_name="QLearningAgent",
                opponent_names=["Opponent1", "Opponent2"],
                target_score=200,
                agent_index=0,
                opponent_agents=[opponent_agent, opponent_agent]
            )
            
            agent = QLearningAgent(
                name="QLearningAgent",
                learning_rate=lr,
                discount_factor=discount,
                epsilon=1.0,
                epsilon_min=0.05,
                epsilon_decay=0.998
            )
            
            # Train
            start_time = time.time()
            training_stats = train_agent(
                env, agent,
                num_episodes=num_episodes,
                eval_interval=num_episodes,  # Only evaluate at end
                eval_episodes=eval_episodes,
                opponent_agents=[opponent_agent, opponent_agent],
                verbose=False  # Less verbose for tuning
            )
            train_time = time.time() - start_time
            
            # Get training win rate from stats (if available)
            training_win_rate = 0.0
            if training_stats.get('win_rates'):
                training_win_rate = training_stats['win_rates'][-1] if training_stats['win_rates'] else 0.0
            
            # Evaluate using the existing function
            win_rate = evaluate_agent(
                env, agent,
                num_episodes=eval_episodes,
                opponent_agents=[opponent_agent, opponent_agent],
                verbose=False
            )
            
            # Calculate avg reward separately
            total_rewards = 0.0
            original_epsilon = agent.epsilon
            agent.set_epsilon(0.0)  # Greedy evaluation
            
            for _ in range(min(10, eval_episodes)):  # Sample a few episodes for avg reward
                state, info = env.reset()
                done = False
                episode_reward = 0.0
                max_steps = 1000
                step_count = 0
                
                while not done and step_count < max_steps:
                    step_count += 1
                    valid_actions = env.get_valid_actions()
                    
                    if not valid_actions:
                        state, reward, done, info = env.step(0)
                        episode_reward += reward
                    else:
                        action = agent.select_action(state, valid_actions, training=False)
                        state, reward, done, info = env.step(action)
                        episode_reward += reward
                
                total_rewards += episode_reward
            
            agent.set_epsilon(original_epsilon)
            avg_reward = total_rewards / min(10, eval_episodes) if eval_episodes > 0 else 0.0
            
            # Get final stats
            stats = agent.get_statistics()
            
            results[(lr, discount)] = {
                'win_rate': win_rate,
                'q_table_size': stats['q_table_size'],
                'train_time': train_time,
                'avg_reward': avg_reward
            }
            
            print(f"  Eval Win Rate: {win_rate:.1%} | Training Win Rate: {training_win_rate:.1%} | "
                  f"Q-table: {stats['q_table_size']} | Time: {train_time:.1f}s")
    
    return results


def print_results(results: Dict):
    """Print formatted results table."""
    print("\n" + "=" * 70)
    print("HYPERPARAMETER TUNING RESULTS")
    print("=" * 70)
    
    # Sort by win rate
    sorted_results = sorted(results.items(), key=lambda x: x[1]['win_rate'], reverse=True)
    
    print(f"\n{'Rank':<6} {'LR':<8} {'Discount':<10} {'Win Rate':<12} {'Q-Table':<12} {'Time':<10}")
    print("-" * 70)
    
    for rank, ((lr, discount), stats) in enumerate(sorted_results, 1):
        print(f"{rank:<6} {lr:<8.2f} {discount:<10.2f} {stats['win_rate']:<12.1%} "
              f"{stats['q_table_size']:<12} {stats['train_time']:<10.1f}s")
    
    # Best configuration
    best = sorted_results[0]
    (best_lr, best_discount), best_stats = best
    print("\n" + "=" * 70)
    print("BEST CONFIGURATION:")
    print(f"  Learning Rate: {best_lr:.2f}")
    print(f"  Discount Factor: {best_discount:.2f}")
    print(f"  Win Rate: {best_stats['win_rate']:.1%}")
    print(f"  Q-table Size: {best_stats['q_table_size']}")
    print("=" * 70)
    
    return best_lr, best_discount


def main():
    parser = argparse.ArgumentParser(description="Tune Q-Learning hyperparameters")
    parser.add_argument('--episodes', type=int, default=2000, 
                       help='Training episodes per configuration')
    parser.add_argument('--eval-episodes', type=int, default=50,
                       help='Evaluation episodes per configuration')
    parser.add_argument('--quick', action='store_true',
                       help='Quick test with fewer combinations')
    
    args = parser.parse_args()
    
    results = tune_hyperparameters(
        num_episodes=args.episodes,
        eval_episodes=args.eval_episodes,
        quick_test=args.quick
    )
    
    best_lr, best_discount = print_results(results)
    
    print(f"\nRecommended training command:")
    print(f"python train.py --episodes 5000 --learning-rate {best_lr:.2f} --discount {best_discount:.2f}")


if __name__ == "__main__":
    main()

