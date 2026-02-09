import os
import sys
import random
import importlib.util
import inspect
from pathlib import Path
from typing import Type, List, Any, Optional
from datetime import datetime
import time

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from pydantic import BaseModel

import pingv4


# ==================== CONFIG ====================

SUBMISSION_PATH = os.path.join("submissions")
BOT_CLASS = pingv4.AbstractBot
IGNORE = ["__init__.py"]
POPULATION_FILE = "population.txt"

console = Console()


# ==================== Pydantic MODELS ====================


class GameResult(BaseModel):
    game_number: int
    winner: Optional[str]


class MatchResult(BaseModel):
    match_number: int
    player_1: str
    player_2: str
    wins_1: int
    wins_2: int
    games: List[GameResult]
    winner: Optional[str]


class RoundState(BaseModel):
    round_number: int
    population: List[str]
    matches: List[MatchResult]


class TournamentResult(BaseModel):
    started_at: datetime
    champion: str
    rounds: List[RoundState]


# ==================== HELPERS ====================


def bot_label(bot_cls):
    try:
        bot = bot_cls(player=pingv4.CellState.Red)
        return bot.strategy_name, bot.author_name
    except Exception:
        return bot_cls.__name__, "Unknown"


def read_population_file(path: str) -> List[str]:
    if not os.path.exists(path):
        return []

    with open(path, "r") as f:
        lines = [line.strip() for line in f.readlines()]

    return [l for l in lines if l]


def write_population_file(path: str, filenames: List[str]):
    with open(path, "w") as f:
        for name in filenames:
            f.write(f"{name}\n")


# ==================== LOADER ====================


def load_and_instantiate(
    directory: str = SUBMISSION_PATH,
    base_class: Type = BOT_CLASS,
    exclude_files: List[str] = IGNORE,
    population_file: str = POPULATION_FILE,
) -> dict[type[Any], str]:
    directory_path = Path(directory)
    requested_files = read_population_file(population_file)

    if requested_files:
        py_files = [directory_path / f for f in requested_files]
    else:
        py_files = list(directory_path.glob("*.py"))

    population: dict[type[Any], str] = {}

    with console.status("[bold cyan]Loading bot submissions...", spinner="dots"):
        for py_file in py_files:
            if not py_file.exists():
                console.print(f"[red]Missing file:[/] {py_file.name}")
                continue

            if py_file.name in exclude_files:
                continue

            module_name = py_file.stem
            spec = importlib.util.spec_from_file_location(module_name, py_file)

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if (
                        issubclass(obj, base_class)
                        and obj is not base_class
                        and obj.__module__ == module_name
                    ):
                        population[obj] = py_file.name
                        strat, author = bot_label(obj)
                        console.print(
                            f"  ✓ Loaded [bold green]{strat}[/] by [cyan]{author}[/]"
                        )

    console.print(f"\n[bold]Total bots loaded:[/] [green]{len(population)}[/]\n")
    return population


# ==================== DISPLAY ====================


def display_matchup(player_1, player_2, round_num):
    table = Table(show_header=False, box=box.DOUBLE_EDGE, border_style="bright_blue")
    table.add_column(justify="center")
    table.add_column(justify="center")
    table.add_column(justify="center")

    p1_strat, p1_author = bot_label(player_1)
    p2_strat, p2_author = bot_label(player_2)

    table.add_row(
        f"{p1_strat}\n({p1_author})",
        "VS",
        f"{p2_strat}\n({p2_author})",
    )

    console.print(
        Panel(
            table,
            title=f"[bold yellow]Round {round_num} Match[/]",
            border_style="yellow",
        )
    )


def display_game_result(game_num, winner_class):
    if winner_class:
        strat, _ = bot_label(winner_class)
        console.print(f"  Game {game_num}: [bold green]{strat}[/] wins!")
    else:
        console.print(f"  Game {game_num}: [bold yellow]Draw[/]")


def display_match_winner(winner, score):
    strat, _ = bot_label(winner)
    console.print(
        Panel(
            f"[bold green]{strat}[/] wins the match! ({score})",
            border_style="green",
        )
    )


# ==================== TOURNAMENT ====================


