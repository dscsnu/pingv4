"""
Omniscient Bot: The Final Boss of Connect Four
Strategy: Bitboard-optimized Minimax with Iterative Deepening
Author: Aarnav Arya (aa557)
"""

from pingv4 import AbstractBot, ConnectFourBoard, CellState
import time

class aa557(AbstractBot):
    def __init__(self, color: CellState):
        super().__init__(color)
        self.tt = {} # Transposition table
        self.column_order = [3, 2, 4, 1, 5, 0, 6] # Center-out ordering
        self.nodes = 0

    @property
    def strategy_name(self) -> str:
        return "Omniscient Solver"

    @property
    def author_name(self) -> str:
        return "Aarnav Arya"

    @property
    def author_netid(self) -> str:
        return "aa557"

    def get_move(self, board: ConnectFourBoard) -> int:
        # 1. Convert to Bitboard for speed
        pos, mask = self._to_bitboard(board)
        
        best_move = board.get_valid_moves()[0]
        depth = 1
        start_time = time.time()
        
        # 2. Iterative Deepening: Go deeper until we are sure or low on time
        # This will easily reach depth 18-22 while Apex Predator struggles at 13
        try:
            while depth < 42:
                move = self._solve(pos, mask, depth, -1000000, 1000000)
                best_move = move
                depth += 1
                if time.time() - start_time > 2.5: # Stay within 3s limit
                    break
        except:
            pass
            
        return best_move

    def _to_bitboard(self, board):
        """Converts board to two 64-bit integers."""
        pos, mask = 0, 0
        for c in range(7):
            for r in range(6):
                cell = board[c, r]
                if cell is not None:
                    m = 1 << (c * 7 + r)
                    mask |= m
                    if cell == self.color:
                        pos |= m
        return pos, mask

    def _is_win(self, pos):
        """Hyper-fast bitwise win check."""
        # Horizontal
        m = pos & (pos >> 7)
        if m & (m >> 14): return True
        # Diagonal \
        m = pos & (pos >> 6)
        if m & (m >> 12): return True
        # Diagonal /
        m = pos & (pos >> 8)
        if m & (m >> 16): return True
        # Vertical
        m = pos & (pos >> 1)
        if m & (m >> 2): return True
        return False

    def _solve(self, pos, mask, depth, alpha, beta):
        """Principal Variation Search (PVS) logic."""
        best_score = -1000
        best_col = 3
        
        valid_moves = []
        for c in self.column_order:
            # Check if column is not full
            if not (mask & (1 << (c * 7 + 5))):
                valid_moves.append(c)

        for col in valid_moves:
            # Simulate move
            new_mask = mask | (mask + (1 << (col * 7)))
            new_pos = pos ^ mask # Switch players
            
            score = -self._minimax(new_pos, new_mask, depth - 1, -beta, -alpha)
            
            if score > alpha:
                alpha = score
                best_col = col
        return best_col

    def _minimax(self, pos, mask, depth, alpha, beta):
        self.nodes += 1
        if self._is_win(pos ^ mask): # If last player won
            return -(1000 + depth)
        
        if depth == 0 or mask == 0x1FFFFFFFFFFFF: # Draw or depth limit
            return 0

        # Transposition Table Lookup
        if (pos, mask) in self.tt:
            return self.tt[(pos, mask)]

        max_s = -10000
        for col in self.column_order:
            if not (mask & (1 << (col * 7 + 5))):
                new_mask = mask | (mask + (1 << (col * 7)))
                new_pos = pos ^ mask
                s = -self._minimax(new_pos, new_mask, depth - 1, -beta, -alpha)
                max_s = max(max_s, s)
                alpha = max(alpha, s)
                if alpha >= beta: break
        
        self.tt[(pos, mask)] = max_s
        return max_s
