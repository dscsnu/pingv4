from pingv4 import AbstractBot, ConnectFourBoard, CellState, Connect4Game, MinimaxBot, RandomBot
from typing import Dict, Tuple


class pravin_s(AbstractBot):
    """UltimateBot-Slayer - Enhanced minimax with superior scoring"""
    
    def __init__(self, color=None):
        super().__init__(color)
        self.transposition_table: Dict[int, Tuple[int, float, int]] = {}
        self.MAX_DEPTH = 7  # Depth 7 beats depth 6 bots

    @property
    def strategy_name(self) -> str:
        return "UltimateBot-Slayer-v7"
    
    @property
    def author_name(self) -> str:
        return "Pravin S" 
    
    @property
    def author_netid(self) -> str:
        return "pravin_s" 
    
    def get_move(self, board: ConnectFourBoard) -> int:
        """Find best move with la390-style approach enhanced"""
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
        
        # 3. Use enhanced minimax with depth 7
        best_col, _ = self.minimax(board, self.MAX_DEPTH, -float('inf'), float('inf'), True, me)
        return best_col
    
    def _opponent_wins_here(self, board: ConnectFourBoard, col: int, opponent: CellState) -> bool:
        """Check if opponent would win by playing at col"""
        if col not in board.get_valid_moves():
            return False
        
        row = board.column_heights[col]
        if row >= board.num_rows:
            return False
        
        # Horizontal
        count = 0
        for c in range(max(0, col-3), min(7, col+4)):
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
        for r in range(row-1, -1, -1):
            if board[col, r] == opponent:
                count += 1
            else:
                break
        if count >= 4:
            return True
        
        # Diagonal /
        count = 1
        # Down-left
        c, r = col-1, row-1
        while c >= 0 and r >= 0 and board[c, r] == opponent:
            count += 1
            c -= 1
            r -= 1
        # Up-right
        c, r = col+1, row+1
        while c < 7 and r < 6 and board[c, r] == opponent:
            count += 1
            c += 1
            r += 1
        if count >= 4:
            return True
        
        # Diagonal \
        count = 1
        # Up-left
        c, r = col-1, row+1
        while c >= 0 and r < 6 and board[c, r] == opponent:
            count += 1
            c -= 1
            r += 1
        # Down-right
        c, r = col+1, row-1
        while c < 7 and r >= 0 and board[c, r] == opponent:
            count += 1
            c += 1
            r -= 1
        if count >= 4:
            return True
        
        return False

    def minimax(self, board: ConnectFourBoard, depth: int, alpha: float,
                beta: float, is_maximizing: bool, my_color: CellState) -> Tuple[int, float]:
        """Enhanced minimax with alpha-beta pruning and transposition table"""
        
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
        
        # Move ordering: center first for better pruning
        center_order = [3, 2, 4, 1, 5, 0, 6]
        ordered_moves = [c for c in center_order if c in valid_moves]
        
        best_col = ordered_moves[0]
        
        if is_maximizing:
            max_eval = -float('inf')
            for col in ordered_moves:
                new_board = board.make_move(col)
                _, eval_score = self.minimax(new_board, depth - 1, alpha, beta, False, my_color)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_col = col
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            
            self.transposition_table[state_id] = (depth, max_eval, best_col)
            return best_col, max_eval
        else:
            min_eval = float('inf')
            for col in ordered_moves:
                new_board = board.make_move(col)
                _, eval_score = self.minimax(new_board, depth - 1, alpha, beta, True, my_color)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_col = col
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            
            self.transposition_table[state_id] = (depth, min_eval, best_col)
            return best_col, min_eval

    def score_position(self, board: ConnectFourBoard, piece: CellState) -> float:
        """Enhanced position evaluation - beats UltimateBot's scoring"""
        score = 0
        
        # Center control bonus (enhanced from 3 to 5)
        center_array = [board[3, i] for i in range(6)]
        center_count = center_array.count(piece)
        score += center_count * 5
        
        # Evaluate all windows
        # Horizontal
        for r in range(6):
            for c in range(4):
                window = [board[c+i, r] for i in range(4)]
                score += self.evaluate_window(window, piece)
        
        # Vertical
        for c in range(7):
            for r in range(3):
                window = [board[c, r+i] for i in range(4)]
                score += self.evaluate_window(window, piece)
        
        # Diagonal /
        for r in range(3):
            for c in range(4):
                window = [board[c+i, r+i] for i in range(4)]
                score += self.evaluate_window(window, piece)
        
        # Diagonal \
        for r in range(3, 6):
            for c in range(4):
                window = [board[c+i, r-i] for i in range(4)]
                score += self.evaluate_window(window, piece)
        
        return score

    def evaluate_window(self, window: list, piece: CellState) -> float:
        """Evaluate 4-cell window - Enhanced from UltimateBot's winning formula"""
        score = 0
        opp_piece = CellState.Yellow if piece == CellState.Red else CellState.Red
        
        piece_count = window.count(piece)
        empty_count = window.count(None)
        opp_count = window.count(opp_piece)
        
        # OFFENSE (enhanced scoring - better than UltimateBot)
        if piece_count == 4:
            score += 10000
        elif piece_count == 3 and empty_count == 1:
            score += 8  # UltimateBot uses 7, we use 8
        elif piece_count == 2 and empty_count == 2:
            score += 4  # UltimateBot uses 3, we use 4
        elif piece_count == 1 and empty_count == 3:
            score += 1
        
        # DEFENSE - CRITICAL (stronger than UltimateBot's -90)
        if opp_count == 3 and empty_count == 1:
            score -= 100  # Even more aggressive than UltimateBot's -90!
        elif opp_count == 2 and empty_count == 2:
            score -= 4  # Enhanced from UltimateBot's -3
        
        return score
