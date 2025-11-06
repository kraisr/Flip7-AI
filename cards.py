"""
Cards module for Flip 7 game.

This module contains the Card and Deck classes used in the Flip 7 card game.
"""

from typing import List, Optional
from dataclasses import dataclass
from enum import Enum
import random


class CardType(Enum):
    """Enumeration of card types in the Flip 7 deck."""
    NUMBER = "number"
    MODIFIER = "modifier"


@dataclass
class Card:
    """
    Represents a single card in the Flip 7 game.
    
    Attributes:
        value: The numeric value of the card (for number cards) or modifier amount (for modifier cards)
        card_type: Whether this is a NUMBER or MODIFIER card
        name: Human-readable name of the card (e.g., "7", "+2", "X2")
    """
    value: int
    card_type: CardType
    name: str
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"Card({self.name}, {self.card_type.value})"


class Deck:
    """
    Represents the deck of cards used in Flip 7.
    
    The deck contains:
    - Number cards: 0-12 (each number appears as many times as its value: 1 card of 0, 1 card of 1, 2 cards of 2, etc.)
    - Modifier cards: +2, +4, +10, X2 (one copy each)
    
    Total: 79 number cards + 4 modifier cards = 83 cards
    
    Deck Management:
    - Cards are drawn and discarded
    - When deck runs out, reshuffle discarded cards (excluding current round)
    - Continue playing with reshuffled deck
    """
    
    def __init__(self):
        """Initialize a new deck with all Flip 7 cards."""
        self.cards: List[Card] = []
        self.discarded_cards: List[Card] = []
        self.current_round_cards: List[Card] = []
        self._create_deck()
        self.shuffle()
    
    def _create_deck(self) -> None:
        """Create the standard Flip 7 deck composition."""
        # Number cards: 0-12, with correct quantities (1 card of value 0, 1 card of value 1, 2 cards of value 2, etc.)
        number_cards = {
            0: 1, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5,  # Each number appears as many times as its value
            6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12   # Higher numbers appear more frequently
        }
        
        for value, count in number_cards.items():
            for _ in range(count):
                self.cards.append(Card(value, CardType.NUMBER, str(value)))
        
        # Modifier cards: one of each type
        modifier_cards = [
            Card(2, CardType.MODIFIER, "+2"),
            Card(4, CardType.MODIFIER, "+4"),
            Card(10, CardType.MODIFIER, "+10"),
            Card(2, CardType.MODIFIER, "X2")
        ]
        
        self.cards.extend(modifier_cards)
    
    def shuffle(self) -> None:
        """Shuffle the deck using Fisher-Yates algorithm."""
        random.shuffle(self.cards)
    
    def draw_card(self) -> Optional[Card]:
        """
        Draw a single card from the top of the deck.
        
        Returns:
            The drawn card, or None if deck is empty
        """
        if not self.cards:
            # Try to reshuffle discarded cards (excluding current round)
            if self.discarded_cards:
                self._reshuffle_discarded()
            else:
                return None
        
        card = self.cards.pop()
        self.current_round_cards.append(card)
        return card
    
    def cards_remaining(self) -> int:
        """Return the number of cards remaining in the deck."""
        return len(self.cards)
    
    def _reshuffle_discarded(self) -> None:
        """Reshuffle discarded cards (excluding current round) back into the deck."""
        if self.discarded_cards:
            self.cards = self.discarded_cards.copy()
            self.discarded_cards.clear()
            self.shuffle()
    
    def end_round(self) -> None:
        """End the current round - move current round cards to discarded pile."""
        self.discarded_cards.extend(self.current_round_cards)
        self.current_round_cards.clear()
    
    def reset_deck(self) -> None:
        """Reset the deck to its original state and shuffle."""
        self.cards.clear()
        self.discarded_cards.clear()
        self.current_round_cards.clear()
        self._create_deck()
        self.shuffle()
