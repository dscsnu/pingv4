"""
SIMPLIFIED KILLER BOT - Learn from la390's Success
Focus: Simple, Fast, Aggressive Defense
"""

from pingv4 import AbstractBot, ConnectFourBoard, CellState
from typing import Dict, Tuple


class la390(AbstractBot):
    """
    Simplified bot that focuses on what works
    """

    def __init__(self, player: CellState):
        super().__init__(player)
        self.transposition_table: Dict[int, Tuple[int, float, int]] = {}
        self.MAX_DEPTH = 6  # Sweet spot: deeper than la390 but not too slow

    @property
    def strategy_name(self) -> str:
        return "Simplified Killer (depth 6)"

    @property
    def author_name(self) -> str:
        return "Lokkesh Ayyappan"

    @property
    def author_netid(self) -> str:
        return "la390"

    def get_move(self, board: ConnectFourBoard) -> int:
        """Find best move with la390-style approach"""
        me = board.current_player

        valid_moves = board.get_valid_moves()

        if len(valid_moves) == 1:
            return valid_moves[0]

        # 1. IMMEDIATE WIN CHECK
        for col in valid_moves:
            test = board.make_move(col)
            if test.is_victory and test.winner == me:
                return col

        # 2. IMMEDIATE BLOCK CHECK (critical!)
        opponent = CellState.Yellow if me == CellState.Red else CellState.Red
        for col in valid_moves:
            if self._opponent_wins_here(board, col, opponent):
                return col

        # 3. Use minimax
        best_col, _ = self.minimax(
            board, self.MAX_DEPTH, -float("inf"), float("inf"), True, me
        )
        return best_col

    def _opponent_wins_here(
        self, board: ConnectFourBoard, col: int, opponent: CellState
    ) -> bool:
        """Check if opponent would win by playing at col"""
        # We need to check if opponent playing at col creates 4-in-a-row
        # Get row where piece would land
        if col not in board.get_valid_moves():
            return False

        row = board.column_heights[col]
        if row >= board.num_rows:
            return False

        # Check all 4 directions for potential 4-in-a-row
        # This checks if opponent has 3-in-a-row with this spot empty

        # Horizontal
        count = 0
        for c in range(max(0, col - 3), min(7, col + 4)):
            if c == col:
                count += 1
            elif board[c, row] == opponent:
                count += 1
            else:
                count = 0
            if count >= 4:
                return True

        # Vertical (only check down)
        count = 1
        for r in range(row - 1, -1, -1):
            if board[col, r] == opponent:
                count += 1
            else:
                break
        if count >= 4:
            return True

        # Diagonal /
        count = 1
        # Down-left
        c, r = col - 1, row - 1
        while c >= 0 and r >= 0 and board[c, r] == opponent:
            count += 1
            c -= 1
            r -= 1
        # Up-right
        c, r = col + 1, row + 1
        while c < 7 and r < 6 and board[c, r] == opponent:
            count += 1
            c += 1
            r += 1
        if count >= 4:
            return True

        # Diagonal \
        count = 1
        # Up-left
        c, r = col - 1, row + 1
        while c >= 0 and r < 6 and board[c, r] == opponent:
            count += 1
            c -= 1
            r += 1
        # Down-right
        c, r = col + 1, row - 1
        while c < 7 and r >= 0 and board[c, r] == opponent:
            count += 1
            c += 1
            r -= 1
        if count >= 4:
            return True

        return False

    def minimax(
        self,
        board: ConnectFourBoard,
        depth: int,
        alpha: float,
        beta: float,
        is_maximizing: bool,
        my_color: CellState,
    ) -> Tuple[int, float]:
        """Minimax with alpha-beta pruning - la390 style"""

        # Check transposition table
        state_id = board.hash
        if state_id in self.transposition_table:
            stored_depth, stored_score, stored_col = self.transposition_table[state_id]
            if stored_depth >= depth:
                return stored_col, stored_score

        valid_moves = board.get_valid_moves()

        # Terminal conditions
        if board.is_victory:
            if board.winner == my_color:
                score = 1000000 + depth
            else:
                score = -1000000 - depth
            return None, score

        if not valid_moves or depth == 0:
            return None, self.score_position(board, my_color)

        # Move ordering: center first (la390's winning strategy)
        center_order = [3, 2, 4, 1, 5, 0, 6]
        ordered_moves = [c for c in center_order if c in valid_moves]

        best_col = ordered_moves[0]

        if is_maximizing:
            max_eval = -float("inf")
            for col in ordered_moves:
                new_board = board.make_move(col)
                _, eval_score = self.minimax(
                    new_board, depth - 1, alpha, beta, False, my_color
                )

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_col = col
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break

            self.transposition_table[state_id] = (depth, max_eval, best_col)
            return best_col, max_eval
        else:
            min_eval = float("inf")
            for col in ordered_moves:
                new_board = board.make_move(col)
                _, eval_score = self.minimax(
                    new_board, depth - 1, alpha, beta, True, my_color
                )

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_col = col
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break

            self.transposition_table[state_id] = (depth, min_eval, best_col)
            return best_col, min_eval

    def score_position(self, board: ConnectFourBoard, piece: CellState) -> float:
        """Evaluate position - la390 style but enhanced"""
        score = 0

        # Center control (la390 uses *3, we use *4 for slight edge)
        center_array = [board[3, i] for i in range(6)]
        center_count = center_array.count(piece)
        score += center_count * 4

        # Evaluate all windows
        # Horizontal
        for r in range(6):
            for c in range(4):
                window = [board[c + i, r] for i in range(4)]
                score += self.evaluate_window(window, piece)

        # Vertical
        for c in range(7):
            for r in range(3):
                window = [board[c, r + i] for i in range(4)]
                score += self.evaluate_window(window, piece)

        # Diagonal /
        for r in range(3):
            for c in range(4):
                window = [board[c + i, r + i] for i in range(4)]
                score += self.evaluate_window(window, piece)

        # Diagonal \
        for r in range(3, 6):
            for c in range(4):
                window = [board[c + i, r - i] for i in range(4)]
                score += self.evaluate_window(window, piece)

        return score

    def evaluate_window(self, window: list, piece: CellState) -> float:
        """Evaluate 4-cell window - MATCH LA390'S WINNING FORMULA"""
        score = 0
        opp_piece = CellState.Yellow if piece == CellState.Red else CellState.Red

        piece_count = window.count(piece)
        empty_count = window.count(None)
        opp_count = window.count(opp_piece)

        # Offense (slightly better than la390)
        if piece_count == 4:
            score += 10000
        elif piece_count == 3 and empty_count == 1:
            score += 7  # la390 uses 5, we use 7
        elif piece_count == 2 and empty_count == 2:
            score += 3  # la390 uses 2, we use 3
        elif piece_count == 1 and empty_count == 3:
            score += 1

        # Defense - CRITICAL (match la390's -80, even go stronger)
        if opp_count == 3 and empty_count == 1:
            score -= 90  # Even more aggressive than la390's -80!
        elif opp_count == 2 and empty_count == 2:
            score -= 3

        return score
