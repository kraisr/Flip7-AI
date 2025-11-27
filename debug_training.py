"""
Debug script to see why rounds aren't ending.
"""

from rl_env import Flip7RLEnv
from q_learning_agent import QLearningAgent
from agents import HeuristicAgent

# Create environment
env = Flip7RLEnv(
    agent_name="TestAgent",
    opponent_names=["Opponent1", "Opponent2"],
    target_score=50,
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

print("=== DEBUGGING TRAINING LOOP ===\n")

state, info = env.reset()
print(f"Initial state: Round {env.game.round_number}, Active: {env.game.round_active}")
print(f"Players: {[p.name for p in env.game.players]}")
print(f"Current player: {env.game.get_current_player().name}\n")

step_count = 0
max_steps = 200

while step_count < max_steps:
    step_count += 1
    
    valid_actions = env.get_valid_actions()
    current_player = env.game.get_current_player()
    agent_player = env.game.players[env.agent_index]
    
    if step_count <= 20 or step_count % 10 == 0:  # Print first 20 steps, then every 10th
        print(f"Step {step_count}:")
        print(f"  Current player: {current_player.name}")
        print(f"  Agent ({agent_player.name}): stayed={agent_player.has_stayed}, busted={agent_player.is_busted}")
        print(f"  Valid actions: {valid_actions}")
        print(f"  Round active: {env.game.round_active}")
        print(f"  All players ended: {all(p.has_stayed or p.is_busted for p in env.game.players)}")
        print(f"  Scores: {[(p.name, p.total_score, p.round_score) for p in env.game.players]}")
    
    if not valid_actions:
        if step_count <= 20 or step_count % 10 == 0:
            print("  -> No valid actions, calling step(0)...")
        state, reward, done, info = env.step(0)
        if step_count <= 20 or step_count % 10 == 0:
            print(f"  -> Result: reward={reward}, done={done}, round_active={env.game.round_active}")
        if done:
            break
        if step_count <= 20 or step_count % 10 == 0:
            print()
        continue
    
    # Agent's turn
    action = agent.select_action(state, valid_actions, training=True)
    if step_count <= 20 or step_count % 10 == 0:
        print(f"  -> Agent action: {action} ({'HIT' if action == 0 else 'STAY'})")
    
    next_state, reward, done, info = env.step(action)
    if step_count <= 20 or step_count % 10 == 0:
        print(f"  -> Result: reward={reward}, done={done}, round_active={env.game.round_active}")
        print(f"  -> Agent score: {agent_player.total_score}, Round score: {agent_player.round_score}")
    
    if done:
        break
    
    state = next_state
    if step_count <= 20 or step_count % 10 == 0:
        print()

print(f"\n=== FINAL STATE ===")
print(f"Steps: {step_count}")
print(f"Round: {env.game.round_number}")
print(f"Round active: {env.game.round_active}")
print(f"Game over: {env.game.is_game_over()}")
for p in env.game.players:
    print(f"  {p.name}: total={p.total_score}, round={p.round_score}, stayed={p.has_stayed}, busted={p.is_busted}")

