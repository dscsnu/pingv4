from pingv4 import (
    AbstractBot,
    ConnectFourBoard,
    CellState,
    Connect4Game,
    GameConfig,
    MinimaxBot,
)


class ys617(AbstractBot):
    @property
    def strategy_name(self) -> str:
        return "My Custom Bot"

    @property
    def author_name(self) -> str:
        return "Yashas Sharma"

    @property
    def author_netid(self) -> str:
        return "ys617"

    def get_move(self, board: ConnectFourBoard) -> int:
        """Return a column index (0-6) for your move."""
        valid_moves = board.get_valid_moves()
        ch = board.column_heights
        for col in [0, 1, 2, 3, 4, 3, 2, 1, 0]:
            if ch[col] == 0:
                if col in valid_moves:
                    return col

            elif ch[col] == 0:
                if col == 1:
                    if col in valid_moves:
                        return col

            elif ch[col] == 1:
                if col == 2:
                    if col in valid_moves:
                        return col

            elif ch[col] == 2:
                if col == 3:
                    if col in valid_moves:
                        return col

        return valid_moves[0]
