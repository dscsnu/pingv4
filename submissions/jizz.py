from pingv4._core import CellState, ConnectFourBoard
import pingv4
import random

class LuckyPebbleBot(pingv4.AbstractBot):
    """Bot that picks moves like drawing a lucky pebble."""

    def __init__(self, player: CellState) -> None:
        super().__init__(player)

    @property
    def strategy_name(self) -> str:
        return "LuckyPebble"

    @property
    def author_name(self) -> str:
        return "KRAKEN"

    @property
    def author_netid(self) -> str:
        return "KRAKEN"

    def get_move(self, board: ConnectFourBoard) -> int:
        valid_moves = board.get_valid_moves()
        return random.choice(valid_moves)
