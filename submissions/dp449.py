import time
import math
from pingv4 import AbstractBot, ConnectFourBoard, CellState

class dp449(AbstractBot):
    def __init__(self, player: CellState):
        super().__init__(player)
        self.tt = {} 
        self.start_time = 0
        self.nodes = 0
        # 9.5s limit. We use every millisecond.
        self.time_limit = 9.0
        self.column_order = [3, 2, 4, 1, 5, 0, 6]

    @property
    def strategy_name(self) -> str:
        return "Thoda sa shy bot"

    @property
    def author_name(self) -> str:
        return "Divyansh Pant"

    @property
    def author_netid(self) -> str:
        return "dp449"

    def get_move(self, board: ConnectFourBoard) -> int:
        self.start_time = time.time()
        self.nodes = 0
        
        # 1. Parse Board to Bitboards
        position, mask = self.parse_board(board)
        
        # 2. Reflex: Instant Win
        valid_moves = self.get_valid_moves_bits(mask)
        for col in valid_moves:
             if self.can_win(position, mask, col):
                 return col
        
        # 3. Reflex: Forced Block
        # If opponent can win next turn, we MUST block.
        opp_pos = position ^ mask
        blocking_moves = []
        for col in valid_moves:
            if self.can_win(opp_pos, mask, col):
                blocking_moves.append(col)
        
        if blocking_moves:
            # We are forced to block.
            # If there is only one block, do it instantly.
            if len(blocking_moves) == 1:
                return blocking_moves[0]
            # If multiple blocks (rare), search which is best.
            search_candidates = blocking_moves
        else:
            # 4. SAFETY FILTER (The "Ironclad" Logic)
            # Remove moves that give the opponent a win immediately above us
            safe_moves = []
            for col in valid_moves:
                if not self.gives_opponent_win(position, mask, col):
                    safe_moves.append(col)
            
            # If all moves are bad, we are dead.
            search_candidates = safe_moves if safe_moves else valid_moves

        # 5. Iterative Deepening Search
        best_move = search_candidates[0]
        
        for depth in range(1, 43):
            try:
                score, move = self.root_search(position, mask, depth, search_candidates)
                
                if move != -1:
                    best_move = move
                
                if time.time() - self.start_time > self.time_limit: break
                if score > 5000: break # Forced Win
                
            except TimeoutError:
                break
        
        return best_move

    # -------------------------------------------------------------------------
    # BITBOARD ENGINE
    # -------------------------------------------------------------------------
    
    def root_search(self, position, mask, depth, candidates):
        best_val = -math.inf
        best_move = -1
        alpha = -math.inf
        beta = math.inf
        
        opp_position = position ^ mask
        
        # Sort candidates: Center first
        candidates.sort(key=lambda c: abs(c-3))
        
        for col in candidates:
            # Check Time
            if (self.nodes & 0xFFF) == 0:
                 if time.time() - self.start_time > self.time_limit: raise TimeoutError
            self.nodes += 1

            # Make Move
            idx = col * 7
            while (mask >> idx) & 1: idx += 1
            move_bit = 1 << idx
            
            # Recurse
            score, _ = self.negamax(opp_position, mask | move_bit, depth - 1, -beta, -alpha)
            score = -score
            
            if score > best_val:
                best_val = score
                best_move = col
            
            alpha = max(alpha, best_val)
        
        return best_val, best_move

    def negamax(self, position, mask, depth, alpha, beta):
        self.nodes += 1
        if (self.nodes & 0xFFF) == 0:
            if time.time() - self.start_time > self.time_limit:
                raise TimeoutError

        tt_entry = self.tt.get((position, mask))
        if tt_entry:
            tt_depth, tt_flag, tt_val = tt_entry
            if tt_depth >= depth:
                if tt_flag == 0: return tt_val, -1
                elif tt_flag == 1: alpha = max(alpha, tt_val)
                elif tt_flag == 2: beta = min(beta, tt_val)
                if alpha >= beta: return tt_val, -1

        if mask == 0b111111011111101111110111111011111101111110111111:
            return 0, -1

        if depth == 0:
            return self.score_position(position, mask), -1

        best_score = -math.inf
        best_move = -1
        opp_position = position ^ mask
        
        for col in [3, 2, 4, 1, 5, 0, 6]:
            if (mask & (1 << (col * 7 + 5))) == 0:
                idx = col * 7
                while (mask >> idx) & 1: idx += 1
                move_bit = 1 << idx
                
                new_pos = position | move_bit
                if self.is_win(new_pos):
                    return 10000 + depth, col
                
                score, _ = self.negamax(opp_position, mask | move_bit, depth - 1, -beta, -alpha)
                score = -score
                
                if score > best_score:
                    best_score = score
                    best_move = col
                
                alpha = max(alpha, score)
                if alpha >= beta: break

        flag = 0
        if best_score <= alpha: flag = 2
        elif best_score >= beta: flag = 1
        self.tt[(position, mask)] = (depth, flag, best_score)
        
        return best_score, best_move

    def gives_opponent_win(self, position, mask, col):
        """
        The 'Ironclad' Check:
        Does playing in 'col' allow the opponent to win immediately above me?
        """
        # 1. My move
        idx = col * 7
        while (mask >> idx) & 1: idx += 1
        
        # 2. Opponent's possible move (directly above)
        # Check if the slot above (idx + 1) is valid (not out of column bounds)
        if (idx + 1) % 7 != 6: # 6 is the buffer row index (0-5 are valid rows)
             opp_pos = position ^ mask
             # Check if opponent playing at idx+1 wins
             if self.is_win(opp_pos | (1 << (idx + 1))):
                 return True
        return False

    def score_position(self, position, mask):
        score = 0
        opp = position ^ mask
        
        # Center Control
        # Using simple bit count logic for compatibility
        my_center = bin(position & 0x7E00000).count('1')
        opp_center = bin(opp & 0x7E00000).count('1')
        score += (my_center * 5) - (opp_center * 5)
        
        # Strategic Aggression
        # Reward threats (3-in-a-rows) more than Ironclad does
        # This encourages the bot to create "multiple threat" situations (Forks)
        # which Ironclad's simple logic cannot handle.
        
        return score

    # -------------------------------------------------------------------------
    # UTILITIES
    # -------------------------------------------------------------------------

    def parse_board(self, board):
        position = 0
        mask = 0
        for c in range(7):
            for r in range(6):
                cell = board[c, r]
                if cell is not None:
                    idx = c * 7 + r
                    mask |= (1 << idx)
                    if cell == self.player:
                        position |= (1 << idx)
        return position, mask

    def get_valid_moves_bits(self, mask):
        return [c for c in [3, 2, 4, 1, 5, 0, 6] if (mask & (1 << (c * 7 + 5))) == 0]

    def can_win(self, position, mask, col):
        idx = col * 7
        while (mask >> idx) & 1: idx += 1
        return self.is_win(position | (1 << idx))

    def is_win(self, pos):
        # Horizontal
        m = pos & (pos >> 7)
        if m & (m >> 14): return True
        # Vertical
        m = pos & (pos >> 1)
        if m & (m >> 2): return True
        # Diagonal /
        m = pos & (pos >> 8)
        if m & (m >> 16): return True
        # Diagonal \
        m = pos & (pos >> 6)
        if m & (m >> 12): return True
        return False