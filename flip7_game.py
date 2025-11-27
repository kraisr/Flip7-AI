"""
Flip 7 Card Game - Main Module

This is the main entry point for the Flip 7 card game. It provides access to both
the modular game components and different interfaces (GUI and CLI).

The game is now organized into separate modules:
- cards.py: Card and Deck classes
- player.py: Player class
- game.py: Flip7Game class
- gui.py: Graphical user interface
- cli.py: Command-line interface

Author: Us
Version: 2.0 (Modular)
"""

import sys
import argparse
from typing import List

# Import the modular components
from cards import Card, Deck, CardType
from player import Player
from game import Flip7Game
from gui import Flip7GUI
from cli import Flip7CLI


def example_game():
    """
    Example of how to use the Flip 7 game module.
    """
    print("=== Flip 7 Game Example ===\n")
    
    # Create a new game
    game = Flip7Game(["Alice", "Bob", "Charlie"], target_score=100)
    
    print(f"Starting game with players: {[p.name for p in game.players]}")
    print(f"Target score: {game.target_score}")
    print(f"Deck has {game.deck.cards_remaining()} cards\n")
    
    # Simulate a few turns
    round_count = 0
    while not game.is_game_over() and round_count < 3:
        round_count += 1
        print(f"--- Round {game.round_number} ---")
        
        # Play the round until it ends
        turn_count = 0
        while game.round_active and turn_count < 20:  # Safety limit
            turn_count += 1
            current_player = game.get_current_player()
            
            # Skip if player has already ended their turn
            if current_player.has_stayed or current_player.is_busted:
                game.next_turn()
                continue
            
            print(f"\nTurn {turn_count}: {current_player.name}'s turn")
            
            # Show current hand
            if current_player.hand:
                print(f"Current hand: {[str(card) for card in current_player.hand]}")
            
            # Decide to hit or stay (simple strategy: hit if hand value < 15)
            hand_value = sum(card.value for card in current_player.hand if card.card_type == CardType.NUMBER)
            
            if hand_value < 15 and not current_player.has_stayed:
                success, message = game.hit()
                print(f"Action: Hit - {message}")
            else:
                success, message = game.stay()
                print(f"Action: Stay - {message}")
            
            if not success:
                print(f"Action failed: {message}")
            
            # Check if round ended
            if not game.round_active:
                print(f"\nRound {game.round_number} ended!")
                break
        
        # Show round results
        if not game.round_active:
            print("\nRound Results:")
            for player in game.players:
                print(f"{player.name}: {player.round_score} points (Total: {player.total_score})")
            
            if not game.is_game_over():
                print("\nStarting new round...")
                game.start_new_round()
    
    # Show final results
    if game.is_game_over():
        print(f"\n🎉 Game Over! {game.get_winner().name} wins with {game.get_winner().total_score} points!")
    else:
        print("\nGame simulation ended early for demonstration purposes.")


def rl_training_mode():
    """Run RL training mode."""
    from train import main as train_main
    train_main()


def rl_play_mode():
    """Run RL agent play mode (watch trained agent play)."""
    import argparse
    from rl_env import Flip7RLEnv
    from q_learning_agent import QLearningAgent
    from agents import HeuristicAgent
    
    parser = argparse.ArgumentParser(description="Watch trained RL agent play")
    parser.add_argument('--q-table', type=str, default='q_table.pkl', 
                       help='Path to Q-table file')
    parser.add_argument('--episodes', type=int, default=1, 
                       help='Number of games to watch')
    parser.add_argument('--target-score', type=int, default=200, 
                       help='Target score to win')
    
    args = parser.parse_args()
    
    # Create environment
    env = Flip7RLEnv(
        agent_name="QLearningAgent",
        opponent_names=["Opponent1", "Opponent2"],
        target_score=args.target_score,
        agent_index=0,
        opponent_agents=[HeuristicAgent(), HeuristicAgent()]
    )
    
    # Load trained agent
    agent = QLearningAgent(name="QLearningAgent")
    try:
        agent.load_q_table(args.q_table)
        print(f"Loaded Q-table from {args.q_table}")
    except FileNotFoundError:
        print(f"Error: Could not load Q-table from {args.q_table}")
        print("Please train an agent first using: python train.py")
        return
    
    agent.set_epsilon(0.0)  # No exploration during play
    
    print(f"Watching trained agent play {args.episodes} game(s)...")
    print("=" * 60)
    
    for episode in range(args.episodes):
        state, info = env.reset()
        done = False
        turn_count = 0
        
        print(f"\n--- Game {episode + 1} ---")
        
        while not done:
            valid_actions = env.get_valid_actions()
            
            if not valid_actions:
                # Wait for agent's turn
                state, _, done, _ = env.step(0)
                continue
            
            # Agent's turn
            current_player = env.game.get_current_player()
            action = 0  # Default action
            if current_player.name == env.agent_name:
                turn_count += 1
                print(f"\nTurn {turn_count}: {current_player.name}'s turn")
                print(f"Hand: {[str(card) for card in current_player.hand]}")
                print(f"Hand value: {sum(card.value for card in current_player.hand if card.card_type == CardType.NUMBER)}")
                
                action = agent.select_action(state, valid_actions, training=False)
                action_name = "HIT" if action == 0 else "STAY"
                print(f"Action: {action_name}")
            
            state, reward, done, info = env.step(action)
            
            if info.get('round_ended'):
                print(f"\nRound {env.game.round_number} ended!")
                for player in env.game.players:
                    print(f"  {player.name}: {player.round_score} points (Total: {player.total_score})")
        
        # Game over
        winner = env.game.get_winner()
        print(f"\n{'='*60}")
        if winner:
            print(f"Winner: {winner.name} with {winner.total_score} points!")
        print("=" * 60)


def main():
    """
    Main entry point for the Flip 7 game.
    
    Supports different interfaces:
    - GUI mode (default)
    - CLI mode
    - Example mode
    - RL training mode
    - RL play mode
    """
    parser = argparse.ArgumentParser(description="Flip 7 Card Game")
    parser.add_argument(
        "--mode", 
        choices=["gui", "cli", "example", "rl", "rl-play"], 
        default="gui",
        help="Choose the interface mode (default: gui)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "gui":
        print("Starting Flip 7 GUI...")
        app = Flip7GUI()
        app.run()
    elif args.mode == "cli":
        print("Starting Flip 7 CLI...")
        cli = Flip7CLI()
        cli.run()
    elif args.mode == "example":
        example_game()
    elif args.mode == "rl":
        rl_training_mode()
    elif args.mode == "rl-play":
        rl_play_mode()


if __name__ == "__main__":
    main()

