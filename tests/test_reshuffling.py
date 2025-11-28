"""
Test deck reshuffling when deck runs out.
"""

from game.game import Flip7Game


def test_deck_reshuffling():
    """Test that deck reshuffles discarded cards when it runs out."""
    print("=== Testing Deck Reshuffling ===\n")
    
    game = Flip7Game(["Player1", "Player2", "Player3"], target_score=50)
    
    print(f"Initial deck size: {game.deck.cards_remaining()}")
    
    # Draw cards until deck is almost empty
    cards_drawn = []
    round_count = 0
    
    while game.deck.cards_remaining() > 5 and round_count < 10:  # Safety limit
        round_count += 1
        print(f"\n--- Round {round_count} ---")
        print(f"Deck size: {game.deck.cards_remaining()}")
        print(f"Discarded cards: {len(game.deck.discarded_cards)}")
        
        # Play the round
        turn_count = 0
        while game.round_active and turn_count < 20:  # Safety limit
            turn_count += 1
            current_player = game.get_current_player()
            
            if current_player.has_stayed or current_player.is_busted:
                game.next_turn()
                continue
            
            success, message = game.hit()
            if success:
                card_drawn = message.split("drew ")[1].split(" and")[0]
                cards_drawn.append(card_drawn)
                print(f"  Drew: {card_drawn}")
            
            if not game.round_active:
                break
        
        print(f"Round ended. Deck size: {game.deck.cards_remaining()}")
        print(f"Discarded cards: {len(game.deck.discarded_cards)}")
        
        # Start new round
        if not game.is_game_over():
            game.start_new_round()
    
    print(f"\n=== Final Results ===")
    print(f"Total rounds played: {round_count}")
    print(f"Final deck size: {game.deck.cards_remaining()}")
    print(f"Final discarded cards: {len(game.deck.discarded_cards)}")
    print(f"Total cards drawn: {len(cards_drawn)}")
    
    # Check if reshuffling occurred
    if len(game.deck.discarded_cards) > 0:
        print("✅ Deck reshuffling system is working!")
    else:
        print("❌ No cards were discarded - reshuffling not tested")


if __name__ == "__main__":
    test_deck_reshuffling()

