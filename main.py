import os
import sys
import random
import importlib.util
import inspect
from pathlib import Path
from typing import Type, List, Any, Optional
from datetime import datetime
import time
import json

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from pydantic import BaseModel

import pingv4


# ==================== CONFIG ====================

SUBMISSION_PATH = "submissions"
POPULATION_FILE = "population.txt"
RESULTS_FILE = "results/tournament_results.json"

BOT_CLASS = pingv4.AbstractBot
IGNORE = ["__init__.py"]

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
    champion: Optional[str]
    rounds: List[RoundState]


# ==================== HELPERS ====================

def bot_label(bot_cls):
    try:
        bot = bot_cls(player=pingv4.CellState.Red)
        return (
            getattr(bot, "strategy_name", bot_cls.__name__),
            getattr(bot, "author_name", "Unknown"),
            getattr(bot, "author_netid", bot_cls.__name__),
        )
    except Exception:
        return bot_cls.__name__, "Unknown", bot_cls.__name__


def read_population_file(path: str) -> List[str]:
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [l.strip() for l in f if l.strip()]


def write_population_file(population: dict[type[Any], str]):
    with open(POPULATION_FILE, "w") as f:
        for filename in population.values():
            f.write(f"{filename}\n")


def load_or_create_tournament() -> TournamentResult:
    if not os.path.exists(RESULTS_FILE) or os.path.getsize(RESULTS_FILE) == 0:
        return TournamentResult(
            started_at=datetime.utcnow(),
            champion=None,
            rounds=[],
        )

    with open(RESULTS_FILE) as f:
        return TournamentResult.model_validate(json.load(f))


def dump_tournament(tournament: TournamentResult):
    os.makedirs("results", exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        f.write(tournament.model_dump_json(indent=2))


# ==================== LOADER ====================

def load_and_instantiate(
    directory: str = SUBMISSION_PATH,
    base_class: Type = BOT_CLASS,
    exclude_files: List[str] = IGNORE,
) -> dict[type[Any], str]:

    directory_path = Path(directory)
    requested_files = read_population_file(POPULATION_FILE)

    py_files = (
        [directory_path / f for f in requested_files]
        if requested_files
        else list(directory_path.glob("*.py"))
    )

    population: dict[type[Any], str] = {}

    with console.status("[bold cyan]Loading bot submissions...", spinner="dots"):
        for py_file in py_files:
            if not py_file.exists() or py_file.name in exclude_files:
                continue

            spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
            if not spec or not spec.loader:
                continue

            module = importlib.util.module_from_spec(spec)
            sys.modules[py_file.stem] = module
            spec.loader.exec_module(module)

            for _, obj in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(obj, base_class)
                    and obj is not base_class
                    and obj.__module__ == py_file.stem
                ):
                    population[obj] = py_file.name
                    strat, author, netid = bot_label(obj)
                    console.print(
                        f"  ✓ Loaded [bold green]{strat}[/] "
                        f"by [cyan]{author}[/] ([magenta]{netid}[/])"
                    )

    write_population_file(population)
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


def display_game_result(game_num, winner):
    if winner:
        strat, _, netid = bot_label(winner)
        console.print(f"  Game {game_num}: [bold green]{strat}[/] ([magenta]{netid}[/])")
    else:
        console.print(f"  Game {game_num}: [bold yellow]Draw[/]")


def display_match_winner(winner, score):
    strat, _, netid = bot_label(winner)
    console.print(
        Panel(
            f"[bold green]{strat}[/] ([magenta]{netid}[/]) wins the match! ({score})",
            border_style="green",
        )
    )


# ==================== TOURNAMENT ====================

def pair(population: dict[type[pingv4.AbstractBot], str]):

    tournament = load_or_create_tournament()
    round_num = len(tournament.rounds) + 1

    console.print(
        Panel.fit(
            "[bold cyan]🏆 CONNECT 4 BOT TOURNAMENT 🏆[/]\n"
            f"[white]Starting with {len(population)} competitors[/]",
            border_style="cyan",
        )
    )

    while len(population) > 1:
        round_state = RoundState(
            round_number=round_num,
            population=[],
            matches=[],
        )

        tournament.rounds.append(round_state)
        dump_tournament(tournament)  # ← round exists on disk immediately

        bot_classes = list(population.keys())

        if len(bot_classes) % 2 == 1:
            console.print("[yellow]Odd number of bots - adding RandomBot[/]\n")
            population[pingv4.RandomBot] = "RandomBot"
            bot_classes.append(pingv4.RandomBot)

        random.shuffle(bot_classes)
        pairs = list(zip(bot_classes[::2], bot_classes[1::2]))

        for match_num, (p1, p2) in enumerate(pairs, 1):
            console.print(f"\n[bold]Match {match_num}/{len(pairs)}[/]")
            display_matchup(p1, p2, round_num)

            wins_1 = wins_2 = games_played = 0
            games: List[GameResult] = []

            while games_played < 3 and wins_1 < 2 and wins_2 < 2:
                game = pingv4.Connect4Game(player1=p1, player2=p2)
                game.run()

                winner = None
                match game.winner:
                    case 1:
                        wins_1 += 1
                        winner = p1
                    case 2:
                        wins_2 += 1
                        winner = p2

                display_game_result(games_played + 1, winner)
                games.append(
                    GameResult(
                        game_number=games_played + 1,
                        winner=bot_label(winner)[0] if winner else None,
                    )
                )
                games_played += 1

            p1_strat, _, p1_id = bot_label(p1)
            p2_strat, _, p2_id = bot_label(p2)

            match_winner = None

            if wins_1 > wins_2:
                match_winner = f"{p1_strat} ({p1_id})"
                display_match_winner(p1, f"{wins_1}-{wins_2}")
                population.pop(p2, None)

            elif wins_2 > wins_1:
                match_winner = f"{p2_strat} ({p2_id})"
                display_match_winner(p2, f"{wins_2}-{wins_1}")
                population.pop(p1, None)

            else:
                population.pop(p1, None)
                population.pop(p2, None)

            round_state.matches.append(
                MatchResult(
                    match_number=match_num,
                    player_1=f"{p1_strat} ({p1_id})",
                    player_2=f"{p2_strat} ({p2_id})",
                    wins_1=wins_1,
                    wins_2=wins_2,
                    games=games,
                    winner=match_winner,
                )
            )

            round_state.population = list(population.values())
            write_population_file(population)
            dump_tournament(tournament)  # ← after each match

            time.sleep(0.4)

        round_num += 1

    champion = next(iter(population))
    strat, _, netid = bot_label(champion)
    tournament.champion = f"{strat} ({netid})"
    dump_tournament(tournament)

    console.print(
        Panel.fit(
            f"[bold gold1]👑 CHAMPION 👑[/]\n\n"
            f"[bold cyan]{strat}[/]",
            border_style="gold1",
        )
    )

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
