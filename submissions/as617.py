from pingv4 import AbstractBot, ConnectFourBoard, CellState
import math
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, OrderedDict

class LRUCache(OrderedDict):
    """
    Least Recently Used Cache.
    Removes the least recently used key when full.
    """
    def __init__(self, maxsize: int = 128, *args, **kwargs):
        self.maxsize = maxsize
        super().__init__(*args, **kwargs)
    
    def __getitem__(self, key):
        value = super().__getitem__(key)
        self.move_to_end(key)  # Mark as recently used
        return value
    
    def __setitem__(self, key, value):
        if key in self:
            self.move_to_end(key)
        super().__setitem__(key, value)
        if len(self) > self.maxsize:
            oldest = next(iter(self))  # Get the first/oldest key
            del self[oldest]


def get_tt_entry(value: float, is_upper_bound: bool = False, is_lower_bound: bool = False) -> dict:
    """
    Create a transposition table entry.
    
    Args:
        value: The score/value to store
        is_upper_bound: True if this is an upper bound (value <= alpha)
        is_lower_bound: True if this is a lower bound (value >= beta)
        
    Returns:
        dict: Transposition table entry
    """
    return {
        'value': value,
        'UB': is_upper_bound,
        'LB': is_lower_bound
    }


class as617(AbstractBot):
    """
    Connect Four bot using LRU cache for transposition table.
    Based on the provided code structure.
    """
    
    DEPTH = 8  # Fixed search depth
    
    @property
    def strategy_name(self) -> str:
        return f"Adi Bot"
    
    @property
    def author_name(self) -> str:
        return "Aditya Singh"
    
    @property
    def author_netid(self) -> str:
        return "as617"
    
    def get_move(self, board: ConnectFourBoard) -> int:
        """
        Determine the best move using minimax with transposition table.
        """
        TT = LRUCache(maxsize=4096)  # Transposition table with LRU eviction
        
        best_score = -float('inf')
        best_move = None
        
        # Get valid moves in optimal search order
        valid_moves = board.get_valid_moves()
        ordered_moves = self.get_search_order(board, valid_moves)
        
        for move in ordered_moves:
            new_board = board.make_move(move)
            
            # Recursive search
            score = -self.recurse(new_board, self.DEPTH - 1, -float('inf'), float('inf'), TT)
            
            if score > best_score:
                best_score = score
                best_move = move
        
        # Fallback to center preference if no move found
        if best_move is None:
            for col in [3, 2, 4, 1, 5, 0, 6]:
                if col in valid_moves:
                    return col
            return valid_moves[0]
            
        return best_move
    
    def recurse(self, board: ConnectFourBoard, depth: int, alpha: float, beta: float, 
                transposition_table: LRUCache) -> float:
        """
        Recursive negamax search with alpha-beta pruning and transposition table.
        """
        alpha_original = alpha
        
        # Transposition table lookup
        board_key = board.hash
        if board_key in transposition_table:
            entry = transposition_table[board_key]
            
            if entry['LB']:  # Lower bound
                alpha = max(alpha, entry['value'])
            elif entry['UB']:  # Upper bound
                beta = min(beta, entry['value'])
            else:  # Exact value
                return entry['value']
            
            # Cut-off from transposition table
            if alpha >= beta:
                return entry['value']
        
        # Base cases
        if depth == 0 or not board.is_in_progress:
            return self.evaluate_leaf(board)
        
        # Terminal state checks
        if board.is_victory:
            return self.get_winning_score(board)
        if board.is_draw:
            return 0
        
        # Negamax search
        best_value = -float('inf')
        
        valid_moves = board.get_valid_moves()
        ordered_moves = self.get_search_order(board, valid_moves)
        
        for move in ordered_moves:
            new_board = board.make_move(move)
            
            value = -self.recurse(new_board, depth - 1, -beta, -alpha, transposition_table)
            best_value = max(best_value, value)
            
            alpha = max(alpha, best_value)
            if alpha >= beta:
                break  # Alpha-beta cutoff
        
        # Transposition table storage
        if best_value <= alpha_original:
            # Upper bound (value <= alpha)
            transposition_table[board_key] = get_tt_entry(best_value, is_upper_bound=True)
        elif best_value >= beta:
            # Lower bound (value >= beta)
            transposition_table[board_key] = get_tt_entry(best_value, is_lower_bound=True)
        else:
            # Exact value
            transposition_table[board_key] = get_tt_entry(best_value)
        
        return best_value
    
    def get_search_order(self, board: ConnectFourBoard, moves: list) -> list:
        """
        Order moves for optimal search efficiency.
        Center columns first, then outward.
        """
        center = board.num_cols // 2
        
        # Score each move
        move_scores = []
        for move in moves:
            score = 0
            
            # Center preference
            score += 10 - abs(move - center) * 2
            
            # Check for immediate win
            new_board = board.make_move(move)
            if new_board.is_victory:
                score += 1000
            
            # Check for block
            for opp_move in new_board.get_valid_moves():
                if new_board.make_move(opp_move).is_victory:
                    score += 500
                    break
            
            move_scores.append((score, move))
        
        # Sort by score descending
        move_scores.sort(key=lambda x: x[0], reverse=True)
        return [move for _, move in move_scores]
    
    def evaluate_leaf(self, board: ConnectFourBoard) -> float:
        """
        Evaluate leaf nodes (positions at depth limit).
        """
        if board.is_victory:
            return self.get_winning_score(board)
        if board.is_draw:
            return 0
        
        # Positional evaluation for non-terminal leaf nodes
        score = 0
        player = board.current_player
        opponent = CellState.Red if player == CellState.Yellow else CellState.Yellow
        
        # Simple positional evaluation
        for col in range(board.num_cols):
            for row in range(board.num_rows):
                cell = board[col, row]
                if cell == player:
                    # Center control bonus
                    if col in [2, 3, 4]:
                        score += 3
                    # Vertical stack bonus
                    if row > 0 and board[col, row-1] == player:
                        score += 2
                elif cell == opponent:
                    # Penalize opponent's center control
                    if col in [2, 3, 4]:
                        score -= 3
        
        return score
    
    def get_winning_score(self, board: ConnectFourBoard) -> float:
        """
        Get the score for a winning position.
        Positive if current player wins, negative if opponent wins.
        """
        if not board.is_victory:
            return 0
        
        # Large winning score, adjusted for depth
        winning_score = 10000
        
        if board.winner == board.current_player:
            return winning_score
        else:
            return -winning_score