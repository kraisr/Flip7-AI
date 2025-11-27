"""
Logging utilities for RL training and evaluation.

This module provides functions for logging training metrics, saving statistics,
and optionally plotting learning curves.
"""

import json
import csv
from typing import Dict, List
from datetime import datetime
import os


class TrainingLogger:
    """Logger for training statistics."""
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize logger.
        
        Args:
            log_dir: Directory to save log files
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"training_{self.timestamp}.json")
        self.csv_file = os.path.join(log_dir, f"training_{self.timestamp}.csv")
        
        self.episode_data = []
    
    def log_episode(self, episode: int, reward: float, length: int,
                   q_table_size: int, epsilon: float, **kwargs) -> None:
        """
        Log episode statistics.
        
        Args:
            episode: Episode number
            reward: Episode reward
            length: Episode length
            q_table_size: Size of Q-table
            epsilon: Current epsilon value
            **kwargs: Additional metrics to log
        """
        data = {
            'episode': episode,
            'reward': reward,
            'length': length,
            'q_table_size': q_table_size,
            'epsilon': epsilon,
            **kwargs
        }
        self.episode_data.append(data)
    
    def log_evaluation(self, episode: int, win_rate: float, **kwargs) -> None:
        """
        Log evaluation results.
        
        Args:
            episode: Episode number when evaluation occurred
            win_rate: Win rate from evaluation
            **kwargs: Additional evaluation metrics
        """
        # Find or create evaluation entry
        eval_data = {
            'episode': episode,
            'win_rate': win_rate,
            **kwargs
        }
        
        # Add to episode data if episode exists, otherwise create new entry
        for ep_data in self.episode_data:
            if ep_data['episode'] == episode:
                ep_data.update(eval_data)
                return
        
        # Episode not found, add new entry
        self.episode_data.append(eval_data)
    
    def save_json(self) -> None:
        """Save all logged data to JSON file."""
        with open(self.log_file, 'w') as f:
            json.dump(self.episode_data, f, indent=2)
        print(f"Saved training log to {self.log_file}")
    
    def save_csv(self) -> None:
        """Save all logged data to CSV file."""
        if not self.episode_data:
            return
        
        # Get all unique keys
        all_keys = set()
        for data in self.episode_data:
            all_keys.update(data.keys())
        
        fieldnames = sorted(all_keys)
        
        with open(self.csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for data in self.episode_data:
                writer.writerow(data)
        
        print(f"Saved training log to {self.csv_file}")
    
    def save(self) -> None:
        """Save logs in both JSON and CSV formats."""
        self.save_json()
        self.save_csv()
    
    def load(self, filepath: str) -> None:
        """
        Load logged data from file.
        
        Args:
            filepath: Path to log file (JSON or CSV)
        """
        if filepath.endswith('.json'):
            with open(filepath, 'r') as f:
                self.episode_data = json.load(f)
        elif filepath.endswith('.csv'):
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                self.episode_data = list(reader)
                # Convert numeric strings to numbers
                for data in self.episode_data:
                    for key, value in data.items():
                        try:
                            if '.' in value:
                                data[key] = float(value)
                            else:
                                data[key] = int(value)
                        except (ValueError, TypeError):
                            pass
        else:
            raise ValueError("File must be .json or .csv")
    
    def get_metrics(self) -> Dict:
        """
        Get summary metrics from logged data.
        
        Returns:
            Dictionary with summary statistics
        """
        if not self.episode_data:
            return {}
        
        rewards = [d.get('reward', 0) for d in self.episode_data if 'reward' in d]
        lengths = [d.get('length', 0) for d in self.episode_data if 'length' in d]
        win_rates = [d.get('win_rate', 0) for d in self.episode_data if 'win_rate' in d]
        
        metrics = {}
        
        if rewards:
            metrics['avg_reward'] = sum(rewards) / len(rewards)
            metrics['max_reward'] = max(rewards)
            metrics['min_reward'] = min(rewards)
        
        if lengths:
            metrics['avg_length'] = sum(lengths) / len(lengths)
            metrics['max_length'] = max(lengths)
            metrics['min_length'] = min(lengths)
        
        if win_rates:
            metrics['avg_win_rate'] = sum(win_rates) / len(win_rates)
            metrics['max_win_rate'] = max(win_rates)
            metrics['min_win_rate'] = min(win_rates)
        
        return metrics


def plot_learning_curves(log_file: str, output_file: str = None) -> None:
    """
    Plot learning curves from log file.
    
    Requires matplotlib to be installed.
    
    Args:
        log_file: Path to log file (JSON or CSV)
        output_file: Path to save plot (optional)
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Warning: matplotlib not installed. Cannot plot learning curves.")
        return
    
    logger = TrainingLogger()
    logger.load(log_file)
    
    if not logger.episode_data:
        print("No data to plot")
        return
    
    episodes = [d['episode'] for d in logger.episode_data if 'episode' in d]
    rewards = [d.get('reward', 0) for d in logger.episode_data if 'reward' in d]
    win_rates = [d.get('win_rate', None) for d in logger.episode_data if 'win_rate' in d]
    epsilons = [d.get('epsilon', 0) for d in logger.episode_data if 'epsilon' in d]
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    # Plot rewards
    if rewards:
        axes[0, 0].plot(episodes[:len(rewards)], rewards)
        axes[0, 0].set_title('Episode Rewards')
        axes[0, 0].set_xlabel('Episode')
        axes[0, 0].set_ylabel('Reward')
        axes[0, 0].grid(True)
    
    # Plot win rates
    if any(wr is not None for wr in win_rates):
        eval_episodes = [ep for ep, wr in zip(episodes, win_rates) if wr is not None]
        eval_win_rates = [wr for wr in win_rates if wr is not None]
        if eval_episodes:
            axes[0, 1].plot(eval_episodes, eval_win_rates, 'o-')
            axes[0, 1].set_title('Win Rate (Evaluation)')
            axes[0, 1].set_xlabel('Episode')
            axes[0, 1].set_ylabel('Win Rate')
            axes[0, 1].grid(True)
            axes[0, 1].set_ylim([0, 1])
    
    # Plot epsilon
    if epsilons:
        axes[1, 0].plot(episodes[:len(epsilons)], epsilons)
        axes[1, 0].set_title('Epsilon (Exploration)')
        axes[1, 0].set_xlabel('Episode')
        axes[1, 0].set_ylabel('Epsilon')
        axes[1, 0].grid(True)
    
    # Plot moving average of rewards
    if rewards and len(rewards) > 10:
        window = min(100, len(rewards) // 10)
        moving_avg = []
        for i in range(len(rewards)):
            start = max(0, i - window + 1)
            moving_avg.append(sum(rewards[start:i+1]) / (i - start + 1))
        
        axes[1, 1].plot(episodes[:len(rewards)], rewards, alpha=0.3, label='Raw')
        axes[1, 1].plot(episodes[:len(rewards)], moving_avg, label=f'Moving Avg (window={window})')
        axes[1, 1].set_title('Reward Moving Average')
        axes[1, 1].set_xlabel('Episode')
        axes[1, 1].set_ylabel('Reward')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file)
        print(f"Saved plot to {output_file}")
    else:
        plt.show()




