"""
Evaluation script for trained Q-Learning agent in Flip 7 game.

This script evaluates a trained agent against various baseline agents
and generates performance metrics.
"""

import argparse
from typing import List, Dict
from rl_env import Flip7RLEnv
from q_learning_agent import QLearningAgent
from agents import RandomAgent, HeuristicAgent, ConservativeAgent, AggressiveAgent, SmartHeuristicAgent


def evaluate_against_opponents(env: Flip7RLEnv, agent: QLearningAgent,
                               num_episodes: int = 100,
                               opponent_agents: List = None) -> Dict:
    """
    Evaluate agent against opponents.
    
    Args:
        env: RL environment
        agent: Agent to evaluate
        num_episodes: Number of evaluation episodes
        opponent_agents: List of opponent agents
        
    Returns:
        Dictionary with evaluation metrics
    """
    if opponent_agents is None:
        opponent_agents = [HeuristicAgent(), HeuristicAgent()]
    
    wins = 0
    total_score = 0
    opponent_scores = [0, 0]
    round_wins = 0
    total_rounds = 0
    episode_rewards = []
    episode_lengths = []
    
    # Set agent to evaluation mode
    original_epsilon = agent.epsilon
    agent.set_epsilon(0.0)
    
    for episode in range(num_episodes):
        state, info = env.reset()
        episode_reward = 0.0
        episode_length = 0
        done = False
        episode_round_wins = 0
        
        while not done:
            valid_actions = env.get_valid_actions()
            
            if not valid_actions:
                state, _, done, _ = env.step(0)
                episode_length += 1
                continue
            
            action = agent.select_action(state, valid_actions, training=False)
            state, reward, done, info = env.step(action)
            
            episode_reward += reward
            episode_length += 1
            
            # Track round wins
            if info.get('round_ended'):
                total_rounds += 1
                agent_player = env.game.players[env.agent_index]
                opponent_round_scores = [
                    env.game.players[i].round_score 
                    for i in range(3) if i != env.agent_index
                ]
                if agent_player.round_score > max(opponent_round_scores):
                    episode_round_wins += 1
        
        # Record episode results
        if info.get('winner') == env.agent_name:
            wins += 1
        
        agent_player = env.game.players[env.agent_index]
        total_score += agent_player.total_score
        
        for i, player in enumerate(env.game.players):
            if i != env.agent_index:
                opp_idx = 0 if i < env.agent_index else 1
                if opp_idx < len(opponent_scores):
                    opponent_scores[opp_idx] += player.total_score
        
        round_wins += episode_round_wins
        episode_rewards.append(episode_reward)
        episode_lengths.append(episode_length)
    
    # Restore epsilon
    agent.set_epsilon(original_epsilon)
    
    # Calculate metrics
    win_rate = wins / num_episodes if num_episodes > 0 else 0.0
    avg_score = total_score / num_episodes if num_episodes > 0 else 0.0
    avg_opponent_score = sum(opponent_scores) / (len(opponent_scores) * num_episodes) if num_episodes > 0 else 0.0
    round_win_rate = round_wins / total_rounds if total_rounds > 0 else 0.0
    avg_reward = sum(episode_rewards) / len(episode_rewards) if episode_rewards else 0.0
    avg_length = sum(episode_lengths) / len(episode_lengths) if episode_lengths else 0.0
    
    return {
        'win_rate': win_rate,
        'wins': wins,
        'total_episodes': num_episodes,
        'avg_score': avg_score,
        'avg_opponent_score': avg_opponent_score,
        'round_win_rate': round_win_rate,
        'round_wins': round_wins,
        'total_rounds': total_rounds,
        'avg_reward': avg_reward,
        'avg_episode_length': avg_length
    }


def compare_against_all_baselines(env: Flip7RLEnv, agent: QLearningAgent,
                                  num_episodes: int = 50) -> Dict:
    """
    Compare agent against all baseline agents.
    
    Args:
        env: RL environment
        agent: Agent to evaluate
        num_episodes: Number of episodes per opponent
        
    Returns:
        Dictionary with comparison results
    """
    baseline_agents = {
        'Random': RandomAgent(),
        'Heuristic': HeuristicAgent(),
        'Conservative': ConservativeAgent(),
        'Aggressive': AggressiveAgent(),
        'SmartHeuristic': SmartHeuristicAgent()
    }
    
    results = {}
    
    print("Evaluating against baseline agents...")
    print("=" * 60)
    
    for name, baseline_agent in baseline_agents.items():
        print(f"\nEvaluating against {name} agent...")
        env.opponent_agents = [baseline_agent, baseline_agent]
        
        metrics = evaluate_against_opponents(env, agent, num_episodes, 
                                            [baseline_agent, baseline_agent])
        results[name] = metrics
        
        print(f"  Win Rate: {metrics['win_rate']:.1%}")
        print(f"  Avg Score: {metrics['avg_score']:.1f} vs {metrics['avg_opponent_score']:.1f}")
        print(f"  Round Win Rate: {metrics['round_win_rate']:.1%}")
        print(f"  Avg Episode Length: {metrics['avg_episode_length']:.1f}")
    
    return results


def main():
    """Main evaluation function."""
    parser = argparse.ArgumentParser(description="Evaluate Q-Learning agent for Flip 7")
    parser.add_argument('--episodes', type=int, default=100, help='Number of evaluation episodes')
    parser.add_argument('--q-table', type=str, required=True, help='Path to Q-table file')
    parser.add_argument('--opponent', type=str, default='heuristic',
                       choices=['random', 'heuristic', 'conservative', 'aggressive', 'all'],
                       help='Opponent agent type or "all" to compare against all')
    parser.add_argument('--target-score', type=int, default=200, help='Target score to win')
    parser.add_argument('--verbose', action='store_true', default=True, help='Print detailed results')
    
    args = parser.parse_args()
    
    # Create environment
    env = Flip7RLEnv(
        agent_name="QLearningAgent",
        opponent_names=["Opponent1", "Opponent2"],
        target_score=args.target_score,
        agent_index=0
    )
    
    # Create and load agent
    agent = QLearningAgent(name="QLearningAgent")
    
    try:
        agent.load_q_table(args.q_table)
        print(f"Loaded Q-table from {args.q_table}")
        print(f"Q-table size: {len(agent.q_table)} states")
    except FileNotFoundError:
        print(f"Error: Could not load Q-table from {args.q_table}")
        return
    
    # Evaluate
    if args.opponent == 'all':
        results = compare_against_all_baselines(env, agent, args.episodes)
        
        print("\n" + "=" * 60)
        print("Summary Comparison:")
        print("-" * 60)
        for name, metrics in results.items():
            print(f"{name:15s} - Win Rate: {metrics['win_rate']:6.1%} | "
                  f"Avg Score: {metrics['avg_score']:6.1f} | "
                  f"Round Win Rate: {metrics['round_win_rate']:6.1%}")
    else:
        opponent_agent_map = {
            'random': RandomAgent(),
            'heuristic': HeuristicAgent(),
            'conservative': ConservativeAgent(),
            'aggressive': AggressiveAgent()
        }
        opponent_agent = opponent_agent_map[args.opponent]
        env.opponent_agents = [opponent_agent, opponent_agent]
        
        metrics = evaluate_against_opponents(env, agent, args.episodes,
                                            [opponent_agent, opponent_agent])
        
        print("\n" + "=" * 60)
        print("Evaluation Results:")
        print("-" * 60)
        print(f"Opponent: {args.opponent}")
        print(f"Episodes: {metrics['total_episodes']}")
        print(f"Win Rate: {metrics['win_rate']:.1%} ({metrics['wins']}/{metrics['total_episodes']})")
        print(f"Average Score: {metrics['avg_score']:.1f}")
        print(f"Average Opponent Score: {metrics['avg_opponent_score']:.1f}")
        print(f"Round Win Rate: {metrics['round_win_rate']:.1%} ({metrics['round_wins']}/{metrics['total_rounds']})")
        print(f"Average Reward: {metrics['avg_reward']:.2f}")
        print(f"Average Episode Length: {metrics['avg_episode_length']:.1f}")


if __name__ == "__main__":
    main()




