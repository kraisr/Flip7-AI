"""
Test the corrected deck management system.
"""

from game import Flip7Game


def test_corrected_deck_management():
    """Test that deck management works correctly with reshuffling."""
    print("=== Testing Corrected Deck Management ===\n")
    
    game = Flip7Game(["Player1", "Player2", "Player3"], target_score=50)
    
    print(f"Initial deck size: {game.deck.cards_remaining()}")
    print(f"Discarded cards: {len(game.deck.discarded_cards)}")
    print(f"Current round cards: {len(game.deck.current_round_cards)}")
    
    # Play a few rounds to test deck management
    for round_num in range(1, 4):
        print(f"\n--- Round {round_num} ---")
        print(f"Deck size at start: {game.deck.cards_remaining()}")
        print(f"Discarded cards: {len(game.deck.discarded_cards)}")
        
        # Draw some cards
        cards_drawn_this_round = []
        for turn in range(6):  # 2 turns per player
            current_player = game.get_current_player()
            
            if current_player.has_stayed or current_player.is_busted:
                game.next_turn()
                continue
            
            success, message = game.hit()
            if success:
                # Extract card from message
                card_drawn = message.split("drew ")[1].split(" and")[0]
                cards_drawn_this_round.append(card_drawn)
                print(f"  Drew: {card_drawn}")
            
            if not game.round_active:
                break
        
        print(f"Cards drawn this round: {cards_drawn_this_round}")
        print(f"Deck size at end: {game.deck.cards_remaining()}")
        print(f"Current round cards: {len(game.deck.current_round_cards)}")
        
        # Start new round
        if not game.is_game_over():
            game.start_new_round()
            print(f"After round end - Discarded cards: {len(game.deck.discarded_cards)}")
            print(f"Current round cards: {len(game.deck.current_round_cards)}")
    
    print(f"\n=== Final State ===")
    print(f"Deck size: {game.deck.cards_remaining()}")
    print(f"Discarded cards: {len(game.deck.discarded_cards)}")
    print(f"Current round cards: {len(game.deck.current_round_cards)}")


if __name__ == "__main__":
    test_corrected_deck_management()

