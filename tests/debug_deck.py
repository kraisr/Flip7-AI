"""
Debug deck creation issue.
"""

from game.cards import Deck
from collections import Counter


def debug_deck():
    """Debug the deck creation."""
    deck = Deck()
    
    print("All cards in deck:")
    for i, card in enumerate(deck.cards):
        print(f"{i+1:2d}: {card.value} ({card.name})")
    
    print(f"\nTotal cards: {len(deck.cards)}")
    
    # Count by value
    counts = Counter([card.value for card in deck.cards])
    print(f"\nCounts by value:")
    for value in sorted(counts.keys()):
        print(f"  {value}: {counts[value]}")


if __name__ == "__main__":
    debug_deck()
