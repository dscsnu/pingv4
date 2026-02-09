from pingv4 import AbstractBot, ConnectFourBoard, CellState

ROWS = 6
COLS = 7
INF = 10**9
MOVE_ORDER = [3, 2, 4, 1, 5, 0, 6]


class MyBot(AbstractBot):

    @property
    def strategy_name(self) -> str:
        return "Apex"

    @property
    def author_name(self) -> str:
        return "Optimized Apex"

    @property
    def author_netid(self) -> str:
        return "apex_fast"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tt = {}

    # ======================
    # MAIN MOVE
    # ======================
    def get_move(self, board: ConnectFourBoard) -> int:
        ME = board.current_player
        OPP = CellState.Red if ME == CellState.Yellow else CellState.Yellow
        valid = board.get_valid_moves()

        # Opening
        if sum(board.column_heights) == 0:
            return 3

        # Immediate win
        for c in valid:
            if self._wins_after(board, c, ME):
                return c

        # Immediate block
        for c in valid:
            if self._wins_after(board, c, OPP):
                return c

        # Double threat win
        for c in valid:
            if self._double_threat(board.make_move(c), ME):
                return c

        depth = self._depth(board)

        best_score = -INF
        best_move = valid[0]

        for c in MOVE_ORDER:
            if c not in valid:
                continue
            score = self._alphabeta(
                board.make_move(c),
                depth - 1,
                -INF,
                INF,
                False,
                ME,
                OPP
            )
            score += self._parity(board.make_move(c))

            if score > best_score:
                best_score = score
                best_move = c

        return best_move

    # ======================
    # ALPHA BETA (FAST)
    # ======================
    def _alphabeta(self, board, depth, alpha, beta, maximizing, ME, OPP):
        key = (board.hash, depth, maximizing)
        if key in self.tt:
            return self.tt[key]

        if depth == 0 or not board.is_in_progress:
            if board.is_victory:
                return INF if board.winner == ME else -INF
            return self._eval(board, ME, OPP)

        valid = board.get_valid_moves()

        if maximizing:
            val = -INF
            for c in MOVE_ORDER:
                if c in valid:
                    val = max(val, self._alphabeta(
                        board.make_move(c),
                        depth - 1, alpha, beta, False, ME, OPP
                    ))
                    alpha = max(alpha, val)
                    if alpha >= beta:
                        break
        else:
            val = INF
            for c in MOVE_ORDER:
                if c in valid:
                    val = min(val, self._alphabeta(
                        board.make_move(c),
                        depth - 1, alpha, beta, True, ME, OPP
                    ))
                    beta = min(beta, val)
                    if alpha >= beta:
                        break

        self.tt[key] = val
        return val

    # ======================
    # EVALUATION
    # ======================
    def _eval(self, board, ME, OPP):
        score = 0

        # Center dominance
        for r in range(ROWS):
            if board[3, r] == ME:
                score += 6
            elif board[3, r] == OPP:
                score -= 6

        for w in self._windows(board):
            score += self._window_score(w, ME)
            score -= int(1.4 * self._window_score(w, OPP))

        return score

    def _window_score(self, w, p):
        c = w.count(p)
        e = w.count(None)
        if c == 4:
            return 100000
        if c == 3 and e == 1:
            return 120
        if c == 2 and e == 2:
            return 18
        return 0

    # ======================
    # THREATS
    # ======================
    def _double_threat(self, board, player):
        wins = 0
        for c in board.get_valid_moves():
            b = board.make_move(c)
            if b.is_victory and b.winner == player:
                wins += 1
        return wins >= 2

    # ======================
    # PARITY
    # ======================
    def _parity(self, board):
        s = 0
        for c in range(COLS):
            h = board.column_heights[c]
            if h < ROWS:
                s += 3 if h % 2 == 0 else -3
        return s

    # ======================
    # HELPERS
    # ======================
    def _wins_after(self, board, col, player):
        b = board.make_move(col)
        return b.is_victory and b.winner == player

    def _windows(self, board):
        W = []
        for r in range(ROWS):
            for c in range(COLS - 3):
                W.append([board[c+i, r] for i in range(4)])
        for c in range(COLS):
            for r in range(ROWS - 3):
                W.append([board[c, r+i] for i in range(4)])
        for c in range(COLS - 3):
            for r in range(ROWS - 3):
                W.append([board[c+i, r+i] for i in range(4)])
        for c in range(COLS - 3):
            for r in range(3, ROWS):
                W.append([board[c+i, r-i] for i in range(4)])
        return W

    # ======================
    # DEPTH CONTROL
    # ======================
    def _depth(self, board):
        moves = sum(board.column_heights)
        if moves < 10:
            return 7
        if moves < 20:
            return 8
        return 9