from pingv4 import AbstractBot, ConnectFourBoard


class as264(AbstractBot):
    @property
    def strategy_name(self) -> str:
        return "AlphaBeta-ThreatEval"

    @property
    def author_name(self) -> str:
        return "Aniket Sharma"

    @property
    def author_netid(self) -> str:
        return "as264"

    def get_move(self, board: ConnectFourBoard) -> int:
        depth = 6
        valid_moves = board.get_valid_moves()

        if len(valid_moves) == 1:
            return valid_moves[0]

        immediate_win = self._find_immediate_win(board, board.current_player)
        if immediate_win is not None:
            return immediate_win

        opponent = (
            board.CellState.Yellow
            if board.current_player == board.CellState.Red
            else board.CellState.Red
        )
        immediate_block = self._find_immediate_win(board, opponent)
        if immediate_block is not None:
            return immediate_block

        best_move = None
        best_score = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        ordered_moves = self._order_moves(valid_moves, board)

        for move in ordered_moves:
            new_board = board.make_move(move)
            score = self._minimax(
                new_board, depth - 1, alpha, beta, False, board.current_player
            )

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, score)

        return best_move if best_move is not None else ordered_moves[0]

    def _find_immediate_win(self, board: ConnectFourBoard, player) -> int:
        for move in board.get_valid_moves():
            new_board = board.make_move(move)
            if new_board.is_victory and new_board.winner == player:
                return move
        return None

    def _order_moves(self, moves: list, board: ConnectFourBoard) -> list:
        center = board.width // 2
        return sorted(moves, key=lambda m: abs(m - center))

    def _minimax(
        self,
        board: ConnectFourBoard,
        depth: int,
        alpha: float,
        beta: float,
        is_maximizing: bool,
        original_player,
    ) -> float:
        if board.is_victory:
            if board.winner == original_player:
                return 10000 + depth
            elif board.winner is not None:
                return -10000 - depth
            else:
                return 0

        if depth == 0 or len(board.get_valid_moves()) == 0:
            return self._evaluate_board(board, original_player)

        valid_moves = self._order_moves(board.get_valid_moves(), board)

        if is_maximizing:
            max_eval = float("-inf")
            for move in valid_moves:
                new_board = board.make_move(move)
                eval_score = self._minimax(
                    new_board, depth - 1, alpha, beta, False, original_player
                )
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float("inf")
            for move in valid_moves:
                new_board = board.make_move(move)
                eval_score = self._minimax(
                    new_board, depth - 1, alpha, beta, True, original_player
                )
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def _evaluate_board(self, board: ConnectFourBoard, player) -> float:
        opponent = (
            board.CellState.Yellow
            if player == board.CellState.Red
            else board.CellState.Red
        )

        player_score = self._count_threats(board, player)
        opponent_score = self._count_threats(board, opponent)

        return player_score - opponent_score

    def _count_threats(self, board: ConnectFourBoard, player) -> float:
        score = 0.0

        for row in range(board.height):
            for col in range(board.width):
                score += self._evaluate_position(board, col, row, player)

        return score

    def _evaluate_position(
        self, board: ConnectFourBoard, col: int, row: int, player
    ) -> float:
        if board[col, row] != player:
            return 0.0

        score = 0.0
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for dx, dy in directions:
            count, empty = self._count_direction(board, col, row, dx, dy, player)

            if count >= 3 and empty >= 1:
                score += 100
            elif count >= 2 and empty >= 2:
                score += 10
            elif count >= 1 and empty >= 3:
                score += 1

        center = board.width // 2
        center_distance = abs(col - center)
        score += (board.width - center_distance) * 0.5

        return score

    def _count_direction(
        self, board: ConnectFourBoard, col: int, row: int, dx: int, dy: int, player
    ):
        count = 0
        empty = 0

        for i in range(4):
            c = col + dx * i
            r = row + dy * i

            if c < 0 or c >= board.width or r < 0 or r >= board.height:
                return count, 0

            cell = board[c, r]
            if cell == player:
                count += 1
            elif cell == board.CellState.Empty:
                empty += 1
            else:
                return count, 0

        return count, empty
