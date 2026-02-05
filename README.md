# pingv4

A high-performance Connect Four library with a graphical game interface and bot framework.

## Installation

```bash
pip install pingv4
```
> *Note: Python 3.9+ required*

## Quick Start

### Play a Game

```python
from pingv4 import Connect4Game, MinimaxBot

# Human vs Human
game = Connect4Game()
game.run()

# Human vs Bot
game = Connect4Game(player1=None, player2=MinimaxBot)
game.run()

# Bot vs Bot
game = Connect4Game(player1=MinimaxBot, player2=MinimaxBot)
game.run()
```

### Use the Board Directly

```python
from pingv4 import ConnectFourBoard, CellState

board = ConnectFourBoard()

# Make moves (returns a new board - immutable!)
board = board.make_move(3)  # Red plays center
board = board.make_move(3)  # Yellow plays center
board = board.make_move(2)  # Red plays left of center

# Check game state
print(board.is_in_progress)  # True
print(board.current_player)  # CellState.Yellow
print(board.get_valid_moves())  # [0, 1, 2, 3, 4, 5, 6]

# Access cells (column-major: board[col, row])
print(board[3, 0])  # CellState.Red
print(board[3, 1])  # CellState.Yellow

# Print the board
print(board)
```

---

## API Reference

### `CellState`

An enum representing the state of a cell.

```python
from pingv4 import CellState

CellState.Red     # Red player (plays first)
CellState.Yellow  # Yellow player
```

---

### `ConnectFourBoard`

The core game board class. **Immutable** - all operations return new board instances.

#### Creating a Board

```python
board = ConnectFourBoard()  # Creates an empty 6x7 board
```

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `num_rows` | `int` | Number of rows (6) |
| `num_cols` | `int` | Number of columns (7) |
| `current_player` | `CellState \| None` | Current player, or `None` if game over |
| `is_in_progress` | `bool` | `True` if game is still ongoing |
| `is_victory` | `bool` | `True` if a player has won |
| `is_draw` | `bool` | `True` if the board is full with no winner |
| `winner` | `CellState \| None` | The winning player, or `None` |
| `column_heights` | `list[int]` | Number of pieces in each column |
| `hash` | `int` | Deterministic hash for the board state |
| `cell_states` | `list[list[CellState \| None]]` | All cells (column-major) |

#### Methods

```python
# Get valid moves (columns that aren't full)
moves: list[int] = board.get_valid_moves()

# Make a move (returns NEW board)
new_board = board.make_move(col_idx)  # col_idx: 0-6

# Access a cell (column-major!)
cell = board[col, row]  # col: 0-6, row: 0-5 (bottom to top)
```

> ⚠️ **Column-Major Access**: Board indexing is `board[column, row]`, not `board[row, column]`.

#### Example: Game Loop

```python
from pingv4 import ConnectFourBoard

board = ConnectFourBoard()

while board.is_in_progress:
    move = int(input(f"{board.current_player}'s turn. Column (0-6): "))
    if move in board.get_valid_moves():
        board = board.make_move(move)
    print(board)

if board.is_victory:
    print(f"{board.winner} wins!")
else:
    print("It's a draw!")
```

---

### `Connect4Game`

A pygame-based graphical game interface.

```python
from pingv4 import Connect4Game, GameConfig, MinimaxBot

# Basic usage
game = Connect4Game(
    player1=None,        # Human player
    player2=MinimaxBot,  # Bot class
    config=GameConfig()  # Optional configuration
)
game.run()
```

#### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `player1` | `PlayerConfig` | `None` | First player (see below) |
| `player2` | `PlayerConfig` | `None` | Second player |
| `config` | `GameConfig` | `GameConfig()` | Game settings |

**`PlayerConfig`** can be:
- `None` — Human player (manual input)
- Bot class (e.g., `MinimaxBot`, `RandomBot`) — Will be instantiated automatically

#### Controls

| Key | Action |
|-----|--------|
| Click | Place piece (human turn) |
| `R` | Restart game |
| `ESC` | Quit |

---

### `GameConfig`

Frozen Pydantic model for game configuration.

```python
from pingv4 import GameConfig

config = GameConfig(
    bot_delay_seconds=0.5,      # Delay before bot moves (default: 1.0)
    animation_speed=35,          # Piece falling speed (default: 25)
    window_width=700,            # Window width in pixels
    window_height=700,           # Window height in pixels
    cell_size=80,                # Size of each cell
    background_color=(30, 30, 40),
    board_color=(0, 80, 180),
    red_color=(220, 50, 50),
    yellow_color=(240, 220, 50),
)
```

---

## Creating Custom Bots

Extend `AbstractBot` to create your own Connect Four AI:

```python
from pingv4 import AbstractBot, ConnectFourBoard, CellState

class MyBot(AbstractBot):
    @property
    def strategy_name(self) -> str:
        return "My Custom Bot"
    
    @property
    def author_name(self) -> str:
        return "Your Name"
    
    @property
    def author_netid(self) -> str:
        return "your_id"
    
    def get_move(self, board: ConnectFourBoard) -> int:
        """Return a column index (0-6) for your move."""
        valid_moves = board.get_valid_moves()
        
        # Your strategy here!
        # Example: prefer center columns
        for col in [3, 2, 4, 1, 5, 0, 6]:
            if col in valid_moves:
                return col
        
        return valid_moves[0]
```

### Using Your Bot

```python
from pingv4 import Connect4Game

game = Connect4Game(player1=MyBot, player2=None)
game.run()
```

### Bot Interface

Your bot receives a `ConnectFourBoard` and must return a valid column index.

```python
def get_move(self, board: ConnectFourBoard) -> int:
    # Useful properties:
    board.current_player      # Your color (CellState.Red or CellState.Yellow)
    board.get_valid_moves()   # List of valid columns
    board.column_heights      # How full each column is
    board.hash                # For transposition tables
    
    # Simulate moves:
    future = board.make_move(col)  # Returns new board
    
    # Check outcomes:
    future.is_victory  # Did someone win?
    future.winner      # Who won?
    
    return column_index  # 0-6
```

---

## Built-in Bots

### `RandomBot`

Plays random valid moves. Useful for testing.

```python
from pingv4 import RandomBot
```

### `MinimaxBot`

Strong AI using minimax with alpha-beta pruning.

```python
from pingv4 import MinimaxBot

# Default depth is 6
game = Connect4Game(player1=MinimaxBot, player2=MinimaxBot)
```

Features:
- Alpha-beta pruning
- Transposition tables (using `board.hash`)
- Center-preference move ordering
- Positional evaluation

---

## Tips for Bot Development

### Use the Hash for Caching

The `board.hash` property is highly optimized. Use it for transposition tables:

```python
cache = {}

def evaluate(board):
    if board.hash in cache:
        return cache[board.hash]
    
    score = expensive_calculation(board)
    cache[board.hash] = score
    return score
```

### Board is Immutable

`make_move()` returns a new board. The original is unchanged:

```python
board1 = ConnectFourBoard()
board2 = board1.make_move(3)

board1[3, 0]  # None (unchanged)
board2[3, 0]  # CellState.Red
```

### Column-Major Access

Remember: it's `board[column, row]`, not `board[row, column]`.

```python
# Check if column 3 has a red piece at the bottom
if board[3, 0] == CellState.Red:
    ...
```