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
        strategy = getattr(bot, "strategy_name", bot_cls.__name__)
        author = getattr(bot, "author_name", "Unknown")
        netid = getattr(bot, "author_netid", "unknown")
        return strategy, author, netid
    except Exception:
        return bot_cls.__name__, "Unknown", "unknown"


def read_population_file(path: str) -> List[str]:
    if not os.path.exists(path):
        return []

    with open(path, "r") as f:
        lines = [line.strip() for line in f.readlines()]

    # format: filename | netid
    return [line.split("|")[0].strip() for line in lines if line]


def append_population_file(path: str, filename: str, netid: str):
    with open(path, "a") as f:
        f.write(f"{filename} | {netid}\n")


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
                        strat, author, netid = bot_label(obj)
                        console.print(
                            f"  ✓ Loaded [bold green]{strat}[/] "
                            f"by [cyan]{author}[/] ([magenta]{netid}[/])"
                        )

    console.print(f"\n[bold]Total bots loaded:[/] [green]{len(population)}[/]\n")
    return population


# ==================== DISPLAY ====================


def display_matchup(player_1, player_2, round_num):
    table = Table(show_header=False, box=box.DOUBLE_EDGE, border_style="bright_blue")
    table.add_column(justify="center")
    table.add_column(justify="center")
    table.add_column(justify="center")

    s1, a1, n1 = bot_label(player_1)
    s2, a2, n2 = bot_label(player_2)

    table.add_row(
        f"{s1}\n({a1} | {n1})",
        "VS",
        f"{s2}\n({a2} | {n2})",
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
        strat, _, netid = bot_label(winner_class)
        console.print(
            f"  Game {game_num}: [bold green]{strat}[/] "
            f"([magenta]{netid}[/]) wins!"
        )
    else:
        console.print(f"  Game {game_num}: [bold yellow]Draw[/]")


def display_match_winner(winner, score):
    strat, _, netid = bot_label(winner)
    console.print(
        Panel(
            f"[bold green]{strat}[/] ([magenta]{netid}[/]) "
            f"wins the match! ({score})",
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

            p1_strat, _, p1_netid = bot_label(player_1)
            p2_strat, _, p2_netid = bot_label(player_2)

            match_winner = None
            if wins_1 > wins_2:
                match_winner = f"{p1_strat} ({p1_netid})"
                display_match_winner(player_1, f"{wins_1}-{wins_2}")
                append_population_file(
                    POPULATION_FILE, population[player_1], p1_netid
                )
                population.pop(player_2, None)

            elif wins_2 > wins_1:
                match_winner = f"{p2_strat} ({p2_netid})"
                display_match_winner(player_2, f"{wins_2}-{wins_1}")
                append_population_file(
                    POPULATION_FILE, population[player_2], p2_netid
                )
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
                        match_winner = f"{p1_strat} ({p1_netid})"
                        append_population_file(
                            POPULATION_FILE, population[player_1], p1_netid
                        )
                        population.pop(player_2, None)
                    case 2:
                        match_winner = f"{p2_strat} ({p2_netid})"
                        append_population_file(
                            POPULATION_FILE, population[player_2], p2_netid
                        )
                        population.pop(player_1, None)
                    case 0:
                        population.pop(player_1, None)
                        population.pop(player_2, None)
                    case -1:
                        append_population_file(
                            POPULATION_FILE, population[player_1], p1_netid
                        )
                        append_population_file(
                            POPULATION_FILE, population[player_2], p2_netid
                        )

            round_matches.append(
                MatchResult(
                    match_number=match_num,
                    player_1=f"{p1_strat} ({p1_netid})",
                    player_2=f"{p2_strat} ({p2_netid})",
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
    champ_strat, champ_author, champ_netid = bot_label(champion)

    console.print(
        Panel.fit(
            f"[bold gold1]👑 CHAMPION 👑[/]\n\n"
            f"[bold cyan]{champ_strat}[/]\n"
            f"[white]{champ_author}[/] ([magenta]{champ_netid}[/])",
            border_style="gold1",
        )
    )

    os.makedirs("results", exist_ok=True)

    tournament_result = TournamentResult(
        started_at=datetime.utcnow(),
        champion=f"{champ_strat} ({champ_netid})",
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
