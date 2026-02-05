import pygame
import random
from pydantic import BaseModel
from typing import Optional, Tuple, Type, Union

from pingv4 import AbstractBot, CellState, ConnectFourBoard


class GameConfig(BaseModel, frozen=True):
    """Configuration options for Connect4Game."""

    # Bot timing
    bot_delay_seconds: float = 1.0

    # Animation
    animation_speed: int = 25

    # Window dimensions
    window_width: int = 700
    window_height: int = 700

    # Board display
    cell_size: int = 80

    # Board constants
    board_rows: int = 6
    board_cols: int = 7

    # Colors
    background_color: Tuple[int, int, int] = (30, 30, 40)
    board_color: Tuple[int, int, int] = (0, 80, 180)
    empty_color: Tuple[int, int, int] = (20, 20, 30)
    red_color: Tuple[int, int, int] = (220, 50, 50)
    yellow_color: Tuple[int, int, int] = (240, 220, 50)
    hover_color: Tuple[int, int, int] = (100, 100, 120)
    text_color: Tuple[int, int, int] = (255, 255, 255)
    win_highlight_color: Tuple[int, int, int] = (50, 255, 50)

    @property
    def board_margin_x(self) -> int:
        """Calculate horizontal margin to center the board."""
        return (self.window_width - self.board_cols * self.cell_size) // 2

    @property
    def board_margin_y(self) -> int:
        """Vertical margin from top of window."""
        return 100


class ManualPlayer:
    """Represents a human player who makes moves manually."""

    def __init__(self, player: CellState) -> None:
        self.player = player
        self.strategy_name = "Manual Player"
        self.author_name = "Human"
        self.author_netid = "N/A"


# Player can be specified as:
# - None (manual player)
# - AbstractBot subclass (will be instantiated with the assigned color)
# - ManualPlayer instance
PlayerConfig = Union[None, Type[AbstractBot], ManualPlayer]


