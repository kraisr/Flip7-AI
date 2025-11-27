"""
Debug script to test training loop and identify where it gets stuck.
"""

from rl_env import Flip7RLEnv
from q_learning_agent import QLearningAgent
from agents import HeuristicAgent

# Create environment
env = Flip7RLEnv(
    agent_name="QLearningAgent",
    opponent_names=["Opponent1", "Opponent2"],
    target_score=200,
    agent_index=0,
    opponent_agents=[HeuristicAgent(), HeuristicAgent()]
)

# Create agent
agent = QLearningAgent()

print("Testing single episode...")
print("=" * 60)

# Reset
state, info = env.reset()
print(f"Initial state: round={env.game.round_number}, active={env.game.round_active}")
print(f"Current player: {env.game.get_current_player().name}")
print(f"Valid actions: {env.get_valid_actions()}")
print()

step_count = 0
max_steps = 100
done = False

while not done and step_count < max_steps:
    step_count += 1
    
    valid_actions = env.get_valid_actions()
    current_player = env.game.get_current_player()
    
    print(f"Step {step_count}:")
    print(f"  Current player: {current_player.name}")
    print(f"  Valid actions: {valid_actions}")
    print(f"  Round: {env.game.round_number}, Active: {env.game.round_active}")
    print(f"  Game over: {env.game.is_game_over()}")
    
    if not valid_actions:
        print("  -> No valid actions, stepping with dummy action")
        state, reward, done, info = env.step(0)
        print(f"  -> After step: done={done}, reward={reward}")
    else:
        print("  -> Agent's turn, selecting action")
        action = agent.select_action(state, valid_actions, training=True)
        print(f"  -> Selected action: {action}")
        state, reward, done, info = env.step(action)
        print(f"  -> After step: done={done}, reward={reward}")
    
    print()
    
    if done:
        print(f"Episode finished after {step_count} steps!")
        print(f"Winner: {info.get('winner', 'None')}")
        break

if step_count >= max_steps:
    print(f"Hit step limit ({max_steps}) - episode didn't finish!")
    print(f"Final state: round={env.game.round_number}, active={env.game.round_active}")
    print(f"Game over: {env.game.is_game_over()}")
    print(f"Current player: {env.game.get_current_player().name}")
    
    # Check player states
    print("\nPlayer states:")
    for i, player in enumerate(env.game.players):
        print(f"  {player.name}: busted={player.is_busted}, stayed={player.has_stayed}, "
              f"score={player.total_score}")

