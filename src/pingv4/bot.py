from abc import ABC, abstractmethod
from typing import Final

from pingv4._core import CellState, ConnectFourBoard


class AbstractBot(ABC):
    """
    Abstract base class for all ConnectFour bots
    """

    def __init__(self, player: CellState) -> None:
        """
        :param player: The CellState (Red or Yellow) this bot is playing as
        :type player: CellState
        """
        self.player: Final[CellState] = player

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """
        Human-readable name of the bot's strategy.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def author_name(self) -> str:
        """
        Full name of the bot's author.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def author_netid(self) -> str:
        """
        NetID (or equivalent identifier) of the bot's author.
        """
        raise NotImplementedError

    @abstractmethod
    def get_move(self, board: ConnectFourBoard) -> int:
        """
        Decide which column to place your next coin in

        :param board: The current ConnectFour Board state
        :type board: ConnectFourBoard
        :return: A valid column index (0 <= i <= 6)
        :rtype: int
        """
        raise NotImplementedError
