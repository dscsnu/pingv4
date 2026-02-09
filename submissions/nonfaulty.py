from pingv4 import AbstractBot, CellState, ConnectFourBoard
import random


class nonfaulty(AbstractBot):
    """Bot that picks moves like drawing a lucky pebble."""

    def __init__(self, player: CellState) -> None:
        super().__init__(player)

    @property
    def strategy_name(self) -> str:
        return "Random"

    @property
    def author_name(self) -> str:
        return "Random"

    @property
    def author_netid(self) -> str:
        return "Random"

    def get_move(self, board: ConnectFourBoard) -> int:
        valid_moves = board.get_valid_moves()
        return random.choice(valid_moves)
