"""
Test to verify that the deck is never reset during a game.
"""

from game.game import Flip7Game
from collections import Counter


def test_deck_persistence():
    """Test that cards stay out of the deck once drawn."""
    print("=== Testing Deck Persistence ===\n")
    
    # Create a game
    game = Flip7Game(["Player1", "Player2", "Player3"], target_score=50)
    
    print(f"Initial deck size: {game.deck.cards_remaining()}")
    
    # Track cards drawn across rounds
    all_drawn_cards = []
    
    # Play several rounds
    for round_num in range(1, 4):
        print(f"\n--- Round {round_num} ---")
        print(f"Deck size at start: {game.deck.cards_remaining()}")
        
        # Draw some cards in this round
        round_cards = []
        for turn in range(6):  # 2 turns per player
            current_player = game.get_current_player()
            
            if current_player.has_stayed or current_player.is_busted:
                game.next_turn()
                continue
            
            success, message = game.hit()
            if success:
                # Extract the card value from the message
                card_drawn = message.split("drew ")[1].split(" and")[0]
                round_cards.append(card_drawn)
                all_drawn_cards.append(card_drawn)
                print(f"  Drew: {card_drawn}")
            
            if not game.round_active:
                break
        
        print(f"Cards drawn this round: {round_cards}")
        print(f"Deck size at end: {game.deck.cards_remaining()}")
        
        # Check for duplicates in all drawn cards
        card_counts = Counter(all_drawn_cards)
        duplicates = {card: count for card, count in card_counts.items() if count > 1}
        
        if duplicates:
            print(f"⚠️  DUPLICATE CARDS FOUND: {duplicates}")
            print("This should be impossible if deck is not reset!")
        else:
            print("✓ No duplicate cards drawn so far")
        
        # Start new round
        if not game.is_game_over():
            game.start_new_round()
    
    print(f"\n=== Final Results ===")
    print(f"Total cards drawn: {len(all_drawn_cards)}")
    print(f"Final deck size: {game.deck.cards_remaining()}")
    
    # Final duplicate check
    card_counts = Counter(all_drawn_cards)
    duplicates = {card: count for card, count in card_counts.items() if count > 1}
    
    if duplicates:
        print(f"❌ FINAL DUPLICATE CARDS: {duplicates}")
        print("This indicates the deck was reset during the game!")
        return False
    else:
        print("✅ No duplicate cards - deck persistence working correctly!")
        return True


if __name__ == "__main__":
    test_deck_persistence()

