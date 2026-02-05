from pingv4._core import CellState, ConnectFourBoard
import pingv4
import random

from pingv4._core import CellState, ConnectFourBoard
import random

class DiceRollerAgent(pingv4.AbstractBot):
    """Bot that decides moves by virtual dice roll."""

    def __init__(self, player: CellState) -> None:
        super().__init__(player)

    @property
    def strategy_name(self) -> str:
        return "DiceRoller"

    @property
    def author_name(self) -> str:
        return "N3BULA"

    @property
    def author_netid(self) -> str:
        return "N3BULA"

    def get_move(self, board: ConnectFourBoard) -> int:
        valid_moves = board.get_valid_moves()
        return random.choice(valid_moves)
