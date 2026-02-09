"""
You can follow this template for your Connect4 bot.
Copy this and rename it to: yourname_yournetid.py
"""
"""
Akshaj's Hybrid Strategic Minimax Bot
Author: Akshaj (as637)

Strategy:
- Fast tactical checks for obvious moves (wins, blocks, forks)
- Deep minimax search (depth 6) for strategic planning
- Alpha-beta pruning and transposition tables for efficiency
"""
import time
from pingv4 import AbstractBot, ConnectFourBoard,CellState

class as637(AbstractBot):
  """
  This will be your Connect4 bot.
  CHANGE THE CLASS NAME TO your snu net id.
  """

  def __init__(self, color):
    super().__init__(color)   
    self.transposition_table = {}
    self.killer_moves = [[None, None] for _ in range(20)]
    self.MAX_DEPTH = 8
    self.time_limit = 5.0

  
  @property
  def strategy_name(self) -> str:
    return "Strategic MiniMax"

  @property
  def author_name(self) -> str:
    return "Akshaj Singh"

  @property
  def author_netid(self) -> str:
    return "as637@snu.edu.in"
  

  
 
    

  def get_move(self, board: ConnectFourBoard) -> int:
    """Main decision function"""
    valid_moves = board.get_valid_moves()
    
    # Opening book
    move_count = sum(board.column_heights)
    if move_count == 0:
      return 3
    elif move_count == 1:
      return 2 if board[3, 0] is not None else 3
    
    # Layer 1: Immediate win or forced win (early game only)
    if move_count < 14:
      win_move = self.find_winning_move(board, valid_moves)
      if win_move is not None:
        return win_move
    else:
      # Late game: only check direct wins
      for move in valid_moves:
        future_board = board.make_move(move)
        if future_board.is_victory and future_board.winner == board.current_player:
          return move
    
    # Layer 2: Block opponent's win
    block_move = self.find_blocking_move(board, valid_moves)
    if block_move is not None:
      return block_move
    
    # Layer 3: Create fork
    fork_move = self.find_fork_move(board, valid_moves)
    if fork_move is not None:
      return fork_move
    
    # Layer 4: Iterative deepening minimax
    return self.minimax_search(board, valid_moves)
  
  # ===== TACTICAL LAYERS =====
  
  def find_winning_move(self, board: ConnectFourBoard, valid_moves: list[int]) -> int | None:
    """Find immediate winning move or forced win"""
    # Direct wins
    for move in valid_moves:
      future_board = board.make_move(move)
      if future_board.is_victory and future_board.winner == board.current_player:
        return move
    
    # Forced wins
    forced_win = self.find_forced_win(board, valid_moves)
    if forced_win is not None:
      return forced_win
    
    return None
  
  def find_forced_win(self, board: ConnectFourBoard, valid_moves: list[int]) -> int | None:
    """Find moves that force opponent into losing position"""
    for move in valid_moves:
      future = board.make_move(move)
      if not future.is_in_progress:
        continue
      
      opponent_moves = future.get_valid_moves()
      all_responses_lose = True
      
      for opp_move in opponent_moves:
        opp_future = future.make_move(opp_move)
        if not opp_future.is_in_progress:
          all_responses_lose = False
          break
        
        we_can_win = False
        for our_next in opp_future.get_valid_moves():
          if opp_future.make_move(our_next).is_victory:
            we_can_win = True
            break
        
        if not we_can_win:
          all_responses_lose = False
          break
      
      if all_responses_lose and len(opponent_moves) > 0:
        return move
    
    return None
  
  def find_blocking_move(self, board: ConnectFourBoard, valid_moves: list[int]) -> int | None:
    """Block opponent's immediate win"""
    opponent = self.get_opponent_color(board.current_player)
    
    for move in valid_moves:
      future_board = board.make_move(move)
      if not future_board.is_in_progress:
        continue
      
      for opponent_move in future_board.get_valid_moves():
        opponent_future = future_board.make_move(opponent_move)
        if opponent_future.is_victory and opponent_future.winner == opponent:
          return opponent_move
    
    return None
  
  def find_fork_move(self, board: ConnectFourBoard, valid_moves: list[int]) -> int | None:
    """Find move that creates 2+ winning threats"""
    for move in valid_moves:
      future_board = board.make_move(move)
      if not future_board.is_in_progress:
        continue
      
      winning_moves_count = 0
      for next_move in future_board.get_valid_moves():
        next_future = future_board.make_move(next_move)
        if next_future.is_victory and next_future.winner == board.current_player:
          winning_moves_count += 1
          if winning_moves_count >= 2:
            return move
    
    return None
  
  # ===== MINIMAX WITH ITERATIVE DEEPENING =====
  
  def minimax_search(self, board: ConnectFourBoard, valid_moves: list[int]) -> int:
    """Iterative deepening minimax search"""
    start_time = time.time()
    best_move = None
    
    for current_depth in range(1, self.MAX_DEPTH + 1):
      if time.time() - start_time > self.time_limit * 0.9:
        break
      
      depth_best_move = None
      best_score = float('-inf')
      alpha = float('-inf')
      beta = float('inf')
      
      ordered_moves = self.order_moves(valid_moves, 0)
      
      for move in ordered_moves:
        if time.time() - start_time > self.time_limit * 0.9:
          break
        
        future_board = board.make_move(move)
        score = -self.minimax(future_board, current_depth - 1, -beta, -alpha, start_time, 1)
        
        if score > best_score:
          best_score = score
          depth_best_move = move
        
        alpha = max(alpha, score)
        if alpha >= beta:
          break
      
      if depth_best_move is not None:
        best_move = depth_best_move
      
      if best_score > 900:
        break
    
    return best_move if best_move is not None else valid_moves[0]
  
  def minimax(self, board: ConnectFourBoard, depth: int, alpha: float, beta: float, start_time: float, ply: int) -> float:
    """Recursive minimax with all optimizations"""
    # Time cutoff
    if time.time() - start_time > self.time_limit * 0.9:
      return self.evaluate_position(board)
    
    # Check cache
    board_hash = board.hash
    if board_hash in self.transposition_table:
      cached_depth, cached_score = self.transposition_table[board_hash]
      if cached_depth >= depth:
        return cached_score
    
    # Terminal states
    if not board.is_in_progress:
      if board.is_victory:
        score = -1000 - depth
      else:
        score = 0
      self.transposition_table[board_hash] = (depth, score)
      return score
    
    if depth == 0:
      score = self.evaluate_position(board)
      self.transposition_table[board_hash] = (depth, score)
      return score
    
    # Recursive search
    max_score = float('-inf')
    ordered_moves = self.order_moves(board.get_valid_moves(), ply)
    
    for move in ordered_moves:
      if time.time() - start_time > self.time_limit * 0.9:
        break
      
      future_board = board.make_move(move)
      score = -self.minimax(future_board, depth - 1, -beta, -alpha, start_time, ply + 1)
      
      if score > max_score:
        max_score = score
      
      alpha = max(alpha, score)
      
      if alpha >= beta:
        # Store killer move
        if ply < len(self.killer_moves):
          if move != self.killer_moves[ply][0]:
            self.killer_moves[ply][1] = self.killer_moves[ply][0]
            self.killer_moves[ply][0] = move
        break
    
    self.transposition_table[board_hash] = (depth, max_score)
    return max_score
  
  def order_moves(self, moves: list[int], depth: int = 0) -> list[int]:
    """Enhanced move ordering with killer moves"""
    move_scores = []
    
    for move in moves:
      score = 0
      
      # Killer move bonus
      if depth < len(self.killer_moves):
        if move == self.killer_moves[depth][0]:
          score += 1000
        elif move == self.killer_moves[depth][1]:
          score += 900
      
      # Center preference
      priority_order = [3, 2, 4, 1, 5, 0, 6]
      score += (10 - priority_order.index(move)) * 10
      
      move_scores.append((score, move))
    
    move_scores.sort(reverse=True, key=lambda x: x[0])
    return [move for score, move in move_scores]
  
  # ===== ENHANCED EVALUATION =====
  
  def evaluate_position(self, board: ConnectFourBoard) -> float:
    """Enhanced position evaluation"""
    current_player = board.current_player
    opponent = self.get_opponent_color(current_player)
    
    score = 0.0
    
    # Threat counting
    our_threats = self.evaluate_threats(board, current_player)
    their_threats = self.evaluate_threats(board, opponent)
    score += our_threats - their_threats
    
    # Center control
    for row in range(board.num_rows):
      if board[3, row] == current_player:
        score += 6
      elif board[3, row] == opponent:
        score -= 6
    
    # Near-center control
    for col in [2, 4]:
      for row in range(board.num_rows):
        if board[col, row] == current_player:
          score += 2
        elif board[col, row] == opponent:
          score -= 2
    
    # Connectivity
    score += self.evaluate_connectivity(board, current_player) * 2
    score -= self.evaluate_connectivity(board, opponent) * 2
    
    # Height advantage
    for col in range(board.num_cols):
      height = board.column_heights[col]
      for row in range(height):
        if board[col, row] == current_player:
          score += (6 - row) * 0.5
        elif board[col, row] == opponent:
          score -= (6 - row) * 0.5
    
    # Parity
    score += self.evaluate_parity(board, current_player)
    
    return score
  
  def evaluate_threats(self, board: ConnectFourBoard, player: CellState) -> float:
    """Count potential winning lines"""
    score = 0.0
    
    # Horizontal
    for row in range(board.num_rows):
      for col in range(board.num_cols - 3):
        window = [board[col + i, row] for i in range(4)]
        score += self.score_window(window, player)
    
    # Vertical
    for col in range(board.num_cols):
      for row in range(board.num_rows - 3):
        window = [board[col, row + i] for i in range(4)]
        score += self.score_window(window, player)
    
    # Diagonal /
    for row in range(board.num_rows - 3):
      for col in range(board.num_cols - 3):
        window = [board[col + i, row + i] for i in range(4)]
        score += self.score_window(window, player)
    
    # Diagonal \
    for row in range(3, board.num_rows):
      for col in range(board.num_cols - 3):
        window = [board[col + i, row - i] for i in range(4)]
        score += self.score_window(window, player)
    
    return score
  
  def score_window(self, window: list, player: CellState) -> float:
    """Score a 4-cell window"""
    opponent = self.get_opponent_color(player)
    
    player_count = window.count(player)
    empty_count = window.count(None)
    opponent_count = window.count(opponent)
    
    if opponent_count > 0:
      return 0
    
    if player_count == 4:
      return 100
    elif player_count == 3 and empty_count == 1:
      return 10
    elif player_count == 2 and empty_count == 2:
      return 3
    elif player_count == 1 and empty_count == 3:
      return 1
    
    return 0
  
  def evaluate_connectivity(self, board: ConnectFourBoard, player: CellState) -> float:
    """Bonus for connected pieces"""
    score = 0.0
    
    # Horizontal
    for row in range(board.num_rows):
      for col in range(board.num_cols - 1):
        if board[col, row] == player and board[col + 1, row] == player:
          score += 1
    
    # Vertical
    for col in range(board.num_cols):
      for row in range(board.num_rows - 1):
        if board[col, row] == player and board[col, row + 1] == player:
          score += 1
    
    # Diagonals
    for row in range(board.num_rows - 1):
      for col in range(board.num_cols - 1):
        if board[col, row] == player and board[col + 1, row + 1] == player:
          score += 1
        if row > 0 and board[col, row] == player and board[col + 1, row - 1] == player:
          score += 1
    
    return score
  
  def evaluate_parity(self, board: ConnectFourBoard, player: CellState) -> float:
    """Odd/even strategy"""
    score = 0.0
    is_first_player = (player == CellState.Red)
    
    for col in range(board.num_cols):
      height = board.column_heights[col]
      remaining_spaces = board.num_rows - height
      
      if remaining_spaces > 0:
        next_row = height
        is_odd_row = (next_row % 2 == 0)
        
        if is_first_player and is_odd_row:
          score += 0.5
        elif not is_first_player and not is_odd_row:
          score += 0.5
    
    return score
  
  # ===== HELPER =====
  
  def get_opponent_color(self, current_player: CellState) -> CellState:
    """Get opponent's color"""
    return CellState.Yellow if current_player == CellState.Red else CellState.Red