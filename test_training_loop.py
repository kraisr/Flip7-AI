"""
Quick test to verify training loop doesn't hang.
"""

from rl_env import Flip7RLEnv
from q_learning_agent import QLearningAgent
from agents import HeuristicAgent

# Create environment
env = Flip7RLEnv(
    agent_name="TestAgent",
    opponent_names=["Opponent1", "Opponent2"],
    target_score=50,  # Lower target for quick test
    agent_index=0,
    opponent_agents=[HeuristicAgent(), HeuristicAgent()]
)

# Create agent
agent = QLearningAgent(
    name="TestAgent",
    learning_rate=0.1,
    discount_factor=0.95,
    epsilon=1.0
)

print("Testing training loop...")
print("=" * 60)

# Test a single episode
state, info = env.reset()
episode_reward = 0.0
episode_length = 0
done = False
max_steps = 500
step_count = 0

while not done and step_count < max_steps:
    step_count += 1
    
    valid_actions = env.get_valid_actions()
    
    if not valid_actions:
        if env.game.is_game_over():
            done = True
            break
        
        state, reward, done, info = env.step(0)
        episode_reward += reward
        episode_length += 1
        
        if done:
            break
        continue
    
    # Agent's turn
    action = agent.select_action(state, valid_actions, training=True)
    next_state, reward, done, info = env.step(action)
    
    next_valid_actions = env.get_valid_actions() if not done else []
    agent.update_q_value(state, action, reward, next_state, next_valid_actions)
    
    episode_reward += reward
    episode_length += 1
    state = next_state

print(f"Episode completed!")
print(f"  Steps: {step_count}")
print(f"  Episode length: {episode_length}")
print(f"  Reward: {episode_reward:.2f}")
print(f"  Done: {done}")
print(f"  Game over: {env.game.is_game_over()}")
if env.game.is_game_over():
    winner = env.game.get_winner()
    print(f"  Winner: {winner.name if winner else 'None'}")
print("=" * 60)

if step_count >= max_steps:
    print("⚠️  WARNING: Hit step limit - episode may not have completed properly")
else:
    print("✅ Episode completed successfully!")

