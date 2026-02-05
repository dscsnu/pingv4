from pingv4._core import CellState, ConnectFourBoard
import pingv4
import random

class ChaosMonkeyBot(pingv4.AbstractBot):
    """Bot that selects moves using chaotic randomness."""

    def __init__(self, player: CellState) -> None:
        super().__init__(player)

    @property
    def strategy_name(self) -> str:
        return "ChaosMonkey"

    @property
    def author_name(self) -> str:
        return "A7XQ"

    @property
    def author_netid(self) -> str:
        return "A7XQ"

    def get_move(self, board: ConnectFourBoard) -> int:
        valid_moves = board.get_valid_moves()
        return random.choice(valid_moves)
