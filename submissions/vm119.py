import math
import random
from pingv4 import AbstractBot, ConnectFourBoard, CellState

class vm119(AbstractBot):

    @property
    def strategy_name(self):
        return "vyusti's goated bot"

    @property
    def author_name(self):
        return "vyusti"

    @property
    def author_netid(self):
        return "vm119"

    def get_move(self, board: ConnectFourBoard) -> int:
        valid_moves = board.get_valid_moves()
        
        # Identify who we are and who the enemy is
        me = board.current_player
        opp = CellState.Yellow if me == CellState.Red else CellState.Red

        # ----------------------------------------
        # PHASE 1: CAN I WIN NOW? (Checkmate)
        # ----------------------------------------
        for col in valid_moves:
            # The API says make_move returns a NEW board. 
            next_board = board.make_move(col)
            if next_board.is_victory:
                return col

        # ----------------------------------------
        # PHASE 2: MUST I BLOCK? (Survival)
        # ----------------------------------------
        # We manually check if the opponent has a winning move at any valid column.
        # Since we can't "make_move" as the opponent on the current board,
        # we calculate it manually using the board accessor board[c, r].
        for col in valid_moves:
            row = board.column_heights[col] # The row where the piece would land
            if self.check_manual_win(board, col, row, opp):
                return col

        # ----------------------------------------
        # PHASE 3: MINIMAX (Look Ahead)
        # ----------------------------------------
        # If we are safe, use Minimax to find the best strategic move.
        try:
            # Depth 4 is a good balance of speed and intelligence
            best_col, _ = self.minimax(board, 4, -math.inf, math.inf, True, me, opp)
            if best_col is not None:
                return best_col
        except Exception as e:
            print(f"Minimax Error: {e}")
            
        # Fallback: Prefer center
        center_order = [3, 2, 4, 1, 5, 0, 6]
        for c in center_order:
            if c in valid_moves: return c
        return valid_moves[0]

    def check_manual_win(self, board, col, row, color):
        """
        Manually checks if placing 'color' at (col, row) creates a line of 4.
        """
        # Directions: (dx, dy) -> Horizontal, Vertical, Diag1, Diag2
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            count = 1 # Start with 1 for the piece we are imagining placing
            
            # Check Positive Direction
            for i in range(1, 4):
                c, r = col + dx*i, row + dy*i
                if 0 <= c < 7 and 0 <= r < 6 and board[c, r] == color:
                    count += 1
                else:
                    break
            
            # Check Negative Direction
            for i in range(1, 4):
                c, r = col - dx*i, row - dy*i
                if 0 <= c < 7 and 0 <= r < 6 and board[c, r] == color:
                    count += 1
                else:
                    break
            
            if count >= 4:
                return True
        return False

    def minimax(self, board, depth, alpha, beta, maximizing, me, opp):
        valid_moves = board.get_valid_moves()
        
        # Terminal checks
        if board.is_victory:
            # Note: If is_victory is true, the PREVIOUS player won.
            # If we are "maximizing" now, it means the Opponent (min) just moved and won.
            return (None, -100000 if maximizing else 100000)
        if board.is_draw or depth == 0:
            return (None, self.evaluate_board(board, me, opp))

        # Move Ordering: Center first makes it faster
        center = 3
        valid_moves.sort(key=lambda x: abs(x - center))

        if maximizing:
            max_eval = -math.inf
            best_col = random.choice(valid_moves)
            for col in valid_moves:
                next_board = board.make_move(col)
                # Pass False because next turn is opponent (minimizing)
                _, eval = self.minimax(next_board, depth-1, alpha, beta, False, me, opp)
                
                if eval > max_eval:
                    max_eval = eval
                    best_col = col
                alpha = max(alpha, eval)
                if beta <= alpha: break
            return best_col, max_eval
        else:
            min_eval = math.inf
            best_col = random.choice(valid_moves)
            for col in valid_moves:
                next_board = board.make_move(col)
                # Pass True because next turn is Us (maximizing)
                _, eval = self.minimax(next_board, depth-1, alpha, beta, True, me, opp)
                
                if eval < min_eval:
                    min_eval = eval
                    best_col = col
                beta = min(beta, min_eval)
                if beta <= alpha: break
            return best_col, min_eval

    def evaluate_board(self, board, me, opp):
        score = 0
        
        # 1. Center Control (Very important in Connect 4)
        center_col = 3
        # Count pieces in center column
        center_count = 0
        for r in range(6):
            if board[center_col, r] == me: center_count += 1
        score += center_count * 3

        # 2. Window Evaluation
        # We scan every 4-cell window on the board
        
        # Horizontal Windows
        for c in range(4): # 0 to 3
            for r in range(6):
                window = [board[c+i, r] for i in range(4)]
                score += self.evaluate_window(window, me, opp)
                
        # Vertical Windows
        for c in range(7):
            for r in range(3): # 0 to 2
                window = [board[c, r+i] for i in range(4)]
                score += self.evaluate_window(window, me, opp)
                
        # Positive Diagonal
        for c in range(4):
            for r in range(3):
                window = [board[c+i, r+i] for i in range(4)]
                score += self.evaluate_window(window, me, opp)
                
        # Negative Diagonal
        for c in range(4):
            for r in range(3, 6):
                window = [board[c+i, r-i] for i in range(4)]
                score += self.evaluate_window(window, me, opp)

        return score

    def evaluate_window(self, window, me, opp):
        score = 0
        # Count our pieces and their pieces in this window
        my_count = window.count(me)
        opp_count = window.count(opp)
        empty_count = window.count(None)

        if my_count == 4:
            score += 100
        elif my_count == 3 and empty_count == 1:
            score += 5
        elif my_count == 2 and empty_count == 2:
            score += 2

        if opp_count == 3 and empty_count == 1:
            score -= 4 # Opponent has a strong threat
            
        return score