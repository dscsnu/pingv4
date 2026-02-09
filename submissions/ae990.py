"""
ae990.py - v17: Fast Fork Bot (<10s per move)
- Uses undoable moves (no deepcopy → much faster search)
- Quick priority checks handle obvious wins/blocks/forks instantly
- Iterative deepening alpha-beta minimax (starts at depth 6, increases)
- Strict 9-second time limit per move
- Strong against MinimaxBot (depth=6) in the library
"""

from pingv4 import AbstractBot, ConnectFourBoard, CellState
import time


class Ae990(AbstractBot):
    @property
    def strategy_name(self) -> str:
        return "Fast Fork v17 (<10s)"

    @property
    def author_name(self) -> str:
        return "Anahita"

    @property
    def author_netid(self) -> str:
        return "ae990"

    def get_move(self, board: ConnectFourBoard) -> int:
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return 0

        # Player setup: 1 = us, 2 = opponent
        me = 1
        opp = 2

        # Build undoable board state (integers only)
        self.grid = [[0] * 6 for _ in range(7)]
        self.heights = list(board.column_heights)
        for c in range(7):
            for r in range(self.heights[c]):
                cell = board[c, r]
                self.grid[c][r] = me if cell == board.current_player else opp

        # 1. Quick priority checks (very fast)
        quick_move = self.quick_priority(valid_moves)
        if quick_move is not None:
            return quick_move

        # 2. Iterative deepening alpha-beta search
        start_time = time.time()
        TIME_LIMIT = 9.0

        best_move = self.center_ordered(valid_moves)[0]
        best_score = -999999

        depth = 6
        while time.time() - start_time < TIME_LIMIT - 0.5:  # buffer
            current_best_move, current_best_score = self.search_at_depth(
                depth, start_time, TIME_LIMIT
            )
            if current_best_move is not None:
                best_move = current_best_move
                best_score = current_best_score
            depth += 1

        return best_move

    def quick_priority(self, valid_moves):
        # Priority 1: Immediate win
        for col in self.center_ordered(valid_moves):
            self.make_move(col, 1)
            if self.has_win(1):
                self.undo_move(col)
                return col
            self.undo_move(col)

        # Priority 2: Block immediate opponent win
        for col in self.center_ordered(valid_moves):
            self.make_move(col, 2)
            if self.has_win(2):
                self.undo_move(col)
                return col
            self.undo_move(col)

        # Priority 3: Block opponent fork (≥2 winning moves)
        for col in self.center_ordered(valid_moves):
            self.make_move(col, 2)
            threats = self.count_threats(2)
            self.undo_move(col)
            if threats >= 2:
                return col

        # Priority 4: Create our own fork
        for col in self.center_ordered(valid_moves):
            self.make_move(col, 1)
            threats = self.count_threats(1)
            self.undo_move(col)
            if threats >= 2:
                return col

        # Priority 5: Create single threat
        for col in self.center_ordered(valid_moves):
            self.make_move(col, 1)
            threats = self.count_threats(1)
            self.undo_move(col)
            if threats >= 1:
                return col

        return None

    def search_at_depth(self, depth, start_time, time_limit):
        valid_moves = [c for c in range(7) if self.heights[c] < 6]
        best_move = None
        best_score = -999999
        alpha = -999999
        beta = 999999

        for col in self.center_ordered(valid_moves):
            if time.time() - start_time >= time_limit - 0.5:
                break

            self.make_move(col, 1)
            score = self.minimax(depth - 1, alpha, beta, False, 2, start_time, time_limit)
            self.undo_move(col)

            if score > best_score:
                best_score = score
                best_move = col

            alpha = max(alpha, score)

        return best_move, best_score

    def minimax(self, depth, alpha, beta, maximizing, player, start_time, time_limit):
        if time.time() - start_time >= time_limit - 0.5:
            return 0  # timeout → neutral score

        if depth == 0:
            return self.evaluate()

        valid = [c for c in range(7) if self.heights[c] < 6]

        if maximizing:  # our turn
            max_eval = -999999
            for col in self.order_moves(valid, 1):
                self.make_move(col, 1)
                eval = self.minimax(depth - 1, alpha, beta, False, player, start_time, time_limit)
                self.undo_move(col)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:  # opponent turn
            min_eval = 999999
            for col in self.order_moves(valid, player):
                self.make_move(col, player)
                eval = self.minimax(depth - 1, alpha, beta, True, 3 - player, start_time, time_limit)
                self.undo_move(col)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def evaluate(self):
        me = 1
        opp = 2
        score = 0

        # Center control (very important)
        for r in range(6):
            if self.grid[3][r] == me:
                score += 8
            elif self.grid[3][r] == opp:
                score -= 8

        # Threats (immediate wins next turn)
        my_threats = self.count_threats(me)
        opp_threats = self.count_threats(opp)
        score += my_threats * 300
        score -= opp_threats * 400

        # Huge penalty if opponent has fork
        if opp_threats >= 2:
            score -= 15000

        # Simple mobility bonus
        score += (len([c for c in range(7) if self.heights[c] < 6]) * 4)

        return score

    # ────────────────────────────────────────────────
    # Core helpers (undoable)
    # ────────────────────────────────────────────────

    def make_move(self, col, player):
        r = self.heights[col]
        self.grid[col][r] = player
        self.heights[col] += 1

    def undo_move(self, col):
        self.heights[col] -= 1
        r = self.heights[col]
        self.grid[col][r] = 0

    def has_win(self, player):
        # Vertical
        for c in range(7):
            for r in range(3):
                if all(self.grid[c][r + i] == player for i in range(4)):
                    return True
        # Horizontal
        for r in range(6):
            for c in range(4):
                if all(self.grid[c + i][r] == player for i in range(4)):
                    return True
        # Diagonal /
        for r in range(3):
            for c in range(4):
                if all(self.grid[c + i][r + i] == player for i in range(4)):
                    return True
        # Diagonal \
        for r in range(3):
            for c in range(3, 7):
                if all(self.grid[c - i][r + i] == player for i in range(4)):
                    return True
        return False

    def count_threats(self, player):
        count = 0
        for col in range(7):
            if self.heights[col] < 6:
                self.make_move(col, player)
                if self.has_win(player):
                    count += 1
                self.undo_move(col)
        return count

    def center_ordered(self, moves):
        order = [3, 2, 4, 1, 5, 0, 6]
        return [c for c in order if c in moves]

    def order_moves(self, valid, player):
        scored = []
        for col in valid:
            self.make_move(col, player)
            threats = self.count_threats(player)
            scored.append((threats, col))
            self.undo_move(col)
        scored.sort(reverse=True)  # high threats first
        return [col for _, col in scored] or valid