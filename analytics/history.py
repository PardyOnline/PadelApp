# Time-series and trend analysis — separate from player_stats.py because these functions
# require sorted, windowed data (grouped by date/month) rather than simple aggregations.
# Keeping time-based queries here makes it easy to swap in a proper DB later.
#   covers: ELO over time, improvement slope, monthly breakdowns, player of the month, closest match

from .data import get_matches


# def get_elo_history():
#     """Returns each player's ELO rating after every match they played, in chronological order."""
#     ...

# def get_improvement_slope(player: str):
#     """Linear regression over a player's ELO history to measure improvement trend."""
#     ...

# def get_monthly_stats():
#     """Aggregates wins, losses, and match counts grouped by calendar month."""
#     ...

# def get_player_of_the_month():
#     """Returns the player with the highest win rate in the most recent complete month."""
#     ...

# def get_closest_matches(top_n=5):
#     """Returns the n matches decided by the smallest combined set-score margin."""
#     ...
