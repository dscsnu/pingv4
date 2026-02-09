from pingv4 import AbstractBot, ConnectFourBoard, CellState

class MyBot(AbstractBot):
    @property
    def strategy_name(self) -> str:
        return "GrumBot"
    
    @property
    def author_name(self) -> str:
        return "Sarthak Jain"
    
    @property
    def author_netid(self) -> str:
        return "sj993"
    
    def get_move(self, board: ConnectFourBoard) -> int:
        valid_moves = board.get_valid_moves()
        center = board.num_cols // 2  

        move = win(board, valid_moves)
        if move != -1:
            return move

        move = prevent(board, valid_moves)
        if move != -1:
            return move

        safe_moves = [
            c for c in valid_moves
            if not move_provides_opponent_support(board, c)
            and not is_winning_cell(
                board,
                c,
                board.column_heights[c],
                CellState.Red if board.current_player == CellState.Yellow else CellState.Yellow
            )
        ]


        if not safe_moves:
            return valid_moves[0]

        if center in safe_moves:
            return center

        return pick_best_safe_move(board, safe_moves)



def pick_best_safe_move(board, safe_moves):
    player = board.current_player
    center = board.num_cols // 2

    best = safe_moves[0]
    best_score = -10**9

    for c in safe_moves:
        row = board.column_heights[c]
        score = 0

        if is_winning_cell(board, c, row, player):
            score += 100

        score -= abs(c - center)

        if score > best_score:
            best_score = score
            best = c

    return best


def win(board, valid_moves):
    player = board.current_player

    for c in valid_moves:
        row = board.column_heights[c]
        if is_supported(board, c, row) and is_winning_cell(board, c, row, player):
            return c

    return -1



def prevent(board, valid_moves):
    opponent = (
        CellState.Red
        if board.current_player == CellState.Yellow
        else CellState.Yellow
    )

    for c in valid_moves:
        row = board.column_heights[c]
        if is_supported(board, c, row) and is_winning_cell(board, c, row, opponent):
            return c

    return -1



def is_supported(board, col, row):
    return row == 0 or board[col, row - 1] is not None

def count_in_direction(board, col, row, dcol, drow, player):
    count = 0
    c, r = col + dcol, row + drow
    steps = 0

    while 0 <= c < board.num_cols and 0 <= r < board.num_rows and steps < 3:
        if board[c, r] == player:
            count += 1
        elif board[c, r] is not None:
            break  
        c += dcol
        r += drow
        steps += 1

    return count



def is_winning_cell(board, col, row, player):
    if board[col, row] is not None:
        return False

    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

    for dc, dr in directions:
        total = 1
        total += count_in_direction(board, col, row, dc, dr, player)
        total += count_in_direction(board, col, row, -dc, -dr, player)
        if total >= 4:
            return True

    return False


def move_provides_opponent_support(board, column):
    opponent = (
        CellState.Red
        if board.current_player == CellState.Yellow
        else CellState.Yellow
    )

    landing_row = board.column_heights[column]
    target_row = landing_row + 1

    if target_row >= board.num_rows:
        return False

    if is_supported(board, column, target_row):
        return False

    return is_winning_cell(board, column, target_row, opponent)