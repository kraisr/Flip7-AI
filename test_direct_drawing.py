"""
Direct test to see what cards are actually being drawn.
"""

from game import Flip7Game


def test_direct_card_drawing():
    """Test card drawing directly."""
    print("=== Direct Card Drawing Test ===\n")
    
    game = Flip7Game(["Player1", "Player2", "Player3"], target_score=50)
    
    print(f"Initial deck size: {game.deck.cards_remaining()}")
    
    # Draw cards directly and track them
    drawn_cards = []
    
    for i in range(20):
        card = game.deck.draw_card()
        if card is None:
            print("Deck exhausted!")
            break
        
        drawn_cards.append(card)
        print(f"Card {i+1}: {card.value} ({card.name})")
        
        if len(drawn_cards) > 1:
            # Check for duplicates
            values = [c.value for c in drawn_cards]
            if len(values) != len(set(values)):
                print(f"  ⚠️  DUPLICATE VALUE FOUND!")
                break
    
    print(f"\nTotal cards drawn: {len(drawn_cards)}")
    print(f"Remaining deck size: {game.deck.cards_remaining()}")
    
    # Check for duplicates
    values = [c.value for c in drawn_cards]
    unique_values = set(values)
    
    if len(values) == len(unique_values):
        print("✅ No duplicate values drawn")
    else:
        print("❌ Duplicate values found!")
        from collections import Counter
        counts = Counter(values)
        duplicates = {v: c for v, c in counts.items() if c > 1}
        print(f"Duplicates: {duplicates}")


if __name__ == "__main__":
    test_direct_card_drawing()

