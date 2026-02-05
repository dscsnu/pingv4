from pingv4._core import CellState, ConnectFourBoard
import pingv4
import random

class QuantumShufflePlayer(pingv4.AbstractBot):
    """Bot that uses pseudo-quantum randomness."""

    def __init__(self, player: CellState) -> None:
        super().__init__(player)

    @property
    def strategy_name(self) -> str:
        return "QuantumShuffle"

    @property
    def author_name(self) -> str:
        return "ZX91"

    @property
    def author_netid(self) -> str:
        return "ZX91"

    def get_move(self, board: ConnectFourBoard) -> int:
        valid_moves = board.get_valid_moves()
        return random.choice(valid_moves)
