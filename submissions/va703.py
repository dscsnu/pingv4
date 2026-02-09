from pingv4 import AbstractBot, ConnectFourBoard, CellState
import random

ROWS = 6
COLS = 7
INF = 10**9
BASE_DEPTH = 5
MOVE_ORDER = [3, 2, 4, 1, 5, 0, 6]


class va703(AbstractBot):

    @property
    def strategy_name(self) -> str:
        return "ThreatSpace-AlphaBeta"

    @property
    def author_name(self) -> str:
        return "Vasu"

    @property
    def author_netid(self) -> str:
        return "va703"

    # ================== MAIN ENTRY ==================

    def get_move(self, board: ConnectFourBoard) -> int:
        ME = board.current_player
        OPP = CellState.Red if ME == CellState.Yellow else CellState.Yellow
        valid = board.get_valid_moves()
        ply = sum(board.column_heights)

        # 0. OPENING BOOK (anti-symmetry)
        book_move = self._opening_book(board, valid)
        if book_move is not None:
            return book_move

        # 1. Instant win
        for col in valid:
            if self._winning_after_move(board, col, ME):
                return col

        # 2. Instant block
        for col in valid:
            if self._winning_after_move(board, col, OPP):
                return col

        best_score = -INF
        best_move = valid[0]

        for col in MOVE_ORDER:
            if col not in valid:
                continue

            child = board.make_move(col)

            # 3a. Double threat → forced win
            if self._creates_double_threat(child, ME):
                return col

            # 3b. Selective deepening
            depth = BASE_DEPTH
            if self._creates_threat(child, ME) or self._creates_threat(child, OPP):
                depth += 2

            score = self._minimax(
                child, depth - 1, -INF, INF,
                maximizing=False, ME=ME, OPP=OPP
            )

            # 3c. Parity bonus
            score += self._parity_score(child, ME, OPP)

            if score > best_score:
                best_score = score
                best_move = col

        return best_move

    # ================== MINIMAX ==================

    def _minimax(self, board, depth, alpha, beta, maximizing, ME, OPP):
        if depth == 0 or not board.is_in_progress:
            if board.is_victory:
                if board.winner == ME:
                    return INF
                elif board.winner == OPP:
                    return -INF
            return self._evaluate(board, ME, OPP)

        valid = board.get_valid_moves()

        if maximizing:
            value = -INF
            for col in MOVE_ORDER:
                if col in valid:
                    value = max(value,
                        self._minimax(
                            board.make_move(col),
                            depth - 1, alpha, beta, False, ME, OPP
                        ))
                    alpha = max(alpha, value)
                    if alpha >= beta:
                        break
            return value

        else:
            value = INF
            for col in MOVE_ORDER:
                if col in valid:
                    value = min(value,
                        self._minimax(
                            board.make_move(col),
                            depth - 1, alpha, beta, True, ME, OPP
                        ))
                    beta = min(beta, value)
                    if alpha >= beta:
                        break
            return value

    # ================== EVALUATION ==================

    def _evaluate(self, board, ME, OPP):
        if board.is_victory:
            if board.winner == ME:
                return INF
            elif board.winner == OPP:
                return -INF

        score = 0

        # Center control
        for r in range(ROWS):
            if board[3, r] == ME:
                score += 6
            elif board[3, r] == OPP:
                score -= 6

        # Window scoring
        for window in self._all_windows(board):
            score += self._score_window(window, ME)
            score -= int(1.3 * self._score_window(window, OPP))

        return score

    def _score_window(self, window, piece):
        count_piece = window.count(piece)
        count_empty = window.count(None)

        if count_piece == 4:
            return 100000
        if count_piece == 3 and count_empty == 1:
            return 120
        if count_piece == 2 and count_empty == 2:
            return 15
        return 0

    # ================== THREAT SPACE ==================

    def _creates_threat(self, board, player):
        return self._count_winning_moves(board, player) >= 1

    def _creates_double_threat(self, board, player):
        return self._count_winning_moves(board, player) >= 2

    def _count_winning_moves(self, board, player):
        count = 0
        for col in board.get_valid_moves():
            next_board = board.make_move(col)
            if next_board.is_victory and next_board.winner == player:
                count += 1
        return count

    # ================== PARITY CONTROL ==================

    def _parity_score(self, board, ME, OPP):
        score = 0
        for c in range(COLS):
            for r in range(ROWS):
                if board[c, r] is None:
                    if r % 2 == 1:
                        score += 1
                    else:
                        score -= 1
        return score

    # ================== OPENING BOOK ==================

    def _opening_book(self, board, valid):
        ply = sum(board.column_heights)

        if ply == 0:
            return 3

        if ply == 2 and 2 in valid and 4 in valid:
            return random.choice([2, 4])

        if ply == 4 and 1 in valid:
            return 1

        return None

    # ================== HELPERS ==================

    def _winning_after_move(self, board, col, player):
        new_board = board.make_move(col)
        return new_board.is_victory and new_board.winner == player

    def _all_windows(self, board):
        windows = []

        for r in range(ROWS):
            for c in range(COLS - 3):
                windows.append([board[c + i, r] for i in range(4)])

        for c in range(COLS):
            for r in range(ROWS - 3):
                windows.append([board[c, r + i] for i in range(4)])

        for c in range(COLS - 3):
            for r in range(ROWS - 3):
                windows.append([board[c + i, r + i] for i in range(4)])

        for c in range(COLS - 3):
            for r in range(3, ROWS):
                windows.append([board[c + i, r - i] for i in range(4)])

        return windows