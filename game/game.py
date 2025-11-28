"""
Game module for Flip 7.

This module contains the main Flip7Game class that manages the game state and logic.
"""

from typing import List, Dict, Optional, Tuple
from game.cards import Deck
from game.player import Player


class Flip7Game:
    """
    Main game controller for Flip 7.
    
    Manages game state, turn order, round progression, and scoring.
    """
    
    def __init__(self, player_names: List[str], target_score: int = 200):
        """
        Initialize a new Flip 7 game.
        
        Args:
            player_names: List of exactly 3 player names
            target_score: Score needed to win the game (default: 200)
        
        Raises:
            ValueError: If not exactly 3 players are provided
        """
        if len(player_names) != 3:
            raise ValueError("Flip 7 requires exactly 3 players")
        
        self.players = [Player(name) for name in player_names]
        self.deck = Deck()
        self.target_score = target_score
        self.current_player_index = 0
        self.round_number = 1
        self.game_over = False
        self.winner: Optional[Player] = None
        self.round_active = True
    
    def get_current_player(self) -> Player:
        """Get the player whose turn it currently is."""
        return self.players[self.current_player_index]
    
    def next_turn(self) -> None:
        """Advance to the next player's turn."""
        self.current_player_index = (self.current_player_index + 1) % 3
    
    def hit(self) -> Tuple[bool, str]:
        """
        Current player draws a card.
        
        Returns:
            Tuple of (success, message) indicating the result
        """
        if not self.round_active:
            return False, "Round is not active"
        
        current_player = self.get_current_player()
        
        if current_player.has_stayed or current_player.is_busted:
            return False, f"{current_player.name} has already ended their turn"
        
        card = self.deck.draw_card()
        if card is None:
            return False, "Deck is empty"
        
        current_player.add_card(card)
        
        # Check if player went bust or got seven-card bonus
        if current_player.is_busted:
            message = f"{current_player.name} drew {card} and went bust!"
            self.next_turn()
            # Check if all players are now busted or have ended their turns
            self._check_round_end_conditions()
            return True, message
        
        if current_player.seven_card_bonus:
            message = f"{current_player.name} drew {card} and got seven unique cards! Round ends."
            self._end_round()
            return True, message
        
        message = f"{current_player.name} drew {card}"
        self.next_turn()
        # Check if all players are now busted or have ended their turns
        self._check_round_end_conditions()
        return True, message
    
    def stay(self) -> Tuple[bool, str]:
        """
        Current player ends their turn.
        
        Returns:
            Tuple of (success, message) indicating the result
        """
        if not self.round_active:
            return False, "Round is not active"
        
        current_player = self.get_current_player()
        
        if current_player.has_stayed or current_player.is_busted:
            return False, f"{current_player.name} has already ended their turn"
        
        current_player.stay()
        message = f"{current_player.name} stayed"
        
        # Check if all players have ended their turns
        self._check_round_end_conditions()
        
        return True, message
    
    def _check_round_end_conditions(self) -> None:
        """
        Check if the round should end based on current game state.
        
        Round ends when:
        1. All players have stayed or are busted
        2. A player got seven unique cards (handled in hit method)
        """
        if all(p.has_stayed or p.is_busted for p in self.players):
            self._end_round()
        else:
            # Keep moving to next player until we find one who can play
            self._advance_to_next_active_player()
    
    def _advance_to_next_active_player(self) -> None:
        """
        Advance to the next player who can still play (not busted and hasn't stayed).
        If all players have ended their turns, this will be handled by _check_round_end_conditions.
        """
        # Keep advancing until we find a player who can play
        attempts = 0
        while attempts < 3:  # Safety limit to prevent infinite loops
            current_player = self.get_current_player()
            if not current_player.has_stayed and not current_player.is_busted:
                # Found an active player
                break
            self.next_turn()
            attempts += 1
    
    def _end_round(self) -> None:
        """End the current round and calculate scores."""
        self.round_active = False
        
        # Calculate round scores
        for player in self.players:
            player.round_score = player.calculate_round_score()
            player.total_score += player.round_score
        
        # End the round for the deck (move current round cards to discarded)
        self.deck.end_round()
        
        # Check for game winner
        for player in self.players:
            if player.total_score >= self.target_score:
                self.game_over = True
                self.winner = player
                break
    
    def start_new_round(self) -> None:
        """Start a new round, resetting all players."""
        if self.game_over:
            return
        
        self.round_number += 1
        self.round_active = True
        self.current_player_index = 0
        
        # Reset all players
        for player in self.players:
            player.reset_for_new_round()
        
        # Note: Deck is NEVER reset in Flip 7 - cards stay out once drawn
    
    def get_game_state(self) -> Dict:
        """
        Get the current state of the game.
        
        Returns:
            Dictionary containing game state information
        """
        return {
            'round_number': self.round_number,
            'round_active': self.round_active,
            'current_player': self.get_current_player().name,
            'players': [
                {
                    'name': p.name,
                    'hand': [str(card) for card in p.hand],
                    'round_score': p.round_score,
                    'total_score': p.total_score,
                    'is_busted': p.is_busted,
                    'has_stayed': p.has_stayed,
                    'seven_card_bonus': p.seven_card_bonus
                }
                for p in self.players
            ],
            'deck_cards_remaining': self.deck.cards_remaining(),
            'game_over': self.game_over,
            'winner': self.winner.name if self.winner else None,
            'target_score': self.target_score
        }
    
    def is_game_over(self) -> bool:
        """Check if the game has ended."""
        return self.game_over
    
    def get_winner(self) -> Optional[Player]:
        """Get the winning player, if any."""
        return self.winner
