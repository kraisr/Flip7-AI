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

Author: AI Assistant
Version: 2.0 (Modular)
"""

import sys
import argparse
import os
from datetime import datetime
from typing import List

# Import the modular components
from game.cards import Card, Deck, CardType
from game.player import Player
from game.game import Flip7Game
from game.gui import Flip7GUI
from game.cli import Flip7CLI


class Tee:
    """Class to duplicate output to both stdout and a log file."""
    def __init__(self, log_file):
        self.log_file = log_file
        self.stdout = sys.stdout
        
    def write(self, text):
        self.stdout.write(text)
        if self.log_file:
            self.log_file.write(text)
            self.log_file.flush()
    
    def flush(self):
        self.stdout.flush()
        if self.log_file:
            self.log_file.flush()


def setup_game_logging():
    """Set up logging to a file in the log folder. Returns the log file handle and path."""
    log_dir = "log"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = os.path.join(log_dir, f"game_{timestamp}.log")
    
    log_file = open(log_file_path, 'w', encoding='utf-8')
    sys.stdout = Tee(log_file)
    
    return log_file, log_file_path


def example_game():
    """
    Example of how to use the Flip 7 game module.
    """
    log_file, _ = setup_game_logging()
    try:
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
    finally:
        sys.stdout = sys.stdout.stdout
        log_file.close()


def main():
    """
    Main entry point for the Flip 7 game.
    
    Supports different interfaces:
    - GUI mode (default)
    - CLI mode
    - Example mode
    """
    parser = argparse.ArgumentParser(description="Flip 7 Card Game")
    parser.add_argument(
        "--mode", 
        choices=["gui", "cli", "example"], 
        default="gui",
        help="Choose the interface mode (default: gui)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "gui":
        log_file, _ = setup_game_logging()
        try:
            print("Starting Flip 7 GUI...")
            app = Flip7GUI(log_file=log_file)
            app.run()
        finally:
            sys.stdout = sys.stdout.stdout
            log_file.close()
    elif args.mode == "cli":
        log_file, _ = setup_game_logging()
        try:
            print("Starting Flip 7 CLI...")
            cli = Flip7CLI()
            cli.run()
        finally:
            sys.stdout = sys.stdout.stdout
            log_file.close()
    elif args.mode == "example":
        example_game()


if __name__ == "__main__":
    main()

