from pingv4 import AbstractBot, ConnectFourBoard, CellState
import math


class as770(AbstractBot):
    def __init__(self, player: CellState):
        super().__init__(player)
        # Opening book: known strong opening moves
        self.opening_book = {
            # First move: always center (proven best)
            0: 3,
        }
        self.move_count = 0

    @property
    def strategy_name(self) -> str:
        return "Pigeon"

    @property
    def author_name(self) -> str:
        return "Arinjay Singh"

    @property
    def author_netid(self) -> str:
        return "as770"

    def get_move(self, board: ConnectFourBoard) -> int:
        """Return optimal move."""
        valid_moves = board.get_valid_moves()
        my_color = board.current_player
        enemy_color = (
            CellState.Red if my_color == CellState.Yellow else CellState.Yellow
        )

        # Count total pieces to track game phase
        total_pieces = sum(board.column_heights)

        # Use opening book for first move if we're Red
        if total_pieces == 0 and my_color == CellState.Red:
            return 3  # Center is mathematically optimal

        # IMMEDIATE WIN
        for move in valid_moves:
            if board.make_move(move).is_victory:
                return move

        # IMMEDIATE BLOCK
        for move in valid_moves:
            row = board.column_heights[move]
            if self.creates_win(board, move, row, enemy_color):
                return move

        # TACTICAL: Find winning setups (double threats, forks)
        tactical_move = self.find_winning_setup(
            board, valid_moves, my_color, enemy_color
        )
        if tactical_move is not None:
            return tactical_move

        # AVOID TRAPS: Don't give opponent winning positions
        safe_moves = self.eliminate_losing_moves(
            board, valid_moves, my_color, enemy_color
        )
        if safe_moves:
            valid_moves = safe_moves
        else:
            # All moves are bad - pick least bad
            return self.pick_defensive_move(board, valid_moves, my_color, enemy_color)

        # DEEP SEARCH: Variable depth based on game phase
        depth = self.calculate_search_depth(board, total_pieces)

        try:
            best_move, best_score = self.negamax_search(
                board, depth, -math.inf, math.inf, my_color, enemy_color
            )
            if best_move is not None:
                return best_move
        except Exception as e:
            print(f"Search error: {e}")

        # FALLBACK: Intelligent default
        return self.smart_fallback(valid_moves, board, my_color)

    def calculate_search_depth(self, board, total_pieces):
        """Adaptive depth: deeper in endgame, shallower in opening."""
        if total_pieces < 10:
            return 7  # Opening: moderate depth
        elif total_pieces < 25:
            return 8  # Midgame: deeper
        else:
            return 10  # Endgame: search to completion if possible

    def creates_win(self, board, col, row, player):
        """Check if move creates 4-in-a-row."""
        for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            count = 1
            for i in range(1, 4):
                c, r = col + dx * i, row + dy * i
                if 0 <= c < 7 and 0 <= r < 6 and board[c, r] == player:
                    count += 1
                else:
                    break
            for i in range(1, 4):
                c, r = col - dx * i, row - dy * i
                if 0 <= c < 7 and 0 <= r < 6 and board[c, r] == player:
                    count += 1
                else:
                    break
            if count >= 4:
                return True
        return False

    def find_winning_setup(self, board, valid_moves, my_color, enemy_color):
        """
        Find moves that create unstoppable threats:
        - Double threats (two ways to win next turn)
        - Forced sequences
        """
        for move in valid_moves:
            temp = board.make_move(move)
            if temp.is_victory:
                continue

            # Count winning opportunities we create
            win_count = 0
            for next_move in temp.get_valid_moves():
                if temp.make_move(next_move).is_victory:
                    win_count += 1

            # Two or more wins = opponent can't block both
            if win_count >= 2:
                return move

            # Check if we create a forced win sequence (zugzwang)
            if self.creates_zugzwang(temp, my_color, enemy_color):
                return move

        return None

    def creates_zugzwang(self, board, my_color, enemy_color):
        """Check if position forces opponent into losing situation."""
        # Simple check: do we have multiple threats?
        threats = 0
        for move in board.get_valid_moves():
            temp = board.make_move(move)
            if temp.is_victory:
                threats += 1
        return threats >= 2

    def eliminate_losing_moves(self, board, valid_moves, my_color, enemy_color):
        """Remove moves that lead to immediate loss."""
        safe = []
        for move in valid_moves:
            temp = board.make_move(move)

            # Does opponent win immediately?
            loses_immediately = False
            for opp_move in temp.get_valid_moves():
                if temp.make_move(opp_move).is_victory:
                    loses_immediately = True
                    break

            # Does this give opponent a double threat?
            if not loses_immediately:
                opp_threats = 0
                for opp_move in temp.get_valid_moves():
                    opp_temp = temp.make_move(opp_move)
                    if opp_temp.is_victory:
                        continue
                    for opp_next in opp_temp.get_valid_moves():
                        if opp_temp.make_move(opp_next).is_victory:
                            opp_threats += 1
                            break

                if opp_threats >= 2:
                    loses_immediately = True

            if not loses_immediately:
                safe.append(move)

        return safe

    def pick_defensive_move(self, board, valid_moves, my_color, enemy_color):
        """When all moves are bad, pick the one that delays loss longest."""
        best_move = valid_moves[0]
        best_delay = -1

        for move in valid_moves:
            temp = board.make_move(move)
            # Shallow search to see which move delays loss
            delay = self.count_moves_until_loss(temp, 3, enemy_color)
            if delay > best_delay:
                best_delay = delay
                best_move = move

        return best_move

    def count_moves_until_loss(self, board, depth, enemy_color):
        """Estimate moves until forced loss."""
        if depth == 0 or board.is_victory or board.is_draw:
            return depth

        # Assume opponent plays optimally
        min_delay = depth
        for move in board.get_valid_moves():
            temp = board.make_move(move)
            if temp.is_victory:
                return 0  # Immediate loss
            delay = self.count_moves_until_loss(
                temp,
                depth - 1,
                CellState.Red if enemy_color == CellState.Yellow else CellState.Yellow,
            )
            min_delay = min(min_delay, delay)

        return min_delay

    def negamax_search(self, board, depth, alpha, beta, my_color, enemy_color):
        """
        Negamax with alpha-beta pruning (cleaner than minimax).
        Uses enhanced move ordering and killer move heuristic.
        """
        valid_moves = board.get_valid_moves()

        # Terminal conditions
        if board.is_victory:
            return (None, -100000 - depth * 100)
        if board.is_draw or depth == 0:
            return (None, self.evaluate_position(board, my_color, enemy_color))

        # Move ordering: critical for alpha-beta efficiency
        def move_value(col):
            temp = board.make_move(col)
            if temp.is_victory:
                return -10000  # Winning move = highest priority

            # Prioritize center, then check if it blocks opponent
            score = abs(col - 3) * 10

            # Check if it blocks opponent win
            for opp_move in temp.get_valid_moves():
                if temp.make_move(opp_move).is_victory:
                    score -= 5000
                    break

            return score

        valid_moves.sort(key=move_value)

        best_move = valid_moves[0]
        best_value = -math.inf

        for move in valid_moves:
            next_board = board.make_move(move)

            # Recursive negamax call (negates score and swaps colors)
            _, value = self.negamax_search(
                next_board, depth - 1, -beta, -alpha, enemy_color, my_color
            )
            value = -value  # Negate for negamax

            if value > best_value:
                best_value = value
                best_move = move

            alpha = max(alpha, value)
            if alpha >= beta:
                break  # Prune

        return best_move, best_value

    def evaluate_position(self, board, my_color, enemy_color):
        """
        Highly tuned evaluation function.
        """
        score = 0

        # 1. Material in center columns (most important)
        center_weights = [1, 2, 3, 5, 3, 2, 1]  # Column 3 worth 5x more
        for col in range(7):
            for row in range(6):
                cell = board[col, row]
                if cell == my_color:
                    score += center_weights[col]
                elif cell == enemy_color:
                    score -= center_weights[col]

        # 2. Connectivity: reward connected pieces
        score += self.evaluate_connectivity(board, my_color, enemy_color)

        # 3. Threat analysis
        score += self.count_threats(board, my_color) * 10
        score -= self.count_threats(board, enemy_color) * 12  # Defend more than attack

        # 4. Control of key squares (bottom row is crucial)
        for col in range(7):
            if board[col, 5] == my_color:
                score += 3
            elif board[col, 5] == enemy_color:
                score -= 3

        return score

    def evaluate_connectivity(self, board, my_color, enemy_color):
        """Score based on connected pieces (2s and 3s in a row)."""
        score = 0

        # Check all windows
        for col in range(4):
            for row in range(6):
                window = [board[col + i, row] for i in range(4)]
                score += self.score_window_advanced(window, my_color, enemy_color)

        for col in range(7):
            for row in range(3):
                window = [board[col, row + i] for i in range(4)]
                score += self.score_window_advanced(window, my_color, enemy_color)

        for col in range(4):
            for row in range(3):
                window = [board[col + i, row + i] for i in range(4)]
                score += self.score_window_advanced(window, my_color, enemy_color)

        for col in range(4):
            for row in range(3, 6):
                window = [board[col + i, row - i] for i in range(4)]
                score += self.score_window_advanced(window, my_color, enemy_color)

        return score

    def score_window_advanced(self, window, my_color, enemy_color):
        """Advanced window scoring."""
        my_count = window.count(my_color)
        opp_count = window.count(enemy_color)
        empty = window.count(None)

        # Can't use window if opponent blocks it
        if my_count > 0 and opp_count > 0:
            return 0

        if my_count == 4:
            return 10000
        elif my_count == 3 and empty == 1:
            return 100
        elif my_count == 2 and empty == 2:
            return 10
        elif my_count == 1 and empty == 3:
            return 1
        elif opp_count == 3 and empty == 1:
            return -150  # Block threats aggressively
        elif opp_count == 2 and empty == 2:
            return -10

        return 0

    def count_threats(self, board, color):
        """Count number of 3-in-a-row threats (one move from winning)."""
        threats = 0

        for col in range(7):
            if col not in board.get_valid_moves():
                continue
            row = board.column_heights[col]
            if self.creates_win(board, col, row, color):
                threats += 1

        return threats

    def smart_fallback(self, valid_moves, board, my_color):
        """Intelligent fallback when search fails."""
        # Prefer center and near-center
        for col in [3, 2, 4, 1, 5, 0, 6]:
            if col in valid_moves:
                # Don't play in a column that's almost full (gives opponent top position)
                if board.column_heights[col] < 5:
                    return col

        # If all near-full, pick least full
        return min(valid_moves, key=lambda c: board.column_heights[c])
