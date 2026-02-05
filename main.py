import os
import sys
import random
import importlib.util
import inspect
from pathlib import Path
from typing import Type, List, Any, Optional
from collections import defaultdict
from datetime import datetime
import time

import matplotlib.pyplot as plt
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from pydantic import BaseModel

import pingv4


# ==================== CONFIG ====================

SUBMISSION_PATH = os.path.join("submissions")
BOT_CLASS = pingv4.AbstractBot
IGNORE = ['__init__.py']

console = Console()


# ==================== Pydantic MODELS ====================

class GameResult(BaseModel):
    game_number: int
    winner: Optional[str]  # None for draw


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
    """
    Match pingv4's printing exactly:
    '<strategy_name> by <author_name>'
    """
    try:
        bot = bot_cls(player=pingv4.CellState.Red)
        return bot.strategy_name, bot.author_name
    except Exception:
        return bot_cls.__name__, "Unknown"


# ==================== LOADER ====================

def load_and_instantiate(
    directory: str = SUBMISSION_PATH,
    base_class: Type = BOT_CLASS,
    exclude_files: List[str] = IGNORE,
) -> List[Any]:
    bots = []
    directory_path = Path(directory)

    with console.status("[bold cyan]Loading bot submissions...", spinner="dots"):
        for py_file in directory_path.glob("*.py"):
            if py_file.name in exclude_files:
                continue

            module_name = py_file.stem
            spec = importlib.util.spec_from_file_location(module_name, py_file)

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, base_class) and obj is not base_class:
                        if obj.__module__ == module_name:
                            bots.append(obj)
                            strat, author = bot_label(obj)
                            console.print(
                                f"  ✓ Loaded [bold green]{strat}[/] by [cyan]{author}[/]"
                            )

    console.print(f"\n[bold]Total bots loaded:[/] [green]{len(bots)}[/]\n")
    return bots


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
        console.print(f"  Game {game_num}: [bold green]{strat}[/] wins! 🎯")
    else:
        console.print(f"  Game {game_num}: [bold yellow]Draw[/] ⚖️")


def display_match_winner(winner, score):
    strat, _ = bot_label(winner)
    console.print(
        Panel(
            f"[bold green]{strat}[/] wins the match! ({score})",
            border_style="green",
        )
    )


# ==================== TOURNAMENT ====================

def pair(population: list[type[pingv4.AbstractBot]]):
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
        console.print(f"\n[bold yellow]{'='*70}[/]")
        console.print(f"[bold white]ROUND {round_num} - {len(population)} bots remaining[/]")
        console.print(f"[bold yellow]{'='*70}[/]\n")

        round_population = [bot_label(b)[0] for b in population]
        round_matches: List[MatchResult] = []

        if len(population) % 2 == 1:
            console.print("[yellow]Odd number of bots - adding RandomBot[/]\n")
            population.append(pingv4.RandomBot)

        random.shuffle(population)
        pairs = list(zip(population[::2], population[1::2]))

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
                population.remove(player_2)
            elif wins_2 > wins_1:
                match_winner = p2_name
                display_match_winner(player_2, f"{wins_2}-{wins_1}")
                population.remove(player_1)
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
            
                    console.print("[red]Invalid input. Enter 1, 2, 0, or -1.[/]")
            
                match choice:
                    case 1:
                        match_winner = p1_name
                        display_match_winner(player_1, f"{wins_1}-{wins_2}")
                        population.remove(player_2)
            
                    case 2:
                        match_winner = p2_name
                        display_match_winner(player_2, f"{wins_2}-{wins_1}")
                        population.remove(player_1)
            
                    case 0:
                        console.print("[red]Both players eliminated.[/]")
                        population.remove(player_1)
                        population.remove(player_2)
            
                    case -1:
                        console.print("[green]Both players advance.[/]")
            
                    case _:
                        console.print("[green]Both players advance.[/]")

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

    champion = population[0]
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

    generate_tournament_chart(tournament_rounds, champion)
    return champion


# ==================== STATS ====================

def generate_tournament_chart(rounds: List[RoundState], champion):
    win_counts = defaultdict(int)

    for rnd in rounds:
        for match in rnd.matches:
            if match.winner:
                win_counts[match.winner] += 1

    if not win_counts:
        return

    champ_name, _ = bot_label(champion)
    bots, wins = zip(*sorted(win_counts.items(), key=lambda x: x[1], reverse=True))

    colors = ["gold" if b == champ_name else "steelblue" for b in bots]

    plt.figure(figsize=(10, 6))
    plt.barh(bots, wins, color=colors)
    plt.xlabel("Wins")
    plt.title("🏆 Tournament Results")
    plt.tight_layout()
    plt.savefig("tournament_results.png", dpi=300)
    plt.show()


# ==================== MAIN ====================

if __name__ == "__main__":
    console.clear()

    try:
        bots = load_and_instantiate()

        if len(bots) < 2:
            console.print("[red]Need at least 2 bots[/]")
            sys.exit(1)

        pair(bots)

    except KeyboardInterrupt:
        console.print("\n[yellow]Tournament interrupted[/]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/]")
        raise
