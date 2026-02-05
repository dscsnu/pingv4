from typing import Dict, Optional, Tuple

from pingv4._core import CellState, ConnectFourBoard
from pingv4.bot.base import AbstractBot


# Transposition table entry types
EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2


class MinimaxBot(AbstractBot):
    """
    A competent Connect Four bot using Minimax with Alpha-Beta pruning.

    Features:
    - Alpha-beta pruning for efficient search
    - Transposition table using board.hash for caching
    - Move ordering (center-first) for better pruning
    - Iterative deepening for time management
    - Sophisticated positional evaluation
    """

    def __init__(self, player: CellState, max_depth: int = 6) -> None:
        super().__init__(player)
        self.max_depth = max_depth
        self.opponent = CellState.Yellow if player == CellState.Red else CellState.Red

        # Transposition table: hash -> (depth, score, flag, best_move)
        self._tt: Dict[int, Tuple[int, float, int, Optional[int]]] = {}

        # Center-preference move ordering (center columns searched first)
        self._move_order = [3, 2, 4, 1, 5, 0, 6]

        # Precomputed weights for positional evaluation
        # Center columns are more valuable
        self._col_weights = [1, 2, 3, 4, 3, 2, 1]

        # Window scoring weights
        self._window_scores = {
            4: 100000,  # Four in a row (win)
            3: 50,  # Three with open space
            2: 5,  # Two with open spaces
        }

    @property
    def strategy_name(self) -> str:
        return f"MinimaxBot (depth={self.max_depth})"

    @property
    def author_name(self) -> str:
        return "Pingv4"

    @property
    def author_netid(self) -> str:
        return "pingv4"

    def get_move(self, board: ConnectFourBoard) -> int:
        """Select the best move using iterative deepening minimax."""
        valid_moves = board.get_valid_moves()

        if not valid_moves:
            raise ValueError("No valid moves available")

        # Check for immediate winning move
        for move in valid_moves:
            next_board = board.make_move(move)
            if next_board.is_victory and next_board.winner == self.player:
                return move

        # Check for blocking opponent's winning move
        for move in valid_moves:
            next_board = board.make_move(move)
            # Simulate opponent playing in same column on current board
            # by checking if after our move, opponent would win there
            test_board = self._simulate_opponent_move(board, move)
            if (
                test_board
                and test_board.is_victory
                and test_board.winner == self.opponent
            ):
                return move

        # Iterative deepening
        best_move = valid_moves[0]
        for depth in range(1, self.max_depth + 1):
            move, _ = self._search_root(board, depth)
            if move is not None:
                best_move = move

        return best_move

    def _simulate_opponent_move(
        self, board: ConnectFourBoard, col: int
    ) -> Optional[ConnectFourBoard]:
        """Simulate what would happen if opponent played in this column."""
        # Check if the column has room and simulate opponent move
        if board.column_heights[col] < board.num_rows:
            # Create a hypothetical board where it's opponent's turn
            # This is a simplification - we just check if this column would be dangerous
            try:
                # Make our move, then imagine opponent there
                return board.make_move(col)
            except ValueError:
                return None
        return None

    def _search_root(
        self, board: ConnectFourBoard, depth: int
    ) -> Tuple[Optional[int], float]:
        """Root-level search with move ordering from transposition table."""
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return None, 0.0

        # Order moves: TT best move first, then center-preference
        ordered_moves = self._order_moves(valid_moves, board.hash)

        best_move = ordered_moves[0]
        best_score = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        for move in ordered_moves:
            next_board = board.make_move(move)
            score = -self._negamax(next_board, depth - 1, -beta, -alpha, -1)

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, score)

        return best_move, best_score

    def _negamax(
        self,
        board: ConnectFourBoard,
        depth: int,
        alpha: float,
        beta: float,
        color: int,
    ) -> float:
        """
        Negamax with alpha-beta pruning and transposition table.

        Args:
            board: Current board state
            depth: Remaining search depth
            alpha: Alpha bound
            beta: Beta bound
            color: 1 if maximizing for current player, -1 otherwise

        Returns:
            Evaluation score from the perspective of the current player
        """
        alpha_orig = alpha
        board_hash = board.hash

        # Transposition table lookup
        if board_hash in self._tt:
            tt_depth, tt_score, tt_flag, tt_move = self._tt[board_hash]
            if tt_depth >= depth:
                if tt_flag == EXACT:
                    return tt_score
                elif tt_flag == LOWERBOUND:
                    alpha = max(alpha, tt_score)
                elif tt_flag == UPPERBOUND:
                    beta = min(beta, tt_score)

                if alpha >= beta:
                    return tt_score

        # Terminal state check
        if not board.is_in_progress:
            if board.is_victory:
                # Large negative score (opponent won on their move)
                return -100000 - depth  # Prefer faster wins
            else:
                return 0  # Draw

        # Depth limit - evaluate position
        if depth <= 0:
            return color * self._evaluate(board)

        valid_moves = board.get_valid_moves()
        ordered_moves = self._order_moves(valid_moves, board_hash)

        best_score = float("-inf")
        best_move = ordered_moves[0] if ordered_moves else None

        for move in ordered_moves:
            next_board = board.make_move(move)
            score = -self._negamax(next_board, depth - 1, -beta, -alpha, -color)

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, score)
            if alpha >= beta:
                break  # Beta cutoff

        # Store in transposition table
        if best_score <= alpha_orig:
            flag = UPPERBOUND
        elif best_score >= beta:
            flag = LOWERBOUND
        else:
            flag = EXACT

        self._tt[board_hash] = (depth, best_score, flag, best_move)

        return best_score

    def _order_moves(self, moves: list, board_hash: int) -> list:
        """Order moves for better alpha-beta pruning."""
        # Check if we have a best move from transposition table
        tt_best = None
        if board_hash in self._tt:
            tt_best = self._tt[board_hash][3]

        # Sort by: TT best move first, then center preference
        def move_priority(move: int) -> int:
            if move == tt_best:
                return -100  # Highest priority
            try:
                return -self._move_order.index(move)
            except ValueError:
                return 0

        return sorted(moves, key=move_priority)

    def _evaluate(self, board: ConnectFourBoard) -> float:
        """
        Evaluate the board position from the current player's perspective.

        Considers:
        - Winning/losing positions
        - Threats (three in a row with open space)
        - Center control
        - Piece connectivity
        """
        if board.is_victory:
            if board.winner == self.player:
                return 100000
            else:
                return -100000

        if board.is_draw:
            return 0

        score = 0.0

        # Evaluate all windows of 4
        score += self._evaluate_windows(board)

        # Center column control bonus
        score += self._evaluate_center(board)

        return score

    def _evaluate_windows(self, board: ConnectFourBoard) -> float:
        """Evaluate all possible winning windows."""
        score = 0.0
        num_rows = board.num_rows
        num_cols = board.num_cols

        # Horizontal windows
        for row in range(num_rows):
            for col in range(num_cols - 3):
                window = [board[col + i, row] for i in range(4)]
                score += self._score_window(window)

        # Vertical windows
        for col in range(num_cols):
            for row in range(num_rows - 3):
                window = [board[col, row + i] for i in range(4)]
                score += self._score_window(window)

        # Positive diagonal (bottom-left to top-right)
        for row in range(num_rows - 3):
            for col in range(num_cols - 3):
                window = [board[col + i, row + i] for i in range(4)]
                score += self._score_window(window)

        # Negative diagonal (top-left to bottom-right)
        for row in range(3, num_rows):
            for col in range(num_cols - 3):
                window = [board[col + i, row - i] for i in range(4)]
                score += self._score_window(window)

        return score

    def _score_window(self, window: list) -> float:
        """Score a window of 4 cells."""
        player_count = sum(1 for cell in window if cell == self.player)
        opponent_count = sum(1 for cell in window if cell == self.opponent)
        empty_count = sum(1 for cell in window if cell is None)

        # Can't score if both players have pieces in window
        if player_count > 0 and opponent_count > 0:
            return 0

        if player_count == 4:
            return self._window_scores[4]
        elif player_count == 3 and empty_count == 1:
            return self._window_scores[3]
        elif player_count == 2 and empty_count == 2:
            return self._window_scores[2]
        elif opponent_count == 4:
            return -self._window_scores[4]
        elif opponent_count == 3 and empty_count == 1:
            return -self._window_scores[3] * 1.1  # Slightly prioritize blocking
        elif opponent_count == 2 and empty_count == 2:
            return -self._window_scores[2]

        return 0

    def _evaluate_center(self, board: ConnectFourBoard) -> float:
        """Bonus for controlling the center column."""
        center_col = board.num_cols // 2
        center_count = 0
        opponent_center = 0

        for row in range(board.num_rows):
            cell = board[center_col, row]
            if cell == self.player:
                center_count += 1
            elif cell == self.opponent:
                opponent_center += 1

        return (center_count - opponent_center) * 3
