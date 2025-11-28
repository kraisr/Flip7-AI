"""
AI module for Flip 7.

This module implements a per-turn decision-making AI for the Flip 7 card game.
The AI uses a recursive, memoized expected-value calculation to decide whether
the current player should HIT (draw a card) or STAY (bank their current hand).

Assumptions:
- Only two card types exist: NUMBER and MODIFIER.
- Modifier cards are: "+2", "+4", "+10", "X2".
- Seven unique NUMBER cards immediately end the turn with a +15 bonus.
- A player goes bust if they ever draw a NUMBER card with a value they already have.
- The deck contains:
    * NUMBER cards with values 0..12, where value v appears v times (0 and 1 appear once).
    * One copy of each modifier card.

The AI works *per turn* and does NOT try to reason about multi-player race-to-200
strategy. It simply maximizes the expected score of the current turn from the
current game state (player's hand + remaining deck).
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List, Tuple

from cards import CardType, Card, Deck
from game import Flip7Game
from player import Player


@dataclass
class TurnState:
    numbers_mask: int  # bit i set if number i is present (0 <= i <= 12)
    a: int             # multiplicative factor from X2 modifiers (1 or 2)
    b: int             # additive offset from +2/+4/+10 and the effect of X2 on them


class OptimalTurnAI:
    """
    Expected-value based AI for a single Flip 7 turn.
    
    Usage:
        ai = OptimalTurnAI()
        action = ai.choose_action(game)
        if action == "hit":
            game.hit()
        else:
            game.stay()
    """
    
    # Order of modifier names for bitmasking (index = bit position)
    MODIFIER_ORDER: Tuple[str, ...] = ("+2", "+4", "+10", "X2")
    
    def choose_action(self, game: Flip7Game) -> str:
        """
        Decide whether the current player should 'hit' or 'stay'.
        
        Args:
            game: The Flip7Game instance
        
        Returns:
            "hit" or "stay"
        """
        if not game.round_active:
            return "stay"
        
        current_player = game.get_current_player()
        
        # If player already finished or busted, nothing to do
        if current_player.has_stayed or current_player.is_busted:
            return "stay"
        
        # If there are no cards left to draw, we must stay
        if game.deck.cards_remaining() == 0:
            return "stay"
        
        # Build probability weights from the current deck
        num_weights, mod_weights = self._build_deck_weights(game.deck)
        
        # If deck somehow has no drawable cards, stay
        total_weight = sum(num_weights) + sum(mod_weights.values())
        if total_weight <= 0:
            return "stay"
        
        # Build the current per-turn state from the player's hand
        turn_state = self._build_turn_state_from_player(current_player)
        
        # Build initial modifier-availability bitmask (1 bit per modifier name)
        mods_mask = 0
        for idx, name in enumerate(self.MODIFIER_ORDER):
            if mod_weights.get(name, 0.0) > 0:
                mods_mask |= (1 << idx)
        
        # Precompute base sum lookup for all possible number sets (0..12)
        base_sum_lookup = self._precompute_base_sum_lookup()
        
        # Cache card weights in local variables for the nested DP
        num_w = tuple(float(w) for w in num_weights)  # ensure hashable
        # Only keep modifiers that exist in the deck
        mod_w = {name: float(mod_weights.get(name, 0.0)) for name in self.MODIFIER_ORDER}
        
        # Small optimization: if ALL weights are zero (shouldn't happen), just stay
        if sum(num_w) + sum(mod_w.values()) == 0.0:
            return "stay"
        
        # Nested DP + memoization
        @lru_cache(maxsize=None)
        def score_from_state(numbers_mask: int, a: int, b: int) -> float:
            """Compute score if we stop now in this scoring configuration."""
            base_sum = base_sum_lookup[numbers_mask]
            score = a * base_sum + b
            # Seven unique numbers grant +15 bonus automatically
            if _popcount(numbers_mask) >= 7:
                score += 15
            return float(score)
        
        @lru_cache(maxsize=None)
        def V(numbers_mask: int, mods_mask_local: int, a: int, b: int) -> float:
            """
            Value function: maximum expected score achievable from this state
            when playing optimally (choosing between hit and stay).
            """
            bank_value = score_from_state(numbers_mask, a, b)
            hit_value = Q_hit(numbers_mask, mods_mask_local, a, b)
            return bank_value if bank_value >= hit_value else hit_value
        
        @lru_cache(maxsize=None)
        def Q_hit(numbers_mask: int, mods_mask_local: int, a: int, b: int) -> float:
            """
            Expected final score if we choose to HIT once from this state
            and then act optimally thereafter.
            """
            # Compute normalizing constant Z for allowed cards
            Z = 0.0
            # All number cards that exist in the deck are considered possible
            for w in num_w:
                Z += w
            # Only modifiers that still remain on this hypothetical path are allowed
            for idx, name in enumerate(self.MODIFIER_ORDER):
                if mods_mask_local & (1 << idx):
                    Z += mod_w.get(name, 0.0)
            
            # No cards effectively available (e.g., zero-weight deck) -> cannot hit
            if Z <= 0.0:
                return score_from_state(numbers_mask, a, b)
            
            ev = 0.0
            
            # Number cards 0..12
            for value, weight in enumerate(num_w):
                if weight <= 0.0:
                    continue
                p = weight / Z
                if p == 0.0:
                    continue
                
                if numbers_mask & (1 << value):
                    # Drawing a duplicate number: immediate bust
                    outcome = 0.0
                else:
                    new_mask = numbers_mask | (1 << value)
                    # If this is the 7th unique number, auto-end with bonus
                    if _popcount(new_mask) >= 7:
                        outcome = score_from_state(new_mask, a, b)
                    else:
                        outcome = V(new_mask, mods_mask_local, a, b)
                ev += p * outcome
            
            # Modifier cards
            for idx, name in enumerate(self.MODIFIER_ORDER):
                base_weight = mod_w.get(name, 0.0)
                if base_weight <= 0.0:
                    continue
                if not (mods_mask_local & (1 << idx)):
                    # This modifier has already been "used" along this hypothetical path
                    continue
                
                p = base_weight / Z
                if p == 0.0:
                    continue
                
                # Apply modifier effect to (a, b)
                if name.startswith("+"):
                    # Additive modifier: f(x) = a*x + (b + value)
                    try:
                        delta = int(name[1:])
                    except ValueError:
                        # Fallback: use 0 if parsing fails (defensive)
                        delta = 0
                    new_a = a
                    new_b = b + delta
                elif name.startswith("X") or name.startswith("x"):
                    # Multiplicative modifier: f(x) = (a*x + b) * value
                    try:
                        mul = int(name[1:])
                    except ValueError:
                        mul = 2
                    new_a = a * mul
                    new_b = b * mul
                else:
                    # Unknown modifier type; ignore effect (safe fallback)
                    new_a = a
                    new_b = b
                
                # This modifier cannot be drawn again along this path
                new_mods_mask = mods_mask_local & ~(1 << idx)
                
                outcome = V(numbers_mask, new_mods_mask, new_a, new_b)
                ev += p * outcome
            
            return ev
        
        # Initial arguments for the DP
        start_mask = turn_state.numbers_mask
        start_a = turn_state.a
        start_b = turn_state.b
        start_mods_mask = mods_mask
        
        current_score = score_from_state(start_mask, start_a, start_b)
        expected_if_hit = Q_hit(start_mask, start_mods_mask, start_a, start_b)
        
        # Decision rule: hit only if expected value of hitting exceeds banking
        if expected_if_hit > current_score:
            return "hit"
        else:
            return "stay"
    
    # --------------------------------------------------------------------- #
    # Helper methods                                                        #
    # --------------------------------------------------------------------- #
    
    def _build_deck_weights(self, deck: Deck) -> Tuple[List[float], Dict[str, float]]:
        """
        Build simple frequency-based weights for each possible card draw from the deck.
        
        Args:
            deck: The current Deck instance
        
        Returns:
            (num_weights, mod_weights)
            
            num_weights: list of length 13, index = number value (0..12)
            mod_weights: mapping from modifier name (e.g., "+2") to count
        """
        num_weights: List[float] = [0.0] * 13  # 0..12
        mod_weights: Dict[str, float] = {}
        
        for card in deck.cards:
            if card.card_type == CardType.NUMBER:
                value = card.value
                if 0 <= value < len(num_weights):
                    num_weights[value] += 1.0
            elif card.card_type == CardType.MODIFIER:
                mod_weights[card.name] = mod_weights.get(card.name, 0.0) + 1.0
        
        return num_weights, mod_weights
    
    def _build_turn_state_from_player(self, player: Player) -> TurnState:
        """
        Construct a TurnState from the current player's hand.
        
        This reproduces the exact scoring semantics from Player.calculate_round_score,
        but in parametric form (numbers_mask, a, b).
        """
        numbers_mask = 0
        number_cards: List[Card] = []
        modifier_cards: List[Card] = []
        
        # Split cards into numbers and modifiers, preserving hand order
        for card in player.hand:
            if card.card_type == CardType.NUMBER:
                number_cards.append(card)
                # Set bit for this value
                if 0 <= card.value <= 12:
                    numbers_mask |= (1 << card.value)
            elif card.card_type == CardType.MODIFIER:
                modifier_cards.append(card)
        
        # Base sum from number cards
        base_sum = sum(card.value for card in number_cards)
        
        # Reconstruct (a, b) so that the final score equals
        # what Player.calculate_round_score() would produce.
        # Start with f(x) = x (i.e., a = 1, b = 0).
        a = 1
        b = 0
        
        for modifier in modifier_cards:
            name = modifier.name
            if name.startswith("+"):
                try:
                    delta = int(name[1:])
                except ValueError:
                    delta = modifier.value
                # f(x) -> f(x) + delta => a*x + (b + delta)
                b += delta
            elif name.startswith("X") or name.startswith("x"):
                try:
                    mul = int(name[1:])
                except ValueError:
                    mul = modifier.value if modifier.value > 0 else 2
                # f(x) -> f(x) * mul => (a*mul)*x + (b*mul)
                a *= mul
                b *= mul
            else:
                # Unknown modifier type; ignore effect
                pass
        
        return TurnState(numbers_mask=numbers_mask, a=a, b=b)
    
    def _precompute_base_sum_lookup(self) -> List[int]:
        """
        Precompute base_sum for every possible numbers_mask (0..2^13 - 1).
        
        base_sum_lookup[mask] = sum of all indices i for which bit i in mask is set.
        """
        max_mask = 1 << 13  # 0..12 inclusive
        lookup = [0] * max_mask
        for mask in range(max_mask):
            s = 0
            v = 0
            m = mask
            while m:
                if m & 1:
                    s += v
                v += 1
                m >>= 1
            lookup[mask] = s
        return lookup


def _popcount(x: int) -> int:
    """
    C++ style wrapper for count # of bits set to 1
    """
    return x.bit_count()
