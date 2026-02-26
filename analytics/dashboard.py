# Aggregation layer for Flask — the only module that main.py/routes should call directly.
# All other modules are implementation details. Adding a new stat means adding a function
# here that calls the relevant module; main.py and render_template stay untouched.
#   covers: assembles all dicts/lists passed to render_template in main.py

from .player_stats import basic_player_stats
from .ratings import get_trueskill_ratings
from .data import get_raw_csv, get_matches
# from .team_stats import get_partnership_stats
# from .history import get_monthly_stats
# from .insights import get_close_matches


def get_all_dashboard_data():
    """
    Single call to get everything needed for all routes.
    Merges TrueSkill ratings (mu, sigma, conservative) with per-player win/loss stats
    into a single unified stats list sorted by conservative TrueSkill score.
    """
    player_stats, recent_matches, all_players = basic_player_stats()
    trueskill_ratings = get_trueskill_ratings()  # [{player, mu, sigma, conservative}, ...]

    # Index TrueSkill data by player name for fast lookup
    ts_lookup = {r['player']: r for r in trueskill_ratings}

    # Index win/loss data by player name
    ps_lookup = {p['player']: p for p in player_stats}

    # Merge: every player in trueskill_ratings gets their win/loss fields attached
    merged = []
    for player, ts in ts_lookup.items():
        ps = ps_lookup.get(player, {'matches': 0, 'wins': 0, 'losses': 0, 'winRate': 0.0})
        merged.append({
            'player': player,
            'mu': ts['mu'],
            'sigma': ts['sigma'],
            'conservative': ts['conservative'],
            'matches': ps['matches'],
            'wins': ps['wins'],
            'losses': ps['losses'],
            'winRate': ps['winRate'],
        })

    # Sort by TrueSkill conservative score (best first)
    merged.sort(key=lambda x: x['conservative'], reverse=True)

    df = get_matches()
    total_matches = len(df) if not df.empty else 0

    top_ranked_player = merged[0]['player'] if merged else '-'
    top_ranked_score = merged[0]['conservative'] if merged else None

    return {
        'stats': merged,
        'recent_matches': recent_matches,
        'all_players': all_players,
        'raw_csv': get_raw_csv(),
        'chart_labels': [s['player'] for s in merged],
        'chart_data': [s['winRate'] for s in merged],
        'total_matches': total_matches,
        'top_ranked_player': top_ranked_player,
        'top_ranked_score': top_ranked_score,
        # 'partnership_stats': get_partnership_stats(),
        # 'close_matches': get_close_matches(),
    }
