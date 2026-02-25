# Aggregation layer for Flask — the only module that main.py/routes should call directly.
# All other modules are implementation details. Adding a new stat means adding a function
# here that calls the relevant module; main.py and render_template stay untouched.
#   covers: assembles all dicts/lists passed to render_template in main.py

from .player_stats import basic_player_stats
from .ratings import get_trueskill_ratings
# from .team_stats import get_partnership_stats
# from .history import get_monthly_stats, get_elo_history
# from .insights import get_close_matches


def get_all_dashboard_data():
    """
    Single call to get everything needed for the index route.
    Expand this as new tabs/sections are added to the frontend.
    """
    stats, recent_matches, all_players = basic_player_stats()
    trueskill_stats = get_trueskill_ratings()

    return {
        'stats': stats,
        'recent_matches': recent_matches,
        'all_players': all_players,
        'trueskill_stats': trueskill_stats,
        # 'partnership_stats': get_partnership_stats(),
        # 'close_matches': get_close_matches(),
    }
