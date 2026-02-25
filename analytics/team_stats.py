# Doubles / partnership analytics — separate from player_stats.py because queries here
# operate on player *pairs* (2-key combinations), requiring different aggregation logic.
# Optimal pairing and heatmap data live here since they are inherently team-level outputs.
#   covers: partner win rates, chemistry rating, rivalries, fairest teams, pairing heatmap

from .data import get_matches


# Example structure for future functions:
#
# def get_partnership_stats():
#     """Win rates for every pair of players who have partnered together."""
#     df = get_matches()
#     ...
#
# def get_best_partnerships(min_matches=3):
#     """Returns partnerships with the highest win rate (min_matches threshold)."""
#     ...
#
# def get_head_to_head(team1: list, team2: list):
#     """Returns W/L record between two specific pairs."""
#     ...
