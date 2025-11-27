"""
Test script to run a single game with a trained AI agent.
Shows detailed play-by-play output.
"""

import sys
from rl_env import Flip7RLEnv
from q_learning_agent import QLearningAgent
from agents import RandomAgent, ConservativeAgent, HeuristicAgent
from cards import CardType

def print_hand(player):
    """Print player's hand in a readable format."""
    number_cards = [card for card in player.hand if card.card_type == CardType.NUMBER]
    modifier_cards = [card for card in player.hand if card.card_type == CardType.MODIFIER]
    hand_value = sum(card.value for card in number_cards)
    
    hand_str = f"[{', '.join(str(card) for card in number_cards)}]"
    if modifier_cards:
        hand_str += f" + Modifiers: [{', '.join(str(card) for card in modifier_cards)}]"
    
    return hand_str, hand_value

def run_ai_game(q_table_path="q_table_curriculum.pkl", opponent_type="heuristic"):
    """
    Run a single game with the trained AI agent.
    
    Args:
        q_table_path: Path to the trained Q-table file
        opponent_type: Type of opponents ("random", "conservative", or "heuristic")
    """
    print("=" * 70)
    print("FLIP 7 - AI AGENT GAME")
    print("=" * 70)
    print(f"Loading Q-table from: {q_table_path}")
    print(f"Opponent type: {opponent_type}")
    print("=" * 70)
    print()
    
    # Create opponent agents based on type
    if opponent_type == "random":
        opponent_agents = [RandomAgent(), RandomAgent()]
    elif opponent_type == "conservative":
        opponent_agents = [ConservativeAgent(), ConservativeAgent()]
    else:  # heuristic
        opponent_agents = [HeuristicAgent(), HeuristicAgent()]
    
    # Create environment
    env = Flip7RLEnv(
        agent_name="AI_Agent",
        opponent_names=["Opponent1", "Opponent2"],
        target_score=200,
        agent_index=0,
        opponent_agents=opponent_agents
    )
    
    # Create and load trained agent
    agent = QLearningAgent()
    try:
        agent.load_q_table(q_table_path)
        print(f"[OK] Loaded Q-table with {len(agent.q_table)} states")
    except FileNotFoundError:
        print(f"[WARNING] Q-table file '{q_table_path}' not found. Using untrained agent.")
    except Exception as e:
        print(f"[ERROR] Error loading Q-table: {e}. Using untrained agent.")
    
    # Set agent to greedy (no exploration)
    agent.epsilon = 0.0
    
    # Reset environment
    state, info = env.reset()
    print(f"\nStarting game! Target score: {env.target_score}")
    print(f"Players: {[p.name for p in env.game.players]}")
    print()
    
    step_count = 0
    max_steps = 500
    done = False
    round_number = 1
    
    while not done and step_count < max_steps:
        step_count += 1
        
        # Get current game state
        current_player = env.game.get_current_player()
        valid_actions = env.get_valid_actions()
        
        # Skip if no valid actions (opponent's turn will be handled by step)
        if not valid_actions:
            state, reward, done, info = env.step(0)
            continue
        
        # It's the agent's turn
        if current_player.name == env.agent_name:
            # Print round header if new round
            if env.game.round_number > round_number:
                round_number = env.game.round_number
                print("\n" + "=" * 70)
                print(f"ROUND {round_number}")
                print("=" * 70)
            
            # Show agent's hand
            hand_str, hand_value = print_hand(current_player)
            print(f"\n[AI Agent's Turn]")
            print(f"Hand: {hand_str}")
            print(f"Hand value: {hand_value}")
            print(f"Total score: {current_player.total_score}")
            
            # Get Q-values for debugging
            q_hit = agent.get_q_value(state, 0)
            q_stay = agent.get_q_value(state, 1)
            
            # Check if state exists in Q-table
            state_in_table = state in agent.q_table
            if state_in_table:
                actual_q_hit = agent.q_table[state].get(0, agent.optimistic_init_value)
                actual_q_stay = agent.q_table[state].get(1, agent.optimistic_init_value)
                print(f"Q-values: HIT={q_hit:.3f}, STAY={q_stay:.3f} (State in Q-table: {state_in_table})")
                if actual_q_hit != q_hit or actual_q_stay != q_stay:
                    print(f"  -> Actual Q-table values: HIT={actual_q_hit:.3f}, STAY={actual_q_stay:.3f}")
            else:
                print(f"Q-values: HIT={q_hit:.3f}, STAY={q_stay:.3f} (NEW STATE - using optimistic init)")
            
            # Select action (greedy - always uses best Q-value)
            action = agent.select_action(state, valid_actions, training=False)
            action_name = "HIT" if action == 0 else "STAY"
            print(f"Action: {action_name} (Selected based on Q-values: {'HIT' if q_hit > q_stay else 'STAY' if q_stay > q_hit else 'TIE'})")
            
            # Take action
            next_state, reward, done, info = env.step(action)
            
            # Show result
            if current_player.is_busted:
                print("  -> BUSTED!")
            elif current_player.seven_card_bonus:
                print("  -> SEVEN CARD BONUS!")
            elif action == 1:  # Stay
                print("  -> Stayed")
            
            print(f"Reward: {reward:.2f}")
            
            state = next_state
            
            # Check if round ended
            if info.get('round_ended'):
                print("\n" + "-" * 70)
                print("ROUND RESULTS:")
                for player in env.game.players:
                    status = ""
                    if player.is_busted:
                        status = " (BUSTED)"
                    elif player.seven_card_bonus:
                        status = " (SEVEN CARD BONUS!)"
                    print(f"  {player.name}: {player.round_score} points{status} (Total: {player.total_score})")
                print("-" * 70)
        
        else:
            # Opponent's turn - show what they're doing
            opp_hand_str, opp_hand_value = print_hand(current_player)
            print(f"\n[{current_player.name}'s Turn]")
            print(f"Hand: {opp_hand_str}")
            print(f"Hand value: {opp_hand_value}")
            print(f"Total score: {current_player.total_score}")
            print(f"(Opponent uses their own strategy, not RL agent's Q-table)")
            
            state, reward, done, info = env.step(0)
        
        if done:
            break
    
    # Game over
    print("\n" + "=" * 70)
    print("GAME OVER!")
    print("=" * 70)
    
    if env.game.is_game_over():
        winner = env.game.get_winner()
        if winner:
            print(f"\n[WINNER] {winner.name} with {winner.total_score} points!")
        else:
            print("\nNo winner determined.")
    else:
        print(f"\nGame stopped after {step_count} steps (hit limit)")
    
    print("\nFinal Scores:")
    for player in env.game.players:
        print(f"  {player.name}: {player.total_score} points")
    
    print("\n" + "=" * 70)
    print(f"Total steps: {step_count}")
    print("=" * 70)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run a single game with trained AI agent")
    parser.add_argument("--q-table", type=str, default="q_table_curriculum.pkl",
                       help="Path to Q-table file (default: q_table_curriculum.pkl)")
    parser.add_argument("--opponent", type=str, default="heuristic",
                       choices=["random", "conservative", "heuristic"],
                       help="Type of opponents (default: heuristic)")
    
    args = parser.parse_args()
    
    run_ai_game(args.q_table, args.opponent)

