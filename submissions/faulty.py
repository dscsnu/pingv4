from pingv4 import AbstractBot, CellState, ConnectFourBoard


class Faulty(AbstractBot):
    """Bot that picks moves like drawing a lucky pebble."""

    def __init__(self, player: CellState) -> None:
        super().__init__(player)

    @property
    def strategy_name(self) -> str:
        return "Faulty"

    @property
    def author_name(self) -> str:
        return "Faulty"

    @property
    def author_netid(self) -> str:
        return "Faulty"

    def get_move(self, board: ConnectFourBoard) -> int:
        raise ValueError()
        # return 0
