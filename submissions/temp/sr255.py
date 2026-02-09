from pingv4 import AbstractBot, ConnectFourBoard
from pingv4._core import CellState


class sr255(AbstractBot):
    def __init__(self, player=None):
        super().__init__(player)

    @property
    def strategy_name(self):
        return "Competitive Defensive Bot (Minimax, Fork-Safe)"

    @property
    def author_name(self):
        return "sr255"

    @property
    def author_netid(self):
        return "sr255"

    def get_move(self, board: ConnectFourBoard) -> int:
        my = board.current_player
        opp = self._opponent(my)
        moves = board.get_valid_moves()
        center = len(board.column_heights) // 2
        # 1. Win if possible
        for col in moves:
            if self._is_win(board, col, my):
                return col
        # 2. Block opponent win
        for col in moves:
            if self._is_win(board, col, opp):
                return col
        # 3. Prefer center
        if center in moves:
            return center
        # 4. Minimax fallback
        return max(
            moves,
            key=lambda c: self.minimax(board.make_move(c), 6, False, my),
        )

    def _is_win(self, board, col, color):
        try:
            return board.make_move(col).winner == color
        except Exception:
            return False

    def minimax(self, board, depth, maximizing, my):
        opp = self._opponent(my)
        moves = board.get_valid_moves()
        if depth == 0 or board.winner or not moves:
            return self._eval(board, my, opp)
        scores = [
            self.minimax(board.make_move(c), depth - 1, not maximizing, my)
            for c in moves
        ]
        return max(scores) if maximizing else min(scores)

    def _eval(self, board, my, opp):
        if board.winner == my:
            return 10000
        if board.winner == opp:
            return -10000
        score = 0
        center = len(board.column_heights) // 2
        score += sum(board[center, r] == my for r in range(6)) * 3
        for w in self._windows(board):
            my_count = w.count(my)
            opp_count = w.count(opp)
            empty = w.count(None)
            if my_count == 4:
                score += 100
            elif my_count == 3 and empty == 1:
                score += 10
            elif my_count == 2 and empty == 2:
                score += 2
            elif opp_count == 3 and empty == 1:
                score -= 20
            elif opp_count == 2 and empty == 2:
                score -= 2
        return score

    def _windows(self, board):
        rows, cols = 6, 7
        for c in range(cols):
            for r in range(rows - 3):
                yield [board[c, r + i] for i in range(4)]
        for c in range(cols - 3):
            for r in range(rows):
                yield [board[c + i, r] for i in range(4)]
        for c in range(cols - 3):
            for r in range(rows - 3):
                yield [board[c + i, r + i] for i in range(4)]
        for c in range(cols - 3):
            for r in range(3, rows):
                yield [board[c + i, r - i] for i in range(4)]

    def _opponent(self, color):
        if hasattr(color, "name"):
            return [c for c in type(color) if c != color][0]
        return 1 if color == 2 else 2