def pair(population: dict[type[pingv4.AbstractBot], str]):
    round_num = 1
    tournament_rounds: List[RoundState] = []

    console.print(
        Panel.fit(
            "[bold cyan]🏆 CONNECT 4 BOT TOURNAMENT 🏆[/]\n"
            f"[white]Starting with {len(population)} competitors[/]",
            border_style="cyan",
        )
    )

    while len(population) > 1:
        console.print(f"\n[bold yellow]{'=' * 70}[/]")
        console.print(
            f"[bold white]ROUND {round_num} - {len(population)} bots remaining[/]"
        )
        console.print(f"[bold yellow]{'=' * 70}[/]\n")

        round_population = list(population.values())
        write_population_file(POPULATION_FILE, round_population)

        round_matches: List[MatchResult] = []

        bot_classes = list(population.keys())

        if len(bot_classes) % 2 == 1:
            console.print("[yellow]Odd number of bots - adding RandomBot[/]\n")
            population[pingv4.RandomBot] = "__builtin__"
            bot_classes.append(pingv4.RandomBot)

        random.shuffle(bot_classes)
        pairs = list(zip(bot_classes[::2], bot_classes[1::2]))

        for match_num, (player_1, player_2) in enumerate(pairs, 1):
            console.print(f"\n[bold]Match {match_num}/{len(pairs)}[/]")
            display_matchup(player_1, player_2, round_num)

            wins_1 = wins_2 = games_played = 0
            games_log: List[GameResult] = []

            while games_played < 3 and wins_1 < 2 and wins_2 < 2:
                console.print(f"\n[dim]Playing game {games_played + 1}...[/]")

                game = pingv4.Connect4Game(player1=player_1, player2=player_2)
                game.run()

                winner_name = None

                match game.winner:
                    case 1:
                        wins_1 += 1
                        winner_name = bot_label(player_1)[0]
                        display_game_result(games_played + 1, player_1)
                    case 2:
                        wins_2 += 1
                        winner_name = bot_label(player_2)[0]
                        display_game_result(games_played + 1, player_2)
                    case _:
                        display_game_result(games_played + 1, None)

                games_log.append(
                    GameResult(
                        game_number=games_played + 1,
                        winner=winner_name,
                    )
                )

                games_played += 1

            p1_name, _ = bot_label(player_1)
            p2_name, _ = bot_label(player_2)

            match_winner = None
            if wins_1 > wins_2:
                match_winner = p1_name
                display_match_winner(player_1, f"{wins_1}-{wins_2}")
                population.pop(player_2, None)

            elif wins_2 > wins_1:
                match_winner = p2_name
                display_match_winner(player_2, f"{wins_2}-{wins_1}")
                population.pop(player_1, None)

            else:
                console.print(
                    "[yellow]Tie match![/]\n"
                    "[dim]Choose outcome:[/]\n"
                    "  [cyan]1[/]  → Player 1 advances\n"
                    "  [cyan]2[/]  → Player 2 advances\n"
                    "  [cyan]0[/]  → Neither advances\n"
                    "  [cyan]-1[/] → Both advance\n"
                )

                while True:
                    try:
                        choice = int(console.input("[bold]Your choice → [/]").strip())
                        if choice in {1, 2, 0, -1}:
                            break
                    except ValueError:
                        pass

                    console.print("[red]Invalid input.[/]")

                match choice:
                    case 1:
                        match_winner = p1_name
                        population.pop(player_2, None)
                    case 2:
                        match_winner = p2_name
                        population.pop(player_1, None)
                    case 0:
                        population.pop(player_1, None)
                        population.pop(player_2, None)
                    case -1:
                        pass

            round_matches.append(
                MatchResult(
                    match_number=match_num,
                    player_1=p1_name,
                    player_2=p2_name,
                    wins_1=wins_1,
                    wins_2=wins_2,
                    games=games_log,
                    winner=match_winner,
                )
            )

            time.sleep(0.4)

        tournament_rounds.append(
            RoundState(
                round_number=round_num,
                population=round_population,
                matches=round_matches,
            )
        )

        round_num += 1

    champion = next(iter(population))
    champ_name, champ_author = bot_label(champion)

    console.print(
        Panel.fit(
            f"[bold gold1]👑 CHAMPION 👑[/]\n\n"
            f"[bold cyan]{champ_name}[/]\n"
            f"[white]by {champ_author}[/]",
            border_style="gold1",
        )
    )

    os.makedirs("results", exist_ok=True)

    tournament_result = TournamentResult(
        started_at=datetime.utcnow(),
        champion=champ_name,
        rounds=tournament_rounds,
    )

    with open("results/tournament_results.json", "w") as f:
        f.write(tournament_result.model_dump_json(indent=2))

    return champion


# ==================== MAIN ====================

if __name__ == "__main__":
    console.clear()

    try:
        population = load_and_instantiate()

        if len(population) < 2:
            console.print("[red]Need at least 2 bots[/]")
            sys.exit(1)

        pair(population)

    except KeyboardInterrupt:
        console.print("\n[yellow]Tournament interrupted[/]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/]")
        raise
