"""
Command-line interface for Flip 7 game.

This module provides a simple command-line interface for playing Flip 7.
"""

from typing import List
from game.game import Flip7Game


class Flip7CLI:
    """
    Command-line interface for Flip 7 card game.
    
    Provides a simple text-based interface for playing the game.
    """
    
    def __init__(self):
        """Initialize the CLI."""
        self.game: Flip7Game = None
    
    def start_game(self):
        """Start a new game."""
        print("=== Flip 7 Card Game ===\n")
        
        # Get player names
        player_names = []
        for i in range(3):
            while True:
                name = input(f"Enter name for Player {i+1}: ").strip()
                if name and name not in player_names:
                    player_names.append(name)
                    break
                elif name in player_names:
                    print("Name already taken! Please choose a different name.")
                else:
                    print("Please enter a valid name.")
        
        # Get target score
        while True:
            try:
                target_score = int(input("Enter target score (default 200): ") or "200")
                if target_score > 0:
                    break
                else:
                    print("Target score must be positive!")
            except ValueError:
                print("Please enter a valid number!")
        
        # Create game
        self.game = Flip7Game(player_names, target_score)
        print(f"\nGame started! Target score: {target_score}")
        print(f"Deck has {self.game.deck.cards_remaining()} cards\n")
        
        # Start playing
        self.play_game()
    
    def play_game(self):
        """Main game loop."""
        while not self.game.is_game_over():
            print(f"--- Round {self.game.round_number} ---")
            
            # Play round
            self.play_round()
            
            # Show round results
            self.show_round_results()
            
            # Check if game is over
            if self.game.is_game_over():
                break
            
            # Automatically start new round (or ask user)
            print("\nRound completed! Starting next round...")
            self.game.start_new_round()
        
        # Show final results
        if self.game.is_game_over():
            winner = self.game.get_winner()
            print(f"\n🎉 GAME OVER! {winner.name} wins with {winner.total_score} points!")
        else:
            print("\nGame ended.")
    
    def play_round(self):
        """Play a single round."""
        while self.game.round_active:
            current_player = self.game.get_current_player()
            
            # Skip if player has already ended their turn
            if current_player.has_stayed or current_player.is_busted:
                # The game logic should handle this automatically now
                continue
            
            print(f"\n{current_player.name}'s turn")
            print(f"Current hand: {[str(card) for card in current_player.hand]}")
            
            # Get player action
            while True:
                action = input("Hit (h) or Stay (s)? ").lower().strip()
                if action in ['h', 'hit']:
                    success, message = self.game.hit()
                    print(f"Action: Hit - {message}")
                    break
                elif action in ['s', 'stay']:
                    success, message = self.game.stay()
                    print(f"Action: Stay - {message}")
                    break
                else:
                    print("Please enter 'h' for hit or 's' for stay")
    
    def show_round_results(self):
        """Show the results of the current round."""
        print(f"\nRound {self.game.round_number} Results:")
        print("-" * 30)
        
        for player in self.game.players:
            status = ""
            if player.is_busted:
                status = " (BUSTED)"
            elif player.seven_card_bonus:
                status = " (SEVEN CARD BONUS!)"
            
            print(f"{player.name}: {player.round_score} points{status} (Total: {player.total_score})")
    
    def run(self):
        """Run the CLI application."""
        try:
            self.start_game()
        except KeyboardInterrupt:
            print("\n\nGame interrupted. Goodbye!")
        except Exception as e:
            print(f"\nAn error occurred: {e}")


def main():
    """Main function to run the Flip 7 CLI."""
    cli = Flip7CLI()
    cli.run()


if __name__ == "__main__":
    main()
