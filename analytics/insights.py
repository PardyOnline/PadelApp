# Match-level cross-cutting analysis — separate from player_stats.py (player-grain) and
# team_stats.py (pair-grain) because insights operate on individual match rows and flag
# qualitative properties regardless of who played.
#   covers: close game detection, upset detection, match quality score

from .data import get_matches


# def get_close_matches():
#     """Flags matches decided by one break (e.g. 6-4) or that went to a deciding set."""
#     ...

# def get_upsets():
#     """Returns matches where the lower-rated team (by ELO) won."""
#     ...

# def get_match_quality_scores():
#     """Scores each match by competitiveness (margin, number of sets, ratings gap)."""
#     ...
