from pingv4 import AbstractBot, ConnectFourBoard
from pingv4.game import CellState
import math
import random


class ss691(AbstractBot):
    strategy_name = "Classic Minimax + AlphaBeta + TT"
    author_name = "Saket Kumar Sinha"
    author_netid = "ss691"

    ROW_COUNT = 6
    COLUMN_COUNT = 7
    WINDOW_LENGTH = 4

    def __init__(self, color: CellState):
        super().__init__(color)

        self.my_color = color
        self.opp_color = CellState.Yellow if color == CellState.Red else CellState.Red

        # Internal representation (same as pygame bot)
        # 0 = empty
        # 1 = opponent
        # 2 = us
        self.EMPTY = 0
        self.PLAYER_PIECE = 1
        self.AI_PIECE = 2

        # Transposition table
        self.tt = {}

        # Depth (8 is strong but still feasible with caching)
        self.DEPTH = 8

    # ----------------------------
    # pingv4 -> classic grid[row][col]
    # pingv4 uses cell_states[col][row]
    # and row=0 is bottom
    # ----------------------------
    def to_grid(self, board: ConnectFourBoard):
        grid = [[0 for _ in range(self.COLUMN_COUNT)] for _ in range(self.ROW_COUNT)]

        for c in range(self.COLUMN_COUNT):
            for r in range(self.ROW_COUNT):
                cell = board.cell_states[c][r]  # col first, then row
                if cell is None:
                    grid[r][c] = 0
                else:
                    # Map to internal pieces
                    if cell == self.my_color:
                        grid[r][c] = self.AI_PIECE
                    else:
                        grid[r][c] = self.PLAYER_PIECE

        return grid

    # ----------------------------
    # Helpers
    # ----------------------------
    def grid_key(self, grid):
        return tuple(tuple(row) for row in grid)

    def order_moves(self, valid_locations):
        center = self.COLUMN_COUNT // 2
        return sorted(valid_locations, key=lambda c: abs(center - c))

    def is_valid_location(self, grid, col):
        return grid[self.ROW_COUNT - 1][col] == 0

    def get_next_open_row(self, grid, col):
        for r in range(self.ROW_COUNT):
            if grid[r][col] == 0:
                return r
        return None

    def drop_piece(self, grid, row, col, piece):
        grid[row][col] = piece

    def get_valid_locations(self, grid):
        return [col for col in range(self.COLUMN_COUNT) if self.is_valid_location(grid, col)]

    # ----------------------------
    # Win check (same as pygame bot)
    # ----------------------------
    def winning_move(self, grid, piece):
        # Horizontal
        for c in range(self.COLUMN_COUNT - 3):
            for r in range(self.ROW_COUNT):
                if (
                    grid[r][c] == piece
                    and grid[r][c + 1] == piece
                    and grid[r][c + 2] == piece
                    and grid[r][c + 3] == piece
                ):
                    return True

        # Vertical
        for c in range(self.COLUMN_COUNT):
            for r in range(self.ROW_COUNT - 3):
                if (
                    grid[r][c] == piece
                    and grid[r + 1][c] == piece
                    and grid[r + 2][c] == piece
                    and grid[r + 3][c] == piece
                ):
                    return True

        # Positive diagonal
        for c in range(self.COLUMN_COUNT - 3):
            for r in range(self.ROW_COUNT - 3):
                if (
                    grid[r][c] == piece
                    and grid[r + 1][c + 1] == piece
                    and grid[r + 2][c + 2] == piece
                    and grid[r + 3][c + 3] == piece
                ):
                    return True

        # Negative diagonal
        for c in range(self.COLUMN_COUNT - 3):
            for r in range(3, self.ROW_COUNT):
                if (
                    grid[r][c] == piece
                    and grid[r - 1][c + 1] == piece
                    and grid[r - 2][c + 2] == piece
                    and grid[r - 3][c + 3] == piece
                ):
                    return True

        return False

    # ----------------------------
    # Scoring (EXACT classic)
    # ----------------------------
    def evaluate_window(self, window, piece):
        score = 0
        opp_piece = self.PLAYER_PIECE if piece == self.AI_PIECE else self.AI_PIECE

        if window.count(piece) == 4:
            score += 100
        elif window.count(piece) == 3 and window.count(self.EMPTY) == 1:
            score += 5
        elif window.count(piece) == 2 and window.count(self.EMPTY) == 2:
            score += 2

        if window.count(opp_piece) == 3 and window.count(self.EMPTY) == 1:
            score -= 4

        return score

    def score_position(self, grid, piece):
        score = 0

        # Center column
        center_array = [grid[r][self.COLUMN_COUNT // 2] for r in range(self.ROW_COUNT)]
        center_count = center_array.count(piece)
        score += center_count * 3

        # Horizontal
        for r in range(self.ROW_COUNT):
            row_array = grid[r]
            for c in range(self.COLUMN_COUNT - 3):
                window = row_array[c : c + self.WINDOW_LENGTH]
                score += self.evaluate_window(window, piece)

        # Vertical
        for c in range(self.COLUMN_COUNT):
            col_array = [grid[r][c] for r in range(self.ROW_COUNT)]
            for r in range(self.ROW_COUNT - 3):
                window = col_array[r : r + self.WINDOW_LENGTH]
                score += self.evaluate_window(window, piece)

        # Positive diagonal
        for r in range(self.ROW_COUNT - 3):
            for c in range(self.COLUMN_COUNT - 3):
                window = [grid[r + i][c + i] for i in range(self.WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece)

        # Negative diagonal
        for r in range(self.ROW_COUNT - 3):
            for c in range(self.COLUMN_COUNT - 3):
                window = [grid[r + 3 - i][c + i] for i in range(self.WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece)

        return score

    # ----------------------------
    # Terminal
    # ----------------------------
    def is_terminal_node(self, grid):
        return (
            self.winning_move(grid, self.PLAYER_PIECE)
            or self.winning_move(grid, self.AI_PIECE)
            or len(self.get_valid_locations(grid)) == 0
        )

    # ----------------------------
    # Minimax with alpha-beta + caching
    # ----------------------------
    def minimax(self, grid, depth, alpha, beta, maximizingPlayer):
        key = (self.grid_key(grid), depth, maximizingPlayer)
        if key in self.tt:
            return self.tt[key]

        valid_locations = self.get_valid_locations(grid)
        is_terminal = self.is_terminal_node(grid)

        if depth == 0 or is_terminal:
            if is_terminal:
                if self.winning_move(grid, self.AI_PIECE):
                    result = (None, 100000000000000)
                elif self.winning_move(grid, self.PLAYER_PIECE):
                    result = (None, -10000000000000)
                else:
                    result = (None, 0)
            else:
                result = (None, self.score_position(grid, self.AI_PIECE))

            self.tt[key] = result
            return result

        # Move ordering = huge pruning boost
        valid_locations = self.order_moves(valid_locations)

        if maximizingPlayer:
            value = -math.inf
            column = valid_locations[0]

            for col in valid_locations:
                row = self.get_next_open_row(grid, col)

                b_copy = [r[:] for r in grid]
                self.drop_piece(b_copy, row, col, self.AI_PIECE)

                new_score = self.minimax(b_copy, depth - 1, alpha, beta, False)[1]

                if new_score > value:
                    value = new_score
                    column = col

                alpha = max(alpha, value)
                if alpha >= beta:
                    break

            result = (column, value)
            self.tt[key] = result
            return result

        else:
            value = math.inf
            column = valid_locations[0]

            for col in valid_locations:
                row = self.get_next_open_row(grid, col)

                b_copy = [r[:] for r in grid]
                self.drop_piece(b_copy, row, col, self.PLAYER_PIECE)

                new_score = self.minimax(b_copy, depth - 1, alpha, beta, True)[1]

                if new_score < value:
                    value = new_score
                    column = col

                beta = min(beta, value)
                if alpha >= beta:
                    break

            result = (column, value)
            self.tt[key] = result
            return result

    # ----------------------------
    # BOT MOVE
    # ----------------------------
    def get_move(self, board: ConnectFourBoard) -> int:
        # Clear cache each move (important!)
        self.tt.clear()

        grid = self.to_grid(board)
        valid = self.get_valid_locations(grid)

        if not valid:
            return 3

        col, _ = self.minimax(grid, self.DEPTH, -math.inf, math.inf, True)

        if col is None:
            return random.choice(valid)

        return col