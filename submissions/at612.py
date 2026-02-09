"""
You can follow this template for your Connect4 bot.
Copy this and rename it to: yourname_yournetid.py
"""

from pingv4 import AbstractBot, ConnectFourBoard, CellState
import math
import random


class at612(AbstractBot):
    """
    This will be your Connect4 bot.
    CHANGE THE CLASS NAME TO your snu net id.
    """

    @property
    def strategy_name(self) -> str:
        return "this kinda sucks but ok"

    @property
    def author_name(self) -> str:
        return "Anirudh Tata"

    @property
    def author_netid(self) -> str:
        return "at612"

    def __init__(self, player: CellState):
        super().__init__(player)

        self.colour = player
        # Depth 5 is the 'sweet spot' for Python—smart enough to see traps,
        # fast enough not to timeout.
        self.depth = 5

    def get_move(self, board) -> int:
        my_color = board.current_player
        opp_color = 2 if my_color == 1 else 1  # Assuming 1 and 2 are the colors
        valid_moves = self.get_ordered_moves(board)

        # --- SHORT CIRCUIT 1: OFFENSE ---
        # If I can win right now, take it.
        for col in valid_moves:
            if board.make_move(col).winner == my_color:
                return col

        # --- SHORT CIRCUIT 2: DEFENSE ---
        # If the opponent can win on their next move, block them!
        for col in valid_moves:
            # We simulate what happens if the OPPONENT moves there
            # Since board.make_move uses current_player, we just check the winner
            # after simulating a move.
            future_state = board.make_move(col)
            if future_state.winner == opp_color:
                return col

        # --- MINIMAX SEARCH ---
        best_score = -math.inf
        best_col = random.choice(valid_moves)

        for col in valid_moves:
            temp_board = board.make_move(col)
            score = self.minimax(
                temp_board,
                self.depth - 1,
                -math.inf,
                math.inf,
                False,
                my_color,
                opp_color,
            )

            if score > best_score:
                best_score = score
                best_col = col

        return best_col

    def minimax(self, board, depth, alpha, beta, is_maximizing, my_color, opp_color):
        if board.winner == my_color:
            return 1000000
        if board.winner == opp_color:
            return -1000000
        if not board.is_in_progress:
            return 0  # Draw
        if depth == 0:
            return self.evaluate_board(board, my_color, opp_color)

        valid_moves = self.get_ordered_moves(board)

        if is_maximizing:
            value = -math.inf
            for col in valid_moves:
                value = max(
                    value,
                    self.minimax(
                        board.make_move(col),
                        depth - 1,
                        alpha,
                        beta,
                        False,
                        my_color,
                        opp_color,
                    ),
                )
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = math.inf
            for col in valid_moves:
                value = min(
                    value,
                    self.minimax(
                        board.make_move(col),
                        depth - 1,
                        alpha,
                        beta,
                        True,
                        my_color,
                        opp_color,
                    ),
                )
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value

    def get_ordered_moves(self, board):
        # Priorities center (3) then works outward: [3, 2, 4, 1, 5, 0, 6]
        return sorted(board.get_valid_moves(), key=lambda x: abs(3 - x))

    def evaluate_board(self, board, my_color, opp_color):
        score = 0

        # 1. Center Dominance
        for r in range(6):
            if board[3, r] == my_color:
                score += 5
            elif board[3, r] == opp_color:
                score -= 5

        # 2. Window Scanning (Horizontal, Vertical, Diagonals)
        # Horizontal
        for r in range(6):
            for c in range(4):
                window = [board[c + i, r] for i in range(4)]
                score += self._score_window(window, my_color, opp_color)

        # Vertical
        for c in range(7):
            for r in range(3):
                window = [board[c, r + i] for i in range(4)]
                score += self._score_window(window, my_color, opp_color)

        # Pos Diagonal
        for r in range(3):
            for c in range(4):
                window = [board[c + i, r + i] for i in range(4)]
                score += self._score_window(window, my_color, opp_color)

        # Neg Diagonal
        for r in range(3, 6):
            for c in range(4):
                window = [board[c + i, r - i] for i in range(4)]
                score += self._score_window(window, my_color, opp_color)

        return score

    def _score_window(self, window, my_color, opp_color):
        score = 0
        # Check based on your guide's CellState (assuming None/0 is empty)
        empty = None

        if window.count(my_color) == 3 and window.count(empty) == 1:
            score += 100
        elif window.count(my_color) == 2 and window.count(empty) == 2:
            score += 10

        if window.count(opp_color) == 3 and window.count(empty) == 1:
            score -= 1000  # Massive penalty for letting opponent have a 3-in-a-row

        return score
