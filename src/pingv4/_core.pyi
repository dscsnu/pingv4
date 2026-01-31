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

    def __getitem__(self, idx: Tuple[int, int]) -> Optional[CellState]:
        """
        Return the state of a specific cell on the board.

        :param idx: A zero-indexed (row, column) tuple identifying the cell.
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