class Connect4Game:
    """
    A graphical Connect Four game supporting both human and bot players.

    Initialize with player configurations and optional game settings:

    Examples:
        # Two manual players
        game = Connect4Game()
        game.run()

        # Bot vs bot with custom timing
        config = GameConfig(bot_delay_seconds=0.5)
        game = Connect4Game(player1=RandomBot, player2=RandomBot, config=config)
        game.run()

        # Manual player vs bot
        game = Connect4Game(player1=None, player2=RandomBot)
        game.run()
    """

    def __init__(
        self,
        player1: PlayerConfig = None,
        player2: PlayerConfig = None,
        config: Optional[GameConfig] = None,
    ) -> None:
        """
        Initialize a Connect Four game.

        Args:
            player1: First player - None for manual, or an AbstractBot subclass.
            player2: Second player - None for manual, or an AbstractBot subclass.
            config: Game configuration options. Uses defaults if not provided.
        """
        self.config = config or GameConfig()
        self._player1_config = player1
        self._player2_config = player2

        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.config.window_width, self.config.window_height)
        )
        pygame.display.set_caption("Connect Four")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)

        # Randomly assign colors to players
        self.player1_is_red = random.choice([True, False])

        if self.player1_is_red:
            red_config = player1
            yellow_config = player2
        else:
            red_config = player2
            yellow_config = player1

        self.red_player = self._resolve_player(red_config, CellState.Red)
        self.yellow_player = self._resolve_player(yellow_config, CellState.Yellow)

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
        print("COIN FLIP RESULT")
        print("=" * 50)
        print(
            f"Red (goes first): {self.red_player.strategy_name} by {self.red_player.author_name}"
        )
        print(
            f"Yellow: {self.yellow_player.strategy_name} by {self.yellow_player.author_name}"
        )
        print("=" * 50)

    def _resolve_player(
        self, player_config: PlayerConfig, color: CellState
    ) -> Union[ManualPlayer, AbstractBot]:
        """
        Convert PlayerConfig to a player instance.

        Args:
            player_config: The player configuration.
            color: The CellState color to assign.

        Returns:
            A ManualPlayer or AbstractBot instance.

        Raises:
            TypeError: If player_config is an invalid type.
        """
        if player_config is None:
            return ManualPlayer(color)
        elif isinstance(player_config, ManualPlayer):
            return player_config
        elif isinstance(player_config, type) and issubclass(player_config, AbstractBot):
            # Bot class provided - instantiate with color
            return player_config(color)
        else:
            raise TypeError(f"Invalid player config type: {type(player_config)}")

    def get_current_player(self) -> Union[ManualPlayer, AbstractBot]:
        """Get the player whose turn it currently is."""
        if self.board.current_player == CellState.Red:
            return self.red_player
        return self.yellow_player

    def is_manual_turn(self) -> bool:
        """Check if the current turn belongs to a manual player."""
        return isinstance(self.get_current_player(), ManualPlayer)

    def get_col_from_mouse(self, mouse_x: int) -> Optional[int]:
        """Convert mouse x-coordinate to board column index."""
        cfg = self.config
        if (
            cfg.board_margin_x
            <= mouse_x
            < cfg.board_margin_x + cfg.board_cols * cfg.cell_size
        ):
            col = (mouse_x - cfg.board_margin_x) // cfg.cell_size
            return col
        return None

    def make_move(self, col: int) -> bool:
        """
        Initiate a move animation for the specified column.

        Returns:
            True if the move is valid and animation started, False otherwise.
        """
        if col not in self.board.get_valid_moves():
            return False

        cfg = self.config
        self.animating = True
        self.animation_col = col
        self.animation_row_target = self.board.column_heights[col]
        self.animation_y = cfg.board_margin_y - cfg.cell_size
        self.animation_color = (
            cfg.red_color
            if self.board.current_player == CellState.Red
            else cfg.yellow_color
        )
        self.last_move_col = col

        return True

    def finish_move(self) -> None:
        """Complete the current move after animation finishes."""
        if self.animation_col is not None:
            self.board = self.board.make_move(self.animation_col)

            if not self.board.is_in_progress:
                self.game_over = True
                if self.board.is_victory:
                    winner = self.board.winner
                    if winner == CellState.Red:
                        self.winner_name = f"{self.red_player.strategy_name} (Red)"
                        self.winner = 1 if self.player1_is_red else 2
                    else:
                        self.winner_name = (
                            f"{self.yellow_player.strategy_name} (Yellow)"
                        )
                        self.winner = 2 if self.player1_is_red else 1
                else:
                    self.winner_name = "Draw"
                    self.winner = 0

        self.animating = False
        self.animation_col = None
        self.animation_row_target = None

    def update_animation(self) -> None:
        """Update the falling piece animation."""
        if not self.animating or self.animation_row_target is None:
            return

        cfg = self.config
        target_y = (
            cfg.board_margin_y
            + (cfg.board_rows - 1 - self.animation_row_target) * cfg.cell_size
            + cfg.cell_size // 2
        )

        self.animation_y += cfg.animation_speed
        if self.animation_y >= target_y:
            self.animation_y = target_y
            self.finish_move()

    def draw_board(self) -> None:
        """Draw the game board and all pieces."""
        cfg = self.config
        board_rect = pygame.Rect(
            cfg.board_margin_x - 10,
            cfg.board_margin_y - 10,
            cfg.board_cols * cfg.cell_size + 20,
            cfg.board_rows * cfg.cell_size + 20,
        )
        pygame.draw.rect(self.screen, cfg.board_color, board_rect, border_radius=10)

        cell_states = self.board.cell_states
        for col in range(cfg.board_cols):
            for row in range(cfg.board_rows):
                screen_row = cfg.board_rows - 1 - row
                x = cfg.board_margin_x + col * cfg.cell_size + cfg.cell_size // 2
                y = cfg.board_margin_y + screen_row * cfg.cell_size + cfg.cell_size // 2

                cell = cell_states[col][row]
                if cell == CellState.Red:
                    color = cfg.red_color
                elif cell == CellState.Yellow:
                    color = cfg.yellow_color
                else:
                    color = cfg.empty_color

                pygame.draw.circle(self.screen, color, (x, y), cfg.cell_size // 2 - 5)

        if (
            self.animating
            and self.animation_col is not None
            and self.animation_color is not None
        ):
            x = (
                cfg.board_margin_x
                + self.animation_col * cfg.cell_size
                + cfg.cell_size // 2
            )
            pygame.draw.circle(
                self.screen,
                self.animation_color,
                (x, int(self.animation_y)),
                cfg.cell_size // 2 - 5,
            )

    def draw_hover_indicator(self) -> None:
        """Draw the hover preview for manual players."""
        if not self.is_manual_turn() or self.game_over or self.animating:
            return

        cfg = self.config
        if (
            self.hover_col is not None
            and self.hover_col in self.board.get_valid_moves()
        ):
            x = cfg.board_margin_x + self.hover_col * cfg.cell_size + cfg.cell_size // 2
            y = cfg.board_margin_y - cfg.cell_size // 2
            color = (
                cfg.red_color
                if self.board.current_player == CellState.Red
                else cfg.yellow_color
            )

            preview_surface = pygame.Surface(
                (cfg.cell_size, cfg.cell_size), pygame.SRCALPHA
            )
            pygame.draw.circle(
                preview_surface,
                (*color, 150),
                (cfg.cell_size // 2, cfg.cell_size // 2),
                cfg.cell_size // 2 - 5,
            )
            self.screen.blit(
                preview_surface, (x - cfg.cell_size // 2, y - cfg.cell_size // 2)
            )

    def draw_status(self) -> None:
        """Draw the game status text."""
        cfg = self.config
        if self.game_over:
            if self.winner_name == "Draw":
                text = "Game Over - It's a Draw!"
            else:
                text = f"{self.winner_name} Wins!"
            color = cfg.win_highlight_color
        else:
            current = self.get_current_player()
            player_color = (
                "Red" if self.board.current_player == CellState.Red else "Yellow"
            )
            if self.is_manual_turn():
                text = (
                    f"{current.strategy_name}'s Turn ({player_color}) - Click to play"
                )
            else:
                text = f"{current.strategy_name}'s Turn ({player_color}) - Thinking..."
            color = cfg.text_color

        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(cfg.window_width // 2, 40))
        self.screen.blit(text_surface, text_rect)

        red_info = f"Red: {self.red_player.strategy_name}"
        yellow_info = f"Yellow: {self.yellow_player.strategy_name}"

        red_surface = self.small_font.render(red_info, True, cfg.red_color)
        yellow_surface = self.small_font.render(yellow_info, True, cfg.yellow_color)

        self.screen.blit(red_surface, (20, cfg.window_height - 60))
        self.screen.blit(yellow_surface, (20, cfg.window_height - 30))

        if self.game_over:
            restart_text = "Press R to restart or ESC to quit"
            restart_surface = self.small_font.render(restart_text, True, cfg.text_color)
            restart_rect = restart_surface.get_rect(
                center=(cfg.window_width // 2, cfg.window_height - 45)
            )
            self.screen.blit(restart_surface, restart_rect)

    def handle_bot_turn(self) -> None:
        """Handle the bot's turn by getting and executing its move."""
        if self.game_over or self.animating or self.is_manual_turn():
            return

        current_player = self.get_current_player()
        if isinstance(current_player, AbstractBot):
            try:
                col = current_player.get_move(self.board)
                if col in self.board.get_valid_moves():
                    self.make_move(col)
                else:
                    print(
                        f"Bot {current_player.strategy_name} returned invalid move: {col}"
                    )
                    valid_moves = self.board.get_valid_moves()
                    if valid_moves:
                        self.make_move(random.choice(valid_moves))
            except Exception as e:
                print(f"Bot {current_player.strategy_name} error: {e}")
                valid_moves = self.board.get_valid_moves()
                if valid_moves:
                    self.make_move(random.choice(valid_moves))

    def reset_game(self) -> None:
        """Reset the game to initial state with new color assignment."""
        self.player1_is_red = random.choice([True, False])

        if self.player1_is_red:
            red_config = self._player1_config
            yellow_config = self._player2_config
        else:
            red_config = self._player2_config
            yellow_config = self._player1_config

        self.red_player = self._resolve_player(red_config, CellState.Red)
        self.yellow_player = self._resolve_player(yellow_config, CellState.Yellow)

        self.board = ConnectFourBoard()
        self.hover_col = None
        self.game_over = False
        self.winner_name = None
        self.last_move_col = None
        self.animating = False
        self.animation_col = None
        self.animation_row_target = None

        print("\n" + "=" * 50)
        print("NEW GAME - COIN FLIP")
        print("=" * 50)
        print(f"Red (goes first): {self.red_player.strategy_name}")
        print(f"Yellow: {self.yellow_player.strategy_name}")
        print("=" * 50)

    def run(self) -> None:
        """Run the game loop until the window is closed."""
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
                    if (
                        event.button == 1
                        and self.is_manual_turn()
                        and not self.game_over
                        and not self.animating
                    ):
                        mouse_x, _ = event.pos
                        col = self.get_col_from_mouse(mouse_x)
                        if col is not None:
                            self.make_move(col)

            self.update_animation()

            if not self.animating and not self.game_over and not self.is_manual_turn():
                bot_delay += 1
                if bot_delay >= self.config.bot_delay_seconds * 60:
                    self.handle_bot_turn()
                    bot_delay = 0
            else:
                bot_delay = 0

            self.screen.fill(self.config.background_color)
            self.draw_board()
            self.draw_hover_indicator()
            self.draw_status()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    # Example usage:
    # Two manual players with default config
    game = Connect4Game()
    game.run()

    # To play with custom settings:
    # config = GameConfig(bot_delay_seconds=0.5, animation_speed=35)
    # game = Connect4Game(player1=RandomBot, player2=RandomBot, config=config)
    # game.run()
