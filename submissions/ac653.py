import math
import random
from pingv4 import AbstractBot, ConnectFourBoard, CellState

class ac653(AbstractBot):
    @property
    def strategy_name(self):
        return "The Punisher"

    @property
    def author_name(self):
        return "Aaryan"

    @property
    def author_netid(self):
        return "ac653"

    def get_move(self, board: ConnectFourBoard) -> int:
        valid_moves = board.get_valid_moves()
        me = board.current_player
        opp = CellState.Yellow if me == CellState.Red else CellState.Red

        # Immediate Win/Block (The "No-Brainer" Phase)
        for col in valid_moves:
            nb = board.make_move(col)
            if nb.is_victory: return col
            
        # Minimax with higher depth
        try:
            # Depth 6 is the "sweet spot" to crush a Depth 4 bot
            best_col, _ = self.minimax(board, 6, -math.inf, math.inf, True, me, opp)
            return best_col if best_col is not None else valid_moves[0]
        except:
            return random.choice(valid_moves)

    def minimax(self, board, depth, alpha, beta, maximizing, me, opp):
        valid_moves = board.get_valid_moves()
        
        if board.is_victory:
            return (None, -1000000 if maximizing else 1000000)
        if board.is_draw or depth == 0:
            return (None, self.evaluate_board(board, me, opp))

        # Advanced Move Ordering: Center -> Sides
        valid_moves.sort(key=lambda x: abs(x - 3))

        if maximizing:
            value = -math.inf
            best_col = valid_moves[0]
            for col in valid_moves:
                next_val = self.minimax(board.make_move(col), depth-1, alpha, beta, False, me, opp)[1]
                if next_val > value:
                    value = next_val
                    best_col = col
                alpha = max(alpha, value)
                if alpha >= beta: break
            return best_col, value
        else:
            value = math.inf
            best_col = valid_moves[0]
            for col in valid_moves:
                next_val = self.minimax(board.make_move(col), depth-1, alpha, beta, True, me, opp)[1]
                if next_val < value:
                    value = next_val
                    best_col = col
                beta = min(beta, value)
                if alpha >= beta: break
            return best_col, value

    def evaluate_board(self, board, me, opp):
        score = 0
        # Weighting: Give much higher priority to 3-in-a-rows (traps)
        # than the original bot does.
        
        # Center column is weighted much higher for setup
        for r in range(6):
            if board[3, r] == me: score += 6
            elif board[3, r] == opp: score -= 6

        # Check all possible 4-slots (Windows)
        # Vertical
        for c in range(7):
            for r in range(3):
                score += self.score_window([board[c, r+i] for i in range(4)], me, opp)
        # Horizontal
        for r in range(6):
            for c in range(4):
                score += self.score_window([board[c+i, r] for i in range(4)], me, opp)
        # Diagonals
        for r in range(3):
            for c in range(4):
                score += self.score_window([board[c+i, r+i] for i in range(4)], me, opp)
                score += self.score_window([board[c+i, r+3-i] for i in range(4)], me, opp)

        return score

    def score_window(self, window, me, opp):
        score = 0
        my_c = window.count(me)
        opp_c = window.count(opp)
        empty = window.count(None)

        if my_c == 4: score += 10000
        elif my_c == 3 and empty == 1: score += 100 # Threatening a win
        elif my_c == 2 and empty == 2: score += 10

        if opp_c == 3 and empty == 1: score -= 500 # Major threat (Block this!)
        elif opp_c == 2 and empty == 2: score -= 50
        
        return score