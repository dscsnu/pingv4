from pingv4 import AbstractBot, ConnectFourBoard

class Ra830(AbstractBot):

    def __init__(self, player):
        super().__init__(player)
        self.prev_board = None

    @property
    def strategy_name(self) -> str:
        return "Copy Opponent Column"

    @property
    def author_name(self) -> str:
        return "Your Name"

    @property
    def author_netid(self) -> str:
        return "Your NetID"

    def get_move(self, board: ConnectFourBoard) -> int:
        valid_moves = board.get_valid_moves()

        user_col = None

        if self.prev_board is not None:
            for col in range(7):
                if board.get_column_height(col) > self.prev_board.get_column_height(col):
                    user_col = col
                    break

        self.prev_board = board.copy()

        if user_col is not None and user_col in valid_moves:
            return user_col

        return valid_moves[0]