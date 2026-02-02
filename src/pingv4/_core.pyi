from typing import List, Tuple, Optional
from enum import IntEnum

class CellState(IntEnum):
    """
    Enumeration representing the state of a cell on a Connect Four board.

    Each value corresponds to the player occupying a cell.

    :cvar Yellow: Indicates a cell occupied by the yellow player.
    :cvar Red: Indicates a cell occupied by the red player.
    """

    Yellow = 0
    Red = 1

class ConnectFourBoard:
    def __init__(self) -> None:
        """
        Initializes an empty Connect Four Board.
        """
        ...

    @property
    def num_rows(self) -> int:
        """
        :return: The total number of rows.
        :rtype: int
        """
        ...

    @property
    def num_cols(self) -> int:
        """
        :return: The total number of columns.
        :rtype: int
        """
        ...

    @property
    def hash(self) -> int:
        """
        Return a hash representing the current board state.

        The hash depends only on the configuration of pieces on the board
        and is deterministic for a given state.

        :return: A hash value for the current board state.
        :rtype: int
        """
        ...

    @property
    def column_heights(self) -> List[int]:
        """
        Return the current heights of all columns.

        Each element represents the number of pieces currently placed
        in the corresponding column.

        :return: A list of column heights indexed by column.
        :rtype: List[int]
        """
        ...

    @property
    def is_in_progress(self) -> bool:
        """
        Check if the game is still in progress.

        :return: True if the game is in progress (no victory or draw), False otherwise.
        :rtype: bool
        """
        ...

    @property
    def current_player(self) -> Optional[CellState]:
        """
        Get the current player whose turn it is.

        :return: The current player if game is in progress, None otherwise.
        :rtype: Optional[CellState]
        """
        ...

    @property
    def is_victory(self) -> bool:
        """
        Check if the game has ended in a victory.

        :return: True if a player has won, False otherwise.
        :rtype: bool
        """
        ...

    @property
    def winner(self) -> Optional[CellState]:
        """
        Get the winning player.

        :return: The winning player if there is a victory, None otherwise.
        :rtype: Optional[CellState]
        """
        ...

    @property
    def is_draw(self) -> bool:
        """
        Check if the game has ended in a draw.

        :return: True if the board is full with no winner, False otherwise.
        :rtype: bool
        """
        ...

    @property
    def cell_states(self) -> List[List[Optional[CellState]]]:
        """
        Return the state of all cells on the board.

        .. warning::
            Cell states are stored in **column-major** order. Access as
            ``cell_states[col_idx][row_idx]`` where ``col_idx`` is the column
            index (0-6) and ``row_idx`` is the row index (0-5, bottom to top).

        :return: A nested list of cell states indexed by [column][row].
        :rtype: List[List[Optional[CellState]]]
        """
        ...

    def get_valid_moves(self) -> List[int]:
        """
        Return all moves that can be made given the current game state.

        Returns empty list if game is in draw/victory state.

        :return: A list of column indexes that are valid moves
        :rtype: List[int]
        """
        ...

    def make_move(self, col_idx: int) -> "ConnectFourBoard":
        """
        Make a move in the specified column.

        Returns a new board with the move applied. The current board
        remains unchanged (immutable).

        :param col_idx: The zero-indexed column to drop the piece into.
        :type col_idx: int
        :return: A new board with the move applied.
        :rtype: ConnectFourBoard
        :raises ValueError: If column index is out of bounds, column is full,
            or game is not in progress (victory/draw).
        """
        ...

    def __getitem__(self, idx: Tuple[int, int]) -> Optional[CellState]:
        """
        Return the state of a specific cell on the board.

        .. warning::
            Access is **column-major**: the first index is the column, the second
            is the row. Use ``board[col_idx, row_idx]`` where ``col_idx`` is the
            column (0-6) and ``row_idx`` is the row (0-5, bottom to top).

        :param idx: A zero-indexed ``(col_idx, row_idx)`` tuple identifying the cell.
        :type idx: Tuple[int, int]
        :return: The cell state if occupied, or None if the cell is empty.
        :rtype: Optional[CellState]
        """
        ...

    def __hash__(self) -> int:
        """
        Return the hash value of the board.

        Enables the board to be used in hash-based collections.

        :return: The hash value of the board.
        :rtype: int
        """
        ...

    def __eq__(self, other: object) -> bool:
        """
        Compare this board with another object for equality.

        Boards are equal if they are the same type and have identical
        piece configurations.

        :param other: The object to compare against.
        :return: True if equal, False otherwise.
        :rtype: bool
        """
        ...

    def __str__(self) -> str:
        """
        :return: The string representation of the board
        :rtype: str
        """
        ...
