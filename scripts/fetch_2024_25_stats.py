"""
fetch_2024_25_stats.py

Fetches 2024-25 NBA player stats (Regular Season + Playoffs) via nba_api,
formats them to match the existing kaggle_data/nba.csv schema, and saves
a combined file ready for the salary prediction pipeline.

Usage:
    pip install nba_api
    python scripts/fetch_2024_25_stats.py
"""

import time
import numpy as np
import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats

# ── Config ────────────────────────────────────────────────────────────────────
SEASON          = "2024-25"
EXISTING_CSV    = "../data/kaggle_data/nba.csv"
OUTPUT_CSV      = "../data/kaggle_data/nba_with_2024_25.csv"

# Season type labels: nba_api value → nba.csv value
SEASON_TYPE_MAP = {
    "Regular Season": "Regular%20Season",
    "Playoffs":       "Playoffs",
}

# Counting stats that can be summed across teams for traded players
COUNTING_COLS = [
    "GP", "MIN", "FGM", "FGA", "FG3M", "FG3A",
    "FTM", "FTA", "OREB", "DREB", "REB",
    "AST", "STL", "BLK", "TOV", "PF", "PTS",
]

# Final column order matching nba.csv
SCHEMA_COLS = [
    "year", "Season_type", "PLAYER_ID", "RANK", "PLAYER",
    "TEAM_ID", "TEAM", "GP", "MIN", "FGM", "FGA", "FG_PCT",
    "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA", "FT_PCT",
    "OREB", "DREB", "REB", "AST", "STL", "BLK", "TOV", "PF",
    "PTS", "EFF", "AST_TOV", "STL_TOV",
]
# ─────────────────────────────────────────────────────────────────────────────


def fetch_raw(season_type_label: str) -> pd.DataFrame:
    """Pull season totals from nba_api for all players."""
    print(f"  Fetching {season_type_label}...")
    endpoint = leaguedashplayerstats.LeagueDashPlayerStats(
        season=SEASON,
        season_type_all_star=season_type_label,
        per_mode_detailed="Totals",
        timeout=60,
    )
    time.sleep(1)  # avoid rate-limit
    return endpoint.get_data_frames()[0]


def aggregate_traded_players(df: pd.DataFrame) -> pd.DataFrame:
    """
    nba_api returns one row per player-team for traded players.
    The existing nba.csv has one row per player (season totals).
    This function sums counting stats and recomputes rate stats,
    keeping the last team the player appeared for.
    """
    if not df.duplicated("PLAYER_ID").any():
        return df

    # Sum all counting stats across teams
    totals = (
        df.groupby(["PLAYER_ID", "PLAYER"], as_index=False)[COUNTING_COLS]
        .sum()
    )

    # Recompute rate stats from totals (avoids averaging percentages)
    totals["FG_PCT"]  = np.where(totals["FGA"]  > 0, totals["FGM"]  / totals["FGA"],  0)
    totals["FG3_PCT"] = np.where(totals["FG3A"] > 0, totals["FG3M"] / totals["FG3A"], 0)
    totals["FT_PCT"]  = np.where(totals["FTA"]  > 0, totals["FTM"]  / totals["FTA"],  0)

    # Use the last team the player was on (highest GP row per player)
    last_team = (
        df.sort_values("GP")
        .groupby("PLAYER_ID")[["TEAM_ID", "TEAM"]]
        .last()
        .reset_index()
    )
    return totals.merge(last_team, on="PLAYER_ID")


def compute_derived(df: pd.DataFrame) -> pd.DataFrame:
    """Add EFF, AST_TOV, STL_TOV to match nba.csv schema."""
    df["EFF"] = (
        df["PTS"] + df["REB"] + df["AST"] + df["STL"] + df["BLK"]
        - (df["FGA"] - df["FGM"])
        - (df["FTA"] - df["FTM"])
        - df["TOV"]
    )
    df["AST_TOV"] = np.where(df["TOV"] > 0, (df["AST"] / df["TOV"]).round(6), 0)
    df["STL_TOV"] = np.where(df["TOV"] > 0, (df["STL"] / df["TOV"]).round(6), 0)
    return df


def format_to_schema(df: pd.DataFrame, season_type_label: str) -> pd.DataFrame:
    """Rename columns, add metadata, rank, and select final columns."""
    df = df.rename(columns={"PLAYER_NAME": "PLAYER", "TEAM_ABBREVIATION": "TEAM"})
    df["year"]        = SEASON
    df["Season_type"] = SEASON_TYPE_MAP[season_type_label]
    df["RANK"]        = df["EFF"].rank(ascending=False, method="min").astype(int)
    return df[SCHEMA_COLS]


def main():
    # ── Fetch ──────────────────────────────────────────────────────────────────
    print(f"Fetching {SEASON} stats from NBA API...")
    rs_raw = fetch_raw("Regular Season")
    po_raw = fetch_raw("Playoffs")

    # ── Clean & format ─────────────────────────────────────────────────────────
    rs = format_to_schema(compute_derived(aggregate_traded_players(rs_raw)), "Regular Season")
    po = format_to_schema(compute_derived(aggregate_traded_players(po_raw)), "Playoffs")

    print(f"  Regular Season: {len(rs)} players")
    print(f"  Playoffs:       {len(po)} players")

    new_data = pd.concat([rs, po], ignore_index=True)

    # ── Append to existing data ─────────────────────────────────────────────────
    existing = pd.read_csv(EXISTING_CSV)
    print(f"\nExisting data: {len(existing)} rows across {existing['year'].nunique()} seasons")

    # Guard against re-running: drop any existing 2024-25 rows before appending
    existing = existing[existing["year"] != SEASON]

    combined = pd.concat([existing, new_data], ignore_index=True)
    combined.to_csv(OUTPUT_CSV, index=False)

    print(f"Combined data: {len(combined)} rows across {combined['year'].nunique()} seasons")
    print(f"\nSaved to {OUTPUT_CSV}")
    print("Update your notebook to load this file instead of nba.csv.")


if __name__ == "__main__":
    main()
