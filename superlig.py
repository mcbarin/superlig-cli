#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Turkish Super Lig CLI - Terminal client for Turkish Football League standings
"""
import re
import requests
import click
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich import box

BASE_URL = "https://www.soccerstats.com"
LEAGUE_URL = f"{BASE_URL}/latest.asp?league=turkey"

console = Console()


def get_page(url):
    """Fetch a webpage and return BeautifulSoup object."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error fetching page: {e}[/red]")
        return None


def get_standings():
    """Scrape league standings from soccerstats.com."""
    soup = get_page(LEAGUE_URL)
    if not soup:
        return None

    standings = []

    # Find the standings table - look for tables with ranking data
    tables = soup.find_all('table')

    for table in tables:
        rows = table.find_all('tr')
        header_found = False
        header_indices = {}

        # First pass: find header row and column indices
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 5:
                continue

            header_text = ' '.join([cell.get_text(strip=True).lower() for cell in cells])

            # Check if this looks like a header row
            if any(keyword in header_text for keyword in ['gp', 'w', 'd', 'l', 'gf', 'ga', 'gd', 'pts', 'pos', 'team', 'played', 'won', 'drawn', 'lost', 'goals', 'points']):
                header_found = True
                # Map column names to indices
                for idx, cell in enumerate(cells):
                    cell_text = cell.get_text(strip=True).upper()
                    if cell_text == 'GP' or ('played' in cell_text.lower() and 'gp' not in header_indices):
                        header_indices['played'] = idx
                    elif cell_text == 'W' or ('won' in cell_text.lower() and 'wins' not in header_indices):
                        header_indices['wins'] = idx
                    elif cell_text == 'D' or ('draw' in cell_text.lower() and 'draws' not in header_indices):
                        header_indices['draws'] = idx
                    elif cell_text == 'L' or ('lost' in cell_text.lower() and 'losses' not in header_indices):
                        header_indices['losses'] = idx
                    elif cell_text == 'GF' or ('for' in cell_text.lower() and 'goals_for' not in header_indices):
                        header_indices['goals_for'] = idx
                    elif cell_text == 'GA' or ('against' in cell_text.lower() and 'goals_against' not in header_indices):
                        header_indices['goals_against'] = idx
                    elif cell_text == 'GD' or ('diff' in cell_text.lower() and 'goal_diff' not in header_indices):
                        header_indices['goal_diff'] = idx
                    elif cell_text == 'PTS' or ('points' in cell_text.lower() and 'points' not in header_indices):
                        header_indices['points'] = idx
                    elif ('pos' in cell_text.lower() or 'rank' in cell_text.lower() or cell_text.isdigit()) and 'rank' not in header_indices:
                        header_indices['rank'] = idx
                    elif 'team' in cell_text.lower() and 'team' not in header_indices:
                        header_indices['team'] = idx
                break

        if not header_found:
            continue

        # Second pass: extract data rows
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < max(header_indices.values(), default=5):
                continue

            # Skip header row
            first_cell = cells[0].get_text(strip=True).lower()
            if any(keyword in first_cell for keyword in ['pos', 'team', 'rank', '#']):
                continue

            try:
                # Extract rank
                rank_idx = header_indices.get('rank', 0)
                rank_text = cells[rank_idx].get_text(strip=True)
                if not rank_text.isdigit():
                    continue
                rank = int(rank_text)

                # Extract team name
                team_idx = header_indices.get('team', 1)
                team_name = cells[team_idx].get_text(strip=True)
                if not team_name or len(team_name) < 3:
                    continue

                # Extract stats
                def get_stat(key, default_idx):
                    idx = header_indices.get(key, default_idx)
                    if idx < len(cells):
                        stat_text = cells[idx].get_text(strip=True)
                        stat_text = re.sub(r'[^\d\-+]', '', stat_text)
                        try:
                            return int(stat_text) if stat_text else 0
                        except:
                            return 0
                    return 0

                played = get_stat('played', 2)
                wins = get_stat('wins', 3)
                draws = get_stat('draws', 4)
                losses = get_stat('losses', 5)
                goals_for = get_stat('goals_for', 6)
                goals_against = get_stat('goals_against', 7)
                goal_diff = get_stat('goal_diff', 8)
                if goal_diff == 0:
                    goal_diff = goals_for - goals_against
                points = get_stat('points', 9)

                if team_name and played > 0:
                    standings.append({
                        'rank': rank,
                        'team': team_name,
                        'played': played,
                        'wins': wins,
                        'draws': draws,
                        'losses': losses,
                        'goals_for': goals_for,
                        'goals_against': goals_against,
                        'goal_diff': goal_diff,
                        'points': points
                    })
            except Exception:
                continue

        if standings and len(standings) >= 10:
            break

    # Fallback: simpler parsing
    if not standings:
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) < 8:
                    continue

                try:
                    rank_text = cells[0].get_text(strip=True)
                    if not rank_text.isdigit():
                        continue

                    rank = int(rank_text)
                    team_name = cells[1].get_text(strip=True)

                    if team_name and len(team_name) > 2:
                        stats = []
                        for i in range(2, min(10, len(cells))):
                            stat_text = re.sub(r'[^\d\-+]', '', cells[i].get_text(strip=True))
                            try:
                                stats.append(int(stat_text) if stat_text else 0)
                            except:
                                stats.append(0)

                        while len(stats) < 8:
                            stats.append(0)

                        standings.append({
                            'rank': rank,
                            'team': team_name,
                            'played': stats[0],
                            'wins': stats[1],
                            'draws': stats[2],
                            'losses': stats[3],
                            'goals_for': stats[4],
                            'goals_against': stats[5],
                            'goal_diff': stats[6] if stats[6] != 0 else (stats[4] - stats[5]),
                            'points': stats[7]
                        })
                except:
                    continue

            if standings:
                break

    return standings if standings else None


