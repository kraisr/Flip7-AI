"""
Test script demonstrating the Flip 7 game API usage.

This script shows how to use the modular Flip 7 game components programmatically.
"""

from game import Flip7Game
from cards import CardType


def test_game_api():
    """Test the Flip 7 game API with various scenarios."""
    print("=== Flip 7 Game API Test ===\n")
    
    # Create a new game
    game = Flip7Game(["Player1", "Player2", "Player3"], target_score=50)
    print(f"Created game with players: {[p.name for p in game.players]}")
    print(f"Target score: {game.target_score}")
    print(f"Deck has {game.deck.cards_remaining()} cards\n")
    
    # Test game state
    state = game.get_game_state()
    print(f"Initial game state:")
    print(f"  Round: {state['round_number']}")
    print(f"  Round active: {state['round_active']}")
    print(f"  Current player: {state['current_player']}")
    print(f"  Game over: {state['game_over']}\n")
    
    # Play a few turns
    print("Playing some turns...")
    
    # Player 1 hits
    success, message = game.hit()
    print(f"Player 1 hit: {message}")
    
    # Player 2 hits
    success, message = game.hit()
    print(f"Player 2 hit: {message}")
    
    # Player 3 hits
    success, message = game.hit()
    print(f"Player 3 hit: {message}")
    
    # Player 1 hits again
    success, message = game.hit()
    print(f"Player 1 hit: {message}")
    
    # Player 2 stays
    success, message = game.stay()
    print(f"Player 2 stay: {message}")
    
    # Player 3 hits
    success, message = game.hit()
    print(f"Player 3 hit: {message}")
    
    # Player 1 stays
    success, message = game.stay()
    print(f"Player 1 stay: {message}")
    
    # Player 3 stays (round should end)
    success, message = game.stay()
    print(f"Player 3 stay: {message}")
    
    # Show round results
    print(f"\nRound {game.round_number} Results:")
    for player in game.players:
        print(f"  {player.name}: {player.round_score} points (Total: {player.total_score})")
        print(f"    Hand: {[str(card) for card in player.hand]}")
        if player.is_busted:
            print(f"    Status: BUSTED")
        elif player.seven_card_bonus:
            print(f"    Status: SEVEN CARD BONUS!")
    
    # Test bust detection
    print(f"\n=== Testing Bust Detection ===")
    game.start_new_round()
    
    # Force a bust scenario
    current_player = game.get_current_player()
    print(f"Testing bust with {current_player.name}")
    
    # Draw cards until we get a duplicate
    cards_drawn = []
    for i in range(10):  # Safety limit
        success, message = game.hit()
        print(f"  Draw {i+1}: {message}")
        
        if current_player.is_busted:
            print(f"  BUST! {current_player.name} went bust with duplicate cards")
            break
        
        if not game.round_active:
            print(f"  Round ended due to seven-card bonus")
            break
    
    print(f"\nFinal hand: {[str(card) for card in current_player.hand]}")
    print(f"Busted: {current_player.is_busted}")
    print(f"Seven card bonus: {current_player.seven_card_bonus}")
    
    print(f"\n=== API Test Complete ===")


def test_card_creation():
    """Test card creation and deck functionality."""
    print("=== Card and Deck Test ===\n")
    
    from cards import Card, Deck, CardType
    
    # Test card creation
    number_card = Card(7, CardType.NUMBER, "7")
    modifier_card = Card(2, CardType.MODIFIER, "+2")
    
    print(f"Number card: {number_card} (type: {number_card.card_type.value})")
    print(f"Modifier card: {modifier_card} (type: {modifier_card.card_type.value})")
    
    # Test deck
    deck = Deck()
    print(f"\nDeck created with {deck.cards_remaining()} cards")
    
    # Draw some cards
    print("Drawing cards:")
    for i in range(5):
        card = deck.draw_card()
        if card:
            print(f"  Card {i+1}: {card}")
        else:
            print(f"  Card {i+1}: None (deck empty)")
    
    print(f"Cards remaining: {deck.cards_remaining()}")
    
    print(f"\n=== Card Test Complete ===")


def test_player_functionality():
    """Test player functionality."""
    print("=== Player Test ===\n")
    
    from player import Player
    from cards import Card, CardType
    
    player = Player("TestPlayer")
    print(f"Created player: {player}")
    
    # Add some cards
    player.add_card(Card(5, CardType.NUMBER, "5"))
    player.add_card(Card(3, CardType.NUMBER, "3"))
    player.add_card(Card(2, CardType.MODIFIER, "+2"))
    
    print(f"Hand: {[str(card) for card in player.hand]}")
    print(f"Round score: {player.calculate_round_score()}")
    print(f"Is busted: {player.is_busted}")
    
    # Test bust scenario
    player.add_card(Card(5, CardType.NUMBER, "5"))  # Duplicate!
    print(f"After adding duplicate 5:")
    print(f"Is busted: {player.is_busted}")
    print(f"Round score: {player.calculate_round_score()}")
    
    print(f"\n=== Player Test Complete ===")


if __name__ == "__main__":
    test_card_creation()
    print("\n" + "="*50 + "\n")
    
    test_player_functionality()
    print("\n" + "="*50 + "\n")
    
    test_game_api()
