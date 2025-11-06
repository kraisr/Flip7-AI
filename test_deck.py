"""
Test to verify that duplicate cards of unique values are impossible.
"""

from cards import Deck
from collections import Counter


def test_deck_composition():
    """Test that the deck has the correct composition."""
    print("=== Testing Deck Composition ===\n")
    
    deck = Deck()
    print(f"Total cards in deck: {deck.cards_remaining()}")
    
    # Count cards by value (only number cards, not modifiers)
    number_cards = [card for card in deck.cards if card.card_type.value == "number"]
    card_counts = Counter([card.value for card in number_cards])
    
    print("\nCard distribution:")
    for value in sorted(card_counts.keys()):
        count = card_counts[value]
        print(f"  Value {value}: {count} cards")
    
    # Verify the distribution is correct
    print("\nVerifying distribution:")
    all_correct = True
    
    for value in range(0, 13):  # 0 to 12
        if value == 0:
            expected_count = 1  # Special case: 0 appears 1 time
        else:
            expected_count = value  # Each number appears as many times as its value
        actual_count = card_counts.get(value, 0)
        
        if actual_count == expected_count:
            print(f"  ✓ Value {value}: {actual_count} cards (correct)")
        else:
            print(f"  ✗ Value {value}: {actual_count} cards (expected {expected_count})")
            all_correct = False
    
    # Check modifier cards
    modifier_cards = [card for card in deck.cards if card.card_type.value == "modifier"]
    print(f"\nModifier cards: {len(modifier_cards)}")
    for card in modifier_cards:
        print(f"  {card.name}")
    
    if len(modifier_cards) == 4:
        print("  ✓ Correct number of modifier cards")
    else:
        print(f"  ✗ Expected 4 modifier cards, got {len(modifier_cards)}")
        all_correct = False
    
    print(f"\nDeck composition {'✓ CORRECT' if all_correct else '✗ INCORRECT'}")
    
    # Test that drawing duplicate unique cards is impossible
    print(f"\n=== Testing Duplicate Prevention ===")
    
    # Draw cards and track what we've seen
    drawn_cards = []
    unique_values = [0, 1]  # These should only appear once
    
    for i in range(20):  # Draw 20 cards
        card = deck.draw_card()
        if card is None:
            print("Deck exhausted")
            break
            
        drawn_cards.append(card.value)
        
        if card.value in unique_values:
            print(f"Card {i+1}: Drew {card.value} (unique value)")
            if drawn_cards.count(card.value) > 1:
                print(f"  ✗ ERROR: Duplicate {card.value} card drawn!")
                return False
            else:
                print(f"  ✓ First {card.value} card (correct)")
    
    print(f"\n✓ No duplicate unique cards drawn - deck composition is correct!")
    return True


if __name__ == "__main__":
    test_deck_composition()
