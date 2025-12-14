# Flip 7 Card Game

A Python implementation of the Flip 7 card game with both graphical and command-line interfaces.

## Game Rules

Flip 7 is a card game for exactly 3 players with the following mechanics:

- Each player starts each round with an empty hand
- Players take turns choosing to 'hit' (draw another card) or 'stay' (end their turn)
- If a player draws a card with the same value as already in their hand, they go bust and score zero for the round
- If a player accumulates seven unique number cards, they immediately end the round and receive a 15-point bonus
- Scoring: each number card counts for its face value, modifier cards (+2, +4, +10, X2) increase scores for non-busted hands
- Game continues until one player reaches or exceeds the target score (default: 200 points)

## Installation

No external dependencies required! The game uses only Python standard library modules:
- `tkinter` (for GUI)
- `argparse` (for command-line arguments)
- `random` (for deck shuffling)
- `typing` (for type hints)

## Usage

### GUI Mode (Default)
```bash
python flip7_game.py
# or
python flip7_game.py --mode gui
```

### Command-Line Interface
```bash
python flip7_game.py --mode cli
```

### Example/Demo Mode
```bash
python flip7_game.py --mode example
```

### Direct Module Usage
```python
from game import Flip7Game

# Create a new game
game = Flip7Game(["Alice", "Bob", "Charlie"], target_score=200)

# Play the game
while not game.is_game_over():
    current_player = game.get_current_player()
    
    # Player hits
    success, message = game.hit()
    print(message)
    
    # Or player stays
    success, message = game.stay()
    print(message)
    
    # Check if round ended
    if not game.round_active:
        game.start_new_round()
```

## License

This project is open source and available under the MIT License.
