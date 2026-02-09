"""
You can follow this template for your Connect4 bot.
Copy this and rename it to: yourname_yournetid.py
"""

from pingv4 import AbstractBot, ConnectFourBoard


class pa896(AbstractBot):
    """
    This will be your Connect4 bot.
    CHANGE THE CLASS NAME TO your snu net id.
    """

    @property
    def strategy_name(self) -> str:
        return "fill the places"

    @property
    def author_name(self) -> str:
        return "Pari Aggarwal"

    @property
    def author_netid(self) -> str:
        return "pa896"

    def get_move(self, board: ConnectFourBoard) -> int:
        valid_moves = board.get_valid_moves()
        # This is an example of just picking the first valid move.
        player = board.current_player

        # 1️⃣ Try winning move
        for move in valid_moves:
            temp = board.copy()
            temp.make_move(move)
            if temp.check_winner() == player:
                return move

        # 2️⃣ Try blocking opponent win
        opponent = 3 - player  # assuming players are 1 and 2
        for move in valid_moves:
            temp = board.copy()
            temp.make_move(move)
            if temp.check_winner() == opponent:
                return move

        # 3️⃣ Prefer center columns
        center = board.width // 2
        valid_moves.sort(key=lambda x: abs(x - center))

        return valid_moves[0]  # You should improve this!
