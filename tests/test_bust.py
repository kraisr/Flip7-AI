"""
Test script to verify bust handling and round progression.
"""

from game import Flip7Game
from cards import CardType


def test_bust_scenario():
    """Test the specific scenario where players get busted."""
    print("=== Testing Bust Scenario ===\n")
    
    # Create a game
    game = Flip7Game(["Player1", "Player2", "Player3"], target_score=50)
    
    print(f"Starting game with players: {[p.name for p in game.players]}")
    print(f"Round: {game.round_number}, Active: {game.round_active}")
    print(f"Current player: {game.get_current_player().name}\n")
    
    # Simulate some turns to get players in different states
    print("Playing turns...")
    
    # Player 1 hits
    success, message = game.hit()
    print(f"Player 1 hit: {message}")
    print(f"Current player: {game.get_current_player().name}")
    
    # Player 2 hits  
    success, message = game.hit()
    print(f"Player 2 hit: {message}")
    print(f"Current player: {game.get_current_player().name}")
    
    # Player 3 hits
    success, message = game.hit()
    print(f"Player 3 hit: {message}")
    print(f"Current player: {game.get_current_player().name}")
    
    # Player 1 hits again
    success, message = game.hit()
    print(f"Player 1 hit: {message}")
    print(f"Current player: {game.get_current_player().name}")
    
    # Player 2 hits again (might go bust)
    success, message = game.hit()
    print(f"Player 2 hit: {message}")
    print(f"Current player: {game.get_current_player().name}")
    print(f"Player 2 busted: {game.players[1].is_busted}")
    
    # Player 3 hits again (might go bust)
    success, message = game.hit()
    print(f"Player 3 hit: {message}")
    print(f"Current player: {game.get_current_player().name}")
    print(f"Player 3 busted: {game.players[2].is_busted}")
    
    # Check game state
    print(f"\nGame state:")
    print(f"Round active: {game.round_active}")
    print(f"Current player: {game.get_current_player().name}")
    print(f"Current player can play: {not game.get_current_player().has_stayed and not game.get_current_player().is_busted}")
    
    for i, player in enumerate(game.players):
        print(f"Player {i+1} ({player.name}): busted={player.is_busted}, stayed={player.has_stayed}")
    
    # Try to continue playing
    if game.round_active:
        print(f"\nContinuing with {game.get_current_player().name}...")
        success, message = game.hit()
        print(f"Action: {message}")
        print(f"Round active: {game.round_active}")
    
    print(f"\n=== Test Complete ===")


if __name__ == "__main__":
    test_bust_scenario()