def show_standings(standings_data):
    """Display league standings in a beautiful table."""
    if not standings_data:
        console.print("[yellow]Could not fetch league standings.[/yellow]")
        return

    table = Table(
        title="Turkish Super Lig - Standings",
        box=box.ROUNDED,
        header_style="bold yellow",
        title_style="bold yellow",
        show_header=True,
        border_style="yellow"
    )

    table.add_column("#", justify="center", style="cyan", width=3)
    table.add_column("Team", justify="left", style="white", min_width=20)
    table.add_column("GP", justify="center", style="cyan", width=3)
    table.add_column("W", justify="center", style="green", width=3)
    table.add_column("D", justify="center", style="yellow", width=3)
    table.add_column("L", justify="center", style="red", width=3)
    table.add_column("GF", justify="center", style="cyan", width=3)
    table.add_column("GA", justify="center", style="cyan", width=3)
    table.add_column("GD", justify="center", style="cyan", width=5)
    table.add_column("Pts", justify="center", style="bold green", width=3)

    for team_data in standings_data:
        rank = team_data.get('rank', 0)
        team = team_data.get('team', '')
        played = team_data.get('played', 0)
        wins = team_data.get('wins', 0)
        draws = team_data.get('draws', 0)
        losses = team_data.get('losses', 0)
        goals_for = team_data.get('goals_for', 0)
        goals_against = team_data.get('goals_against', 0)
        goal_diff = team_data.get('goal_diff', 0)
        points = team_data.get('points', 0)

        # Color code based on position
        rank_style = "cyan"
        if rank <= 3:
            rank_style = "bold green"
        elif rank >= 16:
            rank_style = "bold red"

        table.add_row(
            f"[{rank_style}]{rank}[/{rank_style}]",
            team,
            str(played),
            str(wins),
            str(draws),
            str(losses),
            str(goals_for),
            str(goals_against),
            f"{goal_diff:+d}",
            f"[bold]{points}[/bold]"
        )

    console.print()
    console.print(table)
    console.print()


@click.command()
@click.version_option(version="1.1.0", prog_name="superlig")
def main():
    """Turkish Super Lig CLI - Display league standings in your terminal."""
    standings = get_standings()
    show_standings(standings)


if __name__ == '__main__':
    main()
