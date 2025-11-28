# Flip 7 Card Game

A complete Python implementation of the Flip 7 card game with both graphical and command-line interfaces.

## Game Rules

Flip 7 is a card game for exactly 3 players with the following mechanics:

- Each player starts each round with an empty hand
- Players take turns choosing to 'hit' (draw another card) or 'stay' (end their turn)
- If a player draws a card with the same value as already in their hand, they go bust and score zero for the round
- If a player accumulates seven unique number cards, they immediately end the round and receive a 15-point bonus
- Scoring: each number card counts for its face value, modifier cards (+2, +4, +10, X2) increase scores for non-busted hands
- Game continues until one player reaches or exceeds the target score (default: 200 points)

## Modular Structure

The game is organized into separate modules for better maintainability:

- **`cards.py`**: Contains `Card` and `Deck` classes
- **`player.py`**: Contains the `Player` class
- **`game.py`**: Contains the main `Flip7Game` class
- **`gui.py`**: Graphical user interface using tkinter
- **`cli.py`**: Command-line interface
- **`flip7_game.py`**: Main entry point that ties everything together

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

## Features

### Core Game Engine
- Complete rule implementation
- Deck shuffling and card management
- Bust detection and seven-card bonus
- Round and game progression
- Score calculation with modifiers

### GUI Interface
- Modern tkinter-based interface
- Real-time game state display
- Visual player hand display
- Game controls (Hit, Stay, New Round)
- Status messages and game information
- Game setup dialog

### Command-Line Interface
- Interactive text-based gameplay
- Clear turn-by-turn display
- Round results summary
- Game state management

### API Features
- Clean, well-documented classes and methods
- Type hints throughout
- Comprehensive error handling
- Game state serialization
- Modular design for easy extension

## File Structure

```
flip7_game/
├── flip7_game.py    # Main entry point
├── cards.py         # Card and Deck classes
├── player.py        # Player class
├── game.py          # Main game logic
├── gui.py           # Graphical interface
├── cli.py           # Command-line interface
└── README.md        # This file
```

## Example Game Flow

1. **Setup**: Create game with 3 players and target score
2. **Round Start**: All players start with empty hands
3. **Turns**: Players alternate hitting or staying
4. **Bust Detection**: Duplicate number cards cause bust
5. **Seven-Card Bonus**: Seven unique numbers end round with bonus
6. **Round End**: Calculate scores and check for winner
7. **New Round**: Reset and continue until target score reached

## Extending the Game

The modular design makes it easy to extend:

- **AI Players**: Add decision-making logic to the `Player` class
- **New Card Types**: Extend the `Card` class and deck creation
- **Different Interfaces**: Create new interface modules
- **Game Variants**: Modify rules in the `Flip7Game` class
- **Statistics**: Add tracking and analysis features

## License

This project is open source and available under the MIT License.
>>>>>>> diya-main
