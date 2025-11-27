"""
Curriculum learning script for Q-Learning agent.

Starts training with easier opponents and gradually increases difficulty.
This helps the agent learn more effectively by building up skills progressively.
"""

import argparse
import sys
import os
from datetime import datetime
from rl_env import Flip7RLEnv
from q_learning_agent import QLearningAgent
from agents import RandomAgent, HeuristicAgent, ConservativeAgent
from train import train_agent, evaluate_agent


class TeeOutput:
    """Class to write output to both console and file."""
    def __init__(self, file_path):
        self.terminal = sys.stdout
        self.log_file = open(file_path, 'a', encoding='utf-8')
    
    def write(self, message):
        self.terminal.write(message)
        self.log_file.write(message)
        self.log_file.flush()
    
    def flush(self):
        self.terminal.flush()
        self.log_file.flush()
    
    def close(self):
        self.log_file.close()


def curriculum_training(
    total_episodes: int = 10000,
    eval_episodes: int = 50,
    eval_interval: int = 500,
    learning_rate: float = 0.25,
    discount_factor: float = 0.90,
    epsilon: float = 1.0,
    epsilon_min: float = 0.05,
    epsilon_decay: float = 0.998
):
    """
    Train agent using curriculum learning.
    
    Curriculum stages:
    1. Random opponents (easiest) - 30% of training
    2. Conservative opponents (medium) - 40% of training
    3. Heuristic opponents (harder) - 30% of training
    
    Args:
        total_episodes: Total number of training episodes
        eval_episodes: Number of episodes for evaluation
        eval_interval: Interval between evaluations
        learning_rate: Learning rate (alpha) for Q-learning
        discount_factor: Discount factor (gamma) for future rewards
        epsilon: Initial exploration rate
        epsilon_min: Minimum exploration rate
        epsilon_decay: Epsilon decay rate per episode
    """
    env = Flip7RLEnv()
    
    # Create agents for different difficulty levels
    random_opponents = [RandomAgent("Random1"), RandomAgent("Random2")]
    conservative_opponents = [ConservativeAgent("Conservative1"), ConservativeAgent("Conservative2")]
    heuristic_opponents = [HeuristicAgent("Heuristic1"), HeuristicAgent("Heuristic2")]
    
    # Initialize Q-learning agent with custom hyperparameters
    agent = QLearningAgent(
        name="CurriculumQLearning",
        learning_rate=learning_rate,
        discount_factor=discount_factor,
        epsilon=epsilon,
        epsilon_min=epsilon_min,
        epsilon_decay=epsilon_decay
    )
    
    # Curriculum stages (optimized for better learning)
    # More time on harder opponents for better adaptation
    stage1_episodes = int(total_episodes * 0.25)  # Random opponents (reduced from 0.3)
    stage2_episodes = int(total_episodes * 0.35)   # Conservative opponents (reduced from 0.4)
    stage3_episodes = total_episodes - stage1_episodes - stage2_episodes  # Heuristic opponents (increased to 0.4)
    
    print("=" * 70)
    print("CURRICULUM LEARNING")
    print("=" * 70)
    print(f"Total episodes: {total_episodes}")
    print(f"Learning rate: {learning_rate}, Discount: {discount_factor}")
    print(f"Stage 1 (Random): {stage1_episodes} episodes")
    print(f"Stage 2 (Conservative): {stage2_episodes} episodes")
    print(f"Stage 3 (Heuristic): {stage3_episodes} episodes")
    print("=" * 70)
    
    all_stats = {
        'episode_rewards': [],
        'episode_lengths': [],
        'win_rates': [],
        'q_table_sizes': [],
        'epsilon_values': []
    }
    
    # Stage 1: Random opponents (easiest)
    print("\n" + "=" * 70)
    print("STAGE 1: Training against Random opponents")
    print("=" * 70)
    # Update environment's opponent agents
    env.opponent_agents = random_opponents
    stats1 = train_agent(
        env, agent,
        num_episodes=stage1_episodes,
        eval_interval=eval_interval,
        eval_episodes=eval_episodes,
        opponent_agents=random_opponents,
        verbose=True
    )
    
    # Merge stats
    for key in all_stats:
        all_stats[key].extend(stats1.get(key, []))
    
    # Stage 2: Conservative opponents (medium difficulty)
    print("\n" + "=" * 70)
    print("STAGE 2: Training against Conservative opponents")
    print("=" * 70)
    # Boost learning rate slightly for adaptation (but don't reset completely)
    # This helps the agent adapt to new opponent strategies
    agent.learning_rate = min(learning_rate, agent.learning_rate * 1.5)
    print(f"Adjusted learning rate to {agent.learning_rate:.3f} for Stage 2")
    
    # Update environment's opponent agents
    env.opponent_agents = conservative_opponents
    stats2 = train_agent(
        env, agent,
        num_episodes=stage2_episodes,
        eval_interval=eval_interval,
        eval_episodes=eval_episodes,
        opponent_agents=conservative_opponents,
        verbose=True
    )
    
    # Merge stats
    for key in all_stats:
        all_stats[key].extend(stats2.get(key, []))
    
    # Stage 3: Heuristic opponents (harder)
    print("\n" + "=" * 70)
    print("STAGE 3: Training against Heuristic opponents")
    print("=" * 70)
    # Reset learning rate to a higher value for Stage 3 to ensure adaptation
    # Use at least 50% of original learning rate, but boost significantly
    # This is critical because the agent needs to "unlearn" Conservative strategies
    # and learn new strategies for Heuristic opponents
    stage3_lr = max(learning_rate * 0.5, 0.1)  # At least 50% of original or 0.1
    agent.set_learning_rate(stage3_lr)
    # Disable learning rate decay during Stage 3 to maintain learning capacity
    agent.disable_learning_rate_decay()
    print(f"Reset learning rate to {agent.learning_rate:.3f} for Stage 3")
    print(f"Learning rate decay DISABLED for Stage 3 to maintain adaptation")
    
    # Update environment's opponent agents
    env.opponent_agents = heuristic_opponents
    stats3 = train_agent(
        env, agent,
        num_episodes=stage3_episodes,
        eval_interval=eval_interval,
        eval_episodes=eval_episodes,
        opponent_agents=heuristic_opponents,
        verbose=True
    )
    
    # Merge stats
    for key in all_stats:
        all_stats[key].extend(stats3.get(key, []))
    
    # Re-enable learning rate decay for final evaluation (optional, but cleaner)
    agent.enable_learning_rate_decay()
    
    # Final evaluation against all opponent types
    print("\n" + "=" * 70)
    print("FINAL EVALUATION")
    print("=" * 70)
    
    for opponent_name, opponents in [
        ("Random", random_opponents),
        ("Conservative", conservative_opponents),
        ("Heuristic", heuristic_opponents)
    ]:
        win_rate = evaluate_agent(
            env, agent,
            num_episodes=eval_episodes * 2,  # More episodes for final eval
            opponent_agents=opponents,
            verbose=False
        )
        print(f"Win rate vs {opponent_name}: {win_rate:.1%}")
    
    # Save final Q-table
    agent.save_q_table("q_table_curriculum.pkl")
    print(f"\nSaved Q-table to q_table_curriculum.pkl")
    print(f"Final Q-table size: {len(agent.q_table)} states")
    
    return all_stats, agent


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Curriculum learning for Q-Learning agent")
    parser.add_argument("--episodes", type=int, default=10000, help="Total training episodes")
    parser.add_argument("--eval-episodes", type=int, default=50, help="Evaluation episodes")
    parser.add_argument("--eval-interval", type=int, default=500, help="Evaluation interval")
    parser.add_argument("--learning-rate", type=float, default=0.25, help="Learning rate (alpha)")
    parser.add_argument("--discount", type=float, default=0.90, help="Discount factor (gamma)")
    parser.add_argument("--epsilon", type=float, default=1.0, help="Initial epsilon")
    parser.add_argument("--epsilon-min", type=float, default=0.05, help="Minimum epsilon")
    parser.add_argument("--epsilon-decay", type=float, default=0.998, help="Epsilon decay rate")
    parser.add_argument("--log-file", type=str, default=None, 
                       help="File to append output to (default: curriculum_training_YYYYMMDD_HHMMSS.log)")
    
    args = parser.parse_args()
    
    # Create log directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Set up file logging
    if args.log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.log_file = f"curriculum_training_{timestamp}.log"
    
    # Ensure log file is in the logs directory
    # If user provided a custom path, use it as-is if it's absolute, otherwise put in logs/
    if not os.path.isabs(args.log_file):
        args.log_file = os.path.join(log_dir, args.log_file)
    
    # Redirect output to both console and file
    tee = TeeOutput(args.log_file)
    sys.stdout = tee
    
    try:
        print(f"\n{'='*70}")
        print(f"Curriculum Learning Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Logging to: {args.log_file}")
        print(f"{'='*70}\n")
        
        curriculum_training(
            total_episodes=args.episodes,
            eval_episodes=args.eval_episodes,
            eval_interval=args.eval_interval,
            learning_rate=args.learning_rate,
            discount_factor=args.discount,
            epsilon=args.epsilon,
            epsilon_min=args.epsilon_min,
            epsilon_decay=args.epsilon_decay
        )
        
        print(f"\n{'='*70}")
        print(f"Curriculum Learning Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Output saved to: {args.log_file}")
        print(f"{'='*70}\n")
    finally:
        # Restore stdout and close file
        sys.stdout = tee.terminal
        tee.close()

