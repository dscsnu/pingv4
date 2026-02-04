import random
import sys
from typing import Optional, Tuple, Type, Union

import pygame

sys.path.insert(0, str(__file__).rsplit("/", 1)[0] + "/src")
from pingv4 import AbstractBot, CellState, ConnectFourBoard


WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700
BOARD_ROWS = 6
BOARD_COLS = 7
CELL_SIZE = 80
BOARD_MARGIN_X = (WINDOW_WIDTH - BOARD_COLS * CELL_SIZE) // 2
BOARD_MARGIN_Y = 100
BOT_DELAY_SECONDS = 1 # Delay before bot makes a move (in seconds)

BACKGROUND_COLOR = (30, 30, 40)
BOARD_COLOR = (0, 80, 180)
EMPTY_COLOR = (20, 20, 30)
RED_COLOR = (220, 50, 50)
YELLOW_COLOR = (240, 220, 50)
HOVER_COLOR = (100, 100, 120)
TEXT_COLOR = (255, 255, 255)
WIN_HIGHLIGHT_COLOR = (50, 255, 50)


class ManualPlayer:
    def __init__(self, player: CellState) -> None:
        self.player = player
        self.strategy_name = "Manual Player"
        self.author_name = "Human"
        self.author_netid = "N/A"


class Connect4Game:
    def __init__(
        self,
        bot1: Optional[Type[AbstractBot]] = None,
        bot2: Optional[Type[AbstractBot]] = None,
    ) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Connect Four")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)

        self.player1_is_red = random.choice([True, False])

        if self.player1_is_red:
            red_bot_class = bot1
            yellow_bot_class = bot2
        else:
            red_bot_class = bot2
            yellow_bot_class = bot1

        if red_bot_class is not None:
            self.red_player = red_bot_class(CellState.Red)
        else:
            self.red_player = ManualPlayer(CellState.Red)

        if yellow_bot_class is not None:
            self.yellow_player = yellow_bot_class(CellState.Yellow)
        else:
            self.yellow_player = ManualPlayer(CellState.Yellow)

        self.board = ConnectFourBoard()
        self.hover_col: Optional[int] = None
        self.game_over = False
        self.winner_name: Optional[str] = None
        self.last_move_col: Optional[int] = None
        self.animating = False
        self.animation_col: Optional[int] = None
        self.animation_row_target: Optional[int] = None
        self.animation_y: float = 0
        self.animation_color: Optional[Tuple[int, int, int]] = None

        print("=" * 50)
        print("🪙 COIN FLIP RESULT 🪙")
        print("=" * 50)
        print(f"Red (goes first): {self.red_player.strategy_name} by {self.red_player.author_name}")
        print(f"Yellow: {self.yellow_player.strategy_name} by {self.yellow_player.author_name}")
        print("=" * 50)

    def get_current_player(self) -> Union[ManualPlayer, AbstractBot]:
        if self.board.current_player == CellState.Red:
            return self.red_player
        return self.yellow_player

    def is_manual_turn(self) -> bool:
        return isinstance(self.get_current_player(), ManualPlayer)

    def get_col_from_mouse(self, mouse_x: int) -> Optional[int]:
        if BOARD_MARGIN_X <= mouse_x < BOARD_MARGIN_X + BOARD_COLS * CELL_SIZE:
            col = (mouse_x - BOARD_MARGIN_X) // CELL_SIZE
            return col
        return None

    def make_move(self, col: int) -> bool:
        if col not in self.board.get_valid_moves():
            return False

        self.animating = True
        self.animation_col = col
        self.animation_row_target = self.board.column_heights[col]
        self.animation_y = BOARD_MARGIN_Y - CELL_SIZE
        self.animation_color = RED_COLOR if self.board.current_player == CellState.Red else YELLOW_COLOR
        self.last_move_col = col

        return True

    def finish_move(self) -> None:
        if self.animation_col is not None:
            self.board = self.board.make_move(self.animation_col)

            if not self.board.is_in_progress:
                self.game_over = True
                if self.board.is_victory:
                    winner = self.board.winner
                    if winner == CellState.Red:
                        self.winner_name = f"{self.red_player.strategy_name} (Red)"
                    else:
                        self.winner_name = f"{self.yellow_player.strategy_name} (Yellow)"
                else:
                    self.winner_name = "Draw"

        self.animating = False
        self.animation_col = None
        self.animation_row_target = None

    def update_animation(self) -> None:
        if not self.animating or self.animation_row_target is None:
            return

        target_y = BOARD_MARGIN_Y + (BOARD_ROWS - 1 - self.animation_row_target) * CELL_SIZE + CELL_SIZE // 2
        speed = 25

        self.animation_y += speed
        if self.animation_y >= target_y:
            self.animation_y = target_y
            self.finish_move()

    def draw_board(self) -> None:
        board_rect = pygame.Rect(
            BOARD_MARGIN_X - 10,
            BOARD_MARGIN_Y - 10,
            BOARD_COLS * CELL_SIZE + 20,
            BOARD_ROWS * CELL_SIZE + 20,
        )
        pygame.draw.rect(self.screen, BOARD_COLOR, board_rect, border_radius=10)

        cell_states = self.board.cell_states
        for col in range(BOARD_COLS):
            for row in range(BOARD_ROWS):
                screen_row = BOARD_ROWS - 1 - row
                x = BOARD_MARGIN_X + col * CELL_SIZE + CELL_SIZE // 2
                y = BOARD_MARGIN_Y + screen_row * CELL_SIZE + CELL_SIZE // 2

                cell = cell_states[col][row]
                if cell == CellState.Red:
                    color = RED_COLOR
                elif cell == CellState.Yellow:
                    color = YELLOW_COLOR
                else:
                    color = EMPTY_COLOR

                pygame.draw.circle(self.screen, color, (x, y), CELL_SIZE // 2 - 5)

        if self.animating and self.animation_col is not None and self.animation_color is not None:
            x = BOARD_MARGIN_X + self.animation_col * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(self.screen, self.animation_color, (x, int(self.animation_y)), CELL_SIZE // 2 - 5)

    def draw_hover_indicator(self) -> None:
        if not self.is_manual_turn() or self.game_over or self.animating:
            return

        if self.hover_col is not None and self.hover_col in self.board.get_valid_moves():
            x = BOARD_MARGIN_X + self.hover_col * CELL_SIZE + CELL_SIZE // 2
            y = BOARD_MARGIN_Y - CELL_SIZE // 2
            color = RED_COLOR if self.board.current_player == CellState.Red else YELLOW_COLOR

            preview_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(
                preview_surface,
                (*color, 150),
                (CELL_SIZE // 2, CELL_SIZE // 2),
                CELL_SIZE // 2 - 5,
            )
            self.screen.blit(preview_surface, (x - CELL_SIZE // 2, y - CELL_SIZE // 2))

    def draw_status(self) -> None:
        if self.game_over:
            if self.winner_name == "Draw":
                text = "Game Over - It's a Draw!"
            else:
                text = f"🎉 {self.winner_name} Wins! 🎉"
            color = WIN_HIGHLIGHT_COLOR
        else:
            current = self.get_current_player()
            player_color = "Red" if self.board.current_player == CellState.Red else "Yellow"
            if self.is_manual_turn():
                text = f"{current.strategy_name}'s Turn ({player_color}) - Click to play"
            else:
                text = f"{current.strategy_name}'s Turn ({player_color}) - Thinking..."
            color = TEXT_COLOR

        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, 40))
        self.screen.blit(text_surface, text_rect)

        red_info = f"Red: {self.red_player.strategy_name}"
        yellow_info = f"Yellow: {self.yellow_player.strategy_name}"

        red_surface = self.small_font.render(red_info, True, RED_COLOR)
        yellow_surface = self.small_font.render(yellow_info, True, YELLOW_COLOR)

        self.screen.blit(red_surface, (20, WINDOW_HEIGHT - 60))
        self.screen.blit(yellow_surface, (20, WINDOW_HEIGHT - 30))

        if self.game_over:
            restart_text = "Press R to restart or ESC to quit"
            restart_surface = self.small_font.render(restart_text, True, TEXT_COLOR)
            restart_rect = restart_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 45))
            self.screen.blit(restart_surface, restart_rect)

    def handle_bot_turn(self) -> None:
        if self.game_over or self.animating or self.is_manual_turn():
            return

        current_player = self.get_current_player()
        if isinstance(current_player, AbstractBot):
            try:
                col = current_player.get_move(self.board)
                if col in self.board.get_valid_moves():
                    self.make_move(col)
                else:
                    print(f"⚠️ Bot {current_player.strategy_name} returned invalid move: {col}")
                    valid_moves = self.board.get_valid_moves()
                    if valid_moves:
                        self.make_move(random.choice(valid_moves))
            except Exception as e:
                print(f"⚠️ Bot {current_player.strategy_name} error: {e}")
                valid_moves = self.board.get_valid_moves()
                if valid_moves:
                    self.make_move(random.choice(valid_moves))

    def reset_game(self) -> None:
        self.player1_is_red = random.choice([True, False])
        old_red = self.red_player
        old_yellow = self.yellow_player

        red_was_bot = not isinstance(old_red, ManualPlayer)
        yellow_was_bot = not isinstance(old_yellow, ManualPlayer)

        if self.player1_is_red:
            if red_was_bot:
                self.red_player = type(old_red)(CellState.Red)
            else:
                self.red_player = ManualPlayer(CellState.Red)
            if yellow_was_bot:
                self.yellow_player = type(old_yellow)(CellState.Yellow)
            else:
                self.yellow_player = ManualPlayer(CellState.Yellow)
        else:
            if yellow_was_bot:
                self.red_player = type(old_yellow)(CellState.Red)
            else:
                self.red_player = ManualPlayer(CellState.Red)
            if red_was_bot:
                self.yellow_player = type(old_red)(CellState.Yellow)
            else:
                self.yellow_player = ManualPlayer(CellState.Yellow)

        self.board = ConnectFourBoard()
        self.hover_col = None
        self.game_over = False
        self.winner_name = None
        self.last_move_col = None
        self.animating = False
        self.animation_col = None
        self.animation_row_target = None

        print("\n" + "=" * 50)
        print("🔄 NEW GAME - COIN FLIP 🪙")
        print("=" * 50)
        print(f"Red (goes first): {self.red_player.strategy_name}")
        print(f"Yellow: {self.yellow_player.strategy_name}")
        print("=" * 50)

    def run(self) -> None:
        running = True
        bot_delay = 0

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset_game()

                elif event.type == pygame.MOUSEMOTION:
                    mouse_x, _ = event.pos
                    self.hover_col = self.get_col_from_mouse(mouse_x)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and self.is_manual_turn() and not self.game_over and not self.animating:
                        mouse_x, _ = event.pos
                        col = self.get_col_from_mouse(mouse_x)
                        if col is not None:
                            self.make_move(col)

            self.update_animation()

            if not self.animating and not self.game_over and not self.is_manual_turn():
                bot_delay += 1
                if bot_delay >= BOT_DELAY_SECONDS * 60:
                    self.handle_bot_turn()
                    bot_delay = 0
            else:
                bot_delay = 0

            self.screen.fill(BACKGROUND_COLOR)
            self.draw_board()
            self.draw_hover_indicator()
            self.draw_status()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


def play_game(
    bot1: Optional[Type[AbstractBot]] = None,
    bot2: Optional[Type[AbstractBot]] = None,
) -> None:
    game = Connect4Game(bot1, bot2)
    game.run()


if __name__ == "__main__":
    # Example usage:
    # To play with two manual players:
    play_game()

    # To play with one bot vs manual:
    # from your_bot_module import YourBot
    # play_game(bot1=YourBot)

    # To play two bots against each other:
    # from bot1_module import Bot1
    # from bot2_module import Bot2
    # play_game(bot1=Bot1, bot2=Bot2)
