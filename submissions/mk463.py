"""
You can follow this template for your Connect4 bot.
Copy this and rename it to: yourname_yournetid.py
"""

from pingv4 import AbstractBot, ConnectFourBoard

import copy

import copy

class mk463(AbstractBot):
    @property
    def strategy_name(self) -> str:
        return "Guardian Negamax V3"

    @property
    def author_name(self) -> str:
        return "Mridhula"

    @property
    def author_netid(self) -> str:
        return "mk463"

    def get_move(self, board) -> int:
        # 1. Identify players
        self.player_id = board.current_player
        self.opp_id = 1 if self.player_id == 2 else 2
        
        valid_moves = board.get_valid_moves()
        if not valid_moves: return 0

        # --- 2. EMERGENCY CHECKS (Win & Block) ---
        for move in valid_moves:
            if self._predict_win(board, move, self.player_id):
                return move
        for move in valid_moves:
            if self._predict_win(board, move, self.opp_id):
                return move

        # --- 3. MINIMAX ---
        target_depth = 4 # Kept at 4 because deepcopying is slower than cloning
        best_move = valid_moves[0]
        best_score = -float('inf')
        alpha = -float('inf')
        beta = float('inf')

        # Center-out ordering
        center = board.width // 2
        ordered_moves = sorted(valid_moves, key=lambda x: abs(x - center))

        for move in ordered_moves:
            temp_board = copy.deepcopy(board) # The fix for no .clone()
            temp_board.make_move(move)
            score = self._minimax(temp_board, target_depth - 1, alpha, beta, False)
            
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)
            
        return best_move

    def _predict_win(self, board, move, player):
        """Checks for immediate win without ruining the original board."""
        temp = copy.deepcopy(board)
        temp.current_player = player 
        temp.make_move(move)
        return self._check_win(temp, player)

    def _minimax(self, board, depth, alpha, beta, maximizing_player):
        if self._check_win(board, self.player_id): return 1000000
        if self._check_win(board, self.opp_id): return -1000000
        
        valid_moves = board.get_valid_moves()
        if depth == 0 or not valid_moves:
            return self._evaluate_position(board)

        center = board.width // 2
        ordered_moves = sorted(valid_moves, key=lambda x: abs(x - center))

        if maximizing_player:
            value = -float('inf')
            for move in ordered_moves:
                temp = copy.deepcopy(board)
                temp.make_move(move)
                value = max(value, self._minimax(temp, depth - 1, alpha, beta, False))
                alpha = max(alpha, value)
                if alpha >= beta: break
            return value
        else:
            value = float('inf')
            for move in ordered_moves:
                temp = copy.deepcopy(board)
                temp.make_move(move)
                value = min(value, self._minimax(temp, depth - 1, alpha, beta, True))
                beta = min(beta, value)
                if beta <= alpha: break
            return value

    def _evaluate_position(self, board) -> int:
        score = 0
        # Center column bias
        center_col = board.width // 2
        for r in range(board.height):
            if board.grid[r][center_col] == self.player_id: score += 15
            elif board.grid[r][center_col] == self.opp_id: score -= 15

        # Check Windows
        # Horizontal
        for r in range(board.height):
            for c in range(board.width - 3):
                score += self._score_window(board.grid[r][c:c+4])
        # Vertical
        for c in range(board.width):
            for r in range(board.height - 3):
                window = [board.grid[r+i][c] for i in range(4)]
                score += self._score_window(window)
        # Diagonals
        for r in range(board.height - 3):
            for c in range(board.width - 3):
                p_diag = [board.grid[r+i][c+i] for i in range(4)]
                n_diag = [board.grid[r+3-i][c+i] for i in range(4)]
                score += self._score_window(p_diag)
                score += self._score_window(n_diag)
        return score

    def _score_window(self, window) -> int:
        score = 0
        me, opp, empty = window.count(self.player_id), window.count(self.opp_id), window.count(0)

        if me == 3 and empty == 1: score += 100
        elif me == 2 and empty == 2: score += 10
        if opp == 3 and empty == 1: score -= 600 # Higher penalty for opponent threats
        elif opp == 2 and empty == 2: score -= 50
        return score

    def _check_win(self, board, player) -> bool:
        # Standard Win Check
        for r in range(board.height):
            for c in range(board.width - 3):
                if all(board.grid[r][c+i] == player for i in range(4)): return True
        for c in range(board.width):
            for r in range(board.height - 3):
                if all(board.grid[r+i][c] == player for i in range(4)): return True
        for r in range(board.height - 3):
            for c in range(board.width - 3):
                if all(board.grid[r+i][c+i] == player for i in range(4)): return True
                if all(board.grid[r+3-i][c+i] == player for i in range(4)): return True
        return False