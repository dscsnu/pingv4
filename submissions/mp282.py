from pingv4 import AbstractBot
from pingv4._core import CellState, ConnectFourBoard


class mp282(AbstractBot):
    """
    Connect Four AI using Negamax with Alpha-Beta Pruning.
    Based on classic negamax implementation with position evaluation.
    """

    # Piece values for scoring windows
    AI_PIECE = 1
    HUMAN_PIECE = 2
    EMPTY = 0

    # Score constants
    WINDOW_LENGTH = 4
    EMPTY_SCORE = 0
    ONE_SCORE = 1
    TWO_SCORE = 5
    THREE_SCORE = 10
    FOUR_SCORE = 1000

    def __init__(self, player: CellState, depth: int = 4) -> None:
        super().__init__(player)
        self.depth = depth
        # Pre-order columns for move ordering (center bias)
        self.column_order = [3, 2, 4, 1, 5, 0, 6]

    @property
    def strategy_name(self) -> str:
        return "MP282 Bot"

    @property
    def author_name(self) -> str:
        return "Mukesh P"

    @property
    def author_netid(self) -> str:
        return "mp282"

    def get_move(self, board: ConnectFourBoard) -> int:
        """
        Get the best move using negamax with alpha-beta pruning.
        """
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return 0

        # Order moves for better pruning efficiency
        valid_moves = self._order_moves(valid_moves)

        best_score = -float("inf")
        best_move = valid_moves[0]
        alpha = -float("inf")
        beta = float("inf")

        for col in valid_moves:
            new_board = board.make_move(col)
            # Negamax: flip perspective and negate score
            score = -self._negamax(new_board, self.depth - 1, -beta, -alpha)

            if score > best_score:
                best_score = score
                best_move = col

            alpha = max(alpha, score)

        return best_move

    def _order_moves(self, moves: list) -> list:
        """Order moves by strategic preference (center-first)."""
        return sorted(moves, key=lambda x: abs(x - 3))

    def _negamax(
        self, board: ConnectFourBoard, depth: int, alpha: float, beta: float
    ) -> float:
        """
        Negamax algorithm with alpha-beta pruning.
        Returns the score from the perspective of the current player.
        """
        valid_moves = board.get_valid_moves()

        # Terminal state checks
        if board.is_victory:
            # Return large positive or negative score
            return -self.FOUR_SCORE if board.winner == self.player else self.FOUR_SCORE
        if board.is_tie:
            return 0
        if depth == 0:
            return self._evaluate_position(board)

        max_eval = -float("inf")
        for col in valid_moves:
            new_board = board.make_move(col)
            # Recursive negamax call
            eval_score = -self._negamax(new_board, depth - 1, -beta, -alpha)
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if alpha >= beta:
                break  # Beta cutoff
        return max_eval

    def _evaluate_position(self, board: ConnectFourBoard) -> float:
        """
        Evaluate the current board position.
        Returns a score positive for AI advantage, negative for opponent.
        """
        score = 0

        # Center column preference
        center_array = [board.cell_states[3][row] for row in range(board.rows)]
        center_count = center_array.count(self.player)
        score += center_count * 3

        # Evaluate all windows in horizontal, vertical, and diagonal directions
        # Horizontal windows
        score += self._evaluate_horizontal(board)
        # Vertical windows
        score += self._evaluate_vertical(board)
        # Positive diagonal (bottom-left to top-right)
        score += self._evaluate_diagonal(board)
        # Negative diagonal (top-left to bottom-right)
        score += self._evaluate_anti_diagonal(board)

        return score

    def _evaluate_horizontal(self, board: ConnectFourBoard) -> float:
        """Evaluate horizontal windows."""
        score = 0
        for row in range(board.rows):
            for col in range(board.cols - 3):
                window = self._get_window(board, col, row, 0, 1)
                score += self._evaluate_window(window)
        return score

    def _evaluate_vertical(self, board: ConnectFourBoard) -> float:
        """Evaluate vertical windows."""
        score = 0
        for col in range(board.cols):
            for row in range(board.rows - 3):
                window = self._get_window(board, col, row, 1, 0)
                score += self._evaluate_window(window)
        return score

    def _evaluate_diagonal(self, board: ConnectFourBoard) -> float:
        """Evaluate positive diagonal windows (going up-right)."""
        score = 0
        for row in range(board.rows - 3):
            for col in range(board.cols - 3):
                window = self._get_window(board, col, row, 1, 1)
                score += self._evaluate_window(window)
        return score

    def _evaluate_anti_diagonal(self, board: ConnectFourBoard) -> float:
        """Evaluate negative diagonal windows (going up-left)."""
        score = 0
        for row in range(board.rows - 3):
            for col in range(3, board.cols):
                window = self._get_window(board, col, row, 1, -1)
                score += self._evaluate_window(window)
        return score

    def _get_window(
        self,
        board: ConnectFourBoard,
        col: int,
        row: int,
        delta_row: int,
        delta_col: int,
    ) -> list:
        """Get a window of 4 cells starting from (col, row)."""
        cells = []
        for i in range(self.WINDOW_LENGTH):
            new_row = row + i * delta_row
            new_col = col + i * delta_col
            if 0 <= new_row < board.rows and 0 <= new_col < board.cols:
                cells.append(board.cell_states[new_col][new_row])
            else:
                cells.append(CellState.Empty)
        return cells

    def _evaluate_window(self, window: list) -> float:
        """
        Evaluate a window of 4 cells.
        Returns a score based on the pieces in the window.
        """
        score = 0

        # Convert CellState to our scoring format
        piece_map = {
            self.player: self.AI_PIECE,
            CellState.Red: self.HUMAN_PIECE
            if self.player == CellState.Yellow
            else self.AI_PIECE,
            CellState.Yellow: self.HUMAN_PIECE
            if self.player == CellState.Red
            else self.AI_PIECE,
            CellState.Empty: self.EMPTY,
        }

        # Handle case where window contains opponent pieces
        pieces = []
        for cell in window:
            if cell == CellState.Empty:
                pieces.append(self.EMPTY)
            elif cell == self.player:
                pieces.append(self.AI_PIECE)
            else:
                pieces.append(self.HUMAN_PIECE)

        ai_count = pieces.count(self.AI_PIECE)
        human_count = pieces.count(self.HUMAN_PIECE)
        empty_count = pieces.count(self.EMPTY)

        # Score based on piece counts in the window
        if ai_count == 4:
            score += self.FOUR_SCORE
        elif ai_count == 3 and empty_count == 1:
            score += self.THREE_SCORE
        elif ai_count == 2 and empty_count == 2:
            score += self.TWO_SCORE
        elif ai_count == 1 and empty_count == 3:
            score += self.ONE_SCORE

        # Subtract for opponent advantages (don't let them win)
        if human_count == 3 and empty_count == 1:
            score -= self.THREE_SCORE
        elif human_count == 2 and empty_count == 2:
            score -= self.TWO_SCORE
        elif human_count == 1 and empty_count == 3:
            score -= self.ONE_SCORE

        return score
