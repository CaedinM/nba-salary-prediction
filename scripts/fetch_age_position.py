"""
fetch_age_position.py

Fetches age and position for all players in a given NBA season via nba_api.
Uses leaguedashplayerbiostats (one call) for age, PlayerIndex (one call) for
position, and falls back to commonplayerinfo for players not in PlayerIndex
(typically waived/G-League players no longer on an active roster).

Saves: data/player_age_position_{season_slug}.csv
  Columns: PLAYER_ID, PLAYER, Age, Pos

Position is normalized to G / F / C to match model feature vocabulary.

Usage:
    python scripts/fetch_age_position.py                  # defaults to 2024-25
    python scripts/fetch_age_position.py --season 2025-26
"""

import argparse
import time
import pandas as pd
from nba_api.stats.endpoints import (
    leaguedashplayerbiostats,
    playerindex,
    commonplayerinfo,
)

# Map all NBA API position strings → simplified G / F / C
POS_MAP = {
    "G": "G", "F": "F", "C": "C",
    "G-F": "G", "F-G": "F",
    "F-C": "F", "C-F": "C",
    "Guard": "G", "Forward": "F", "Center": "C",
    "Guard-Forward": "G", "Forward-Guard": "F",
    "Forward-Center": "F", "Center-Forward": "C",
}


def fetch_bio(season: str) -> pd.DataFrame:
    print(f"  Fetching bio stats (age) for {season}...")
    bio = leaguedashplayerbiostats.LeagueDashPlayerBioStats(
        season=season, season_type_all_star="Regular Season", timeout=60
    ).get_data_frames()[0]
    time.sleep(1)
    return bio[["PLAYER_ID", "PLAYER_NAME", "AGE"]].copy()


def fetch_positions_bulk() -> pd.DataFrame:
    """PlayerIndex (current season) returns positions for all active-roster players."""
    print("  Fetching PlayerIndex (positions)...")
    pi = playerindex.PlayerIndex(timeout=60).get_data_frames()[0]
    time.sleep(1)
    pi = pi.rename(columns={"PERSON_ID": "PLAYER_ID"})
    return pi[["PLAYER_ID", "POSITION"]].copy()


def fetch_positions_individual(player_ids: list) -> dict:
    """Fall back to commonplayerinfo for players not in PlayerIndex."""
    print(f"  Fetching commonplayerinfo for {len(player_ids)} unlisted players...")
    lookup = {}
    for i, pid in enumerate(player_ids):
        try:
            info = commonplayerinfo.CommonPlayerInfo(
                player_id=pid, timeout=30
            ).get_data_frames()[0]
            lookup[pid] = info["POSITION"].iloc[0] if len(info) else ""
        except Exception as e:
            lookup[pid] = ""
            print(f"    Warning: could not fetch player {pid}: {e}")
        if i % 25 == 0 and i > 0:
            print(f"    {i}/{len(player_ids)} done...")
        time.sleep(0.6)
    return lookup


def main(season: str):
    season_slug = season.replace("-", "_")
    output_path = f"../data/player_age_position_{season_slug}.csv"

    bio = fetch_bio(season)
    pi = fetch_positions_bulk()

    merged = bio.merge(pi, on="PLAYER_ID", how="left")

    # Fill missing positions via individual API calls
    missing_ids = merged.loc[merged["POSITION"].isna(), "PLAYER_ID"].tolist()
    if missing_ids:
        fallback = fetch_positions_individual(missing_ids)
        merged.loc[merged["POSITION"].isna(), "POSITION"] = (
            merged.loc[merged["POSITION"].isna(), "PLAYER_ID"].map(fallback)
        )

    # Normalize positions
    merged["Pos"] = merged["POSITION"].map(POS_MAP).fillna("F")
    merged["Age"] = merged["AGE"].astype(float)
    merged = merged.rename(columns={"PLAYER_NAME": "PLAYER"})

    out = merged[["PLAYER_ID", "PLAYER", "Age", "Pos"]]
    out.to_csv(output_path, index=False)

    print(f"\nSaved {len(out)} players → {output_path}")
    print(f"Position distribution: {out['Pos'].value_counts().to_dict()}")
    print(f"Age range: {out['Age'].min():.0f} – {out['Age'].max():.0f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", default="2024-25", help="NBA season (e.g. 2024-25)")
    args = parser.parse_args()
    main(args.season)
