"""
Player module for Flip 7 game.

This module contains the Player class used in the Flip 7 card game.
"""

from typing import List
from game.cards import Card, CardType


class Player:
    """
    Represents a player in the Flip 7 game.
    
    Each player maintains their hand, tracks their score, and manages game state.
    """
    
    def __init__(self, name: str):
        """
        Initialize a new player.
        
        Args:
            name: The player's name
        """
        self.name = name
        self.hand: List[Card] = []
        self.total_score: int = 0
        self.round_score: int = 0
        self.is_busted: bool = False
        self.has_stayed: bool = False
        self.seven_card_bonus: bool = False
    
    def add_card(self, card: Card) -> None:
        """
        Add a card to the player's hand.
        
        Args:
            card: The card to add to the hand
        """
        self.hand.append(card)
        self._check_bust()
        self._check_seven_card_bonus()
    
    def _check_bust(self) -> None:
        """Check if the player has gone bust (duplicate number cards)."""
        number_cards = [card for card in self.hand if card.card_type == CardType.NUMBER]
        values = [card.value for card in number_cards]
        
        # Check for duplicate values
        if len(values) != len(set(values)):
            self.is_busted = True
    
    def _check_seven_card_bonus(self) -> None:
        """Check if the player has seven unique number cards."""
        number_cards = [card for card in self.hand if card.card_type == CardType.NUMBER]
        unique_values = set(card.value for card in number_cards)
        
        if len(unique_values) == 7:
            self.seven_card_bonus = True
            self.has_stayed = True  # Automatically end turn
    
    def calculate_round_score(self) -> int:
        """
        Calculate the player's score for the current round.
        
        Returns:
            The calculated round score (0 if busted)
        """
        if self.is_busted:
            return 0
        
        # Base score from number cards
        number_cards = [card for card in self.hand if card.card_type == CardType.NUMBER]
        base_score = sum(card.value for card in number_cards)
        
        # Apply modifier cards
        modifier_cards = [card for card in self.hand if card.card_type == CardType.MODIFIER]
        modified_score = base_score
        
        for modifier in modifier_cards:
            if modifier.name.startswith('+'):
                modified_score += modifier.value
            elif modifier.name == 'X2':
                modified_score *= 2
        
        # Add seven-card bonus
        if self.seven_card_bonus:
            modified_score += 15
        
        return modified_score
    
    def stay(self) -> None:
        """End the player's turn and bank their current cards."""
        self.has_stayed = True
    
    def reset_for_new_round(self) -> None:
        """Reset player state for a new round."""
        self.hand.clear()
        self.round_score = 0
        self.is_busted = False
        self.has_stayed = False
        self.seven_card_bonus = False
    
    def __str__(self) -> str:
        return f"{self.name} (Score: {self.total_score})"
    
    def __repr__(self) -> str:
        return f"Player({self.name}, {self.total_score})"
