import json
import urllib.parse
import urllib.request

from pingv4 import AbstractBot, CellState, ConnectFourBoard

API_ENDPOINT = "https://kevinalbs.com/connect4/back-end/index.php/getMoves"


def _board_to_api_string(board: ConnectFourBoard) -> str:
  rows = board.num_rows
  cols = board.num_cols
  chars = []
  for row in range(rows - 1, -1, -1):
    for col in range(cols):
      cell = board[col, row]
      if cell is None:
        chars.append("0")
      elif cell == CellState.Red:
        chars.append("1")
      else:
        chars.append("2")
  return "".join(chars)


def _player_to_api_value(board: ConnectFourBoard) -> int:
  if board.current_player == CellState.Red:
    return 1
  if board.current_player == CellState.Yellow:
    return 2
  return 1


def _fetch_move_scores(board_data: str, player: int) -> dict:
  query = urllib.parse.urlencode({"board_data": board_data, "player": player})
  url = f"{API_ENDPOINT}?{query}"
  with urllib.request.urlopen(url, timeout=2.5) as response:
    payload = response.read().decode("utf-8")
  return json.loads(payload)

class AA371(AbstractBot):
  @property
  def strategy_name(self) -> str:
    return "lolz"

  @property
  def author_name(self) -> str:
    return "Amogh"

  @property
  def author_netid(self) -> str:
    return "AA371"

  def get_move(self, board: ConnectFourBoard) -> int:
    valid_moves = board.get_valid_moves()
    if not valid_moves:
      raise ValueError("No valid moves available")

    board_data = _board_to_api_string(board)
    player_value = _player_to_api_value(board)

    try:
      scores = _fetch_move_scores(board_data, player_value)
      best_move = None
      best_score = None
      for move in valid_moves:
        score = scores.get(str(move))
        if score is None:
          continue
        if best_move is None or score > best_score:
          best_move = move
          best_score = score
      if best_move is not None:
        return best_move
    except Exception:
      pass

    for col in [3, 2, 4, 1, 5, 0, 6]:
      if col in valid_moves:
        return col

    return valid_moves[0]