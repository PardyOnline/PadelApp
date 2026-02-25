# Per-player aggregates — kept separate from team_stats.py because the grain is
# player-level (one row per player), whereas team_stats.py works on pairs/combinations.
# Time-series queries live in history.py and match-level flags in insights.py to keep
# this file focused purely on cumulative per-player numbers.
#   covers: wins/losses, set breakdown, win%, H2H, margins, recent form, win streak, nemesis

from .data import get_matches


def basic_player_stats():
    """Aggregates per-player win/loss stats for the dashboard leaderboard."""
    df = get_matches()
    if df.empty:
        return [], [], []

    stats = {}

    for _, row in df.iterrows():
        t1 = [row['team1_player1'], row['team1_player2']]
        t2 = [row['team2_player1'], row['team2_player2']]
        winner = row['winner_team']

        for p in t1:
            if p not in stats: stats[p] = {'matches': 0, 'wins': 0}
            stats[p]['matches'] += 1
            if winner == 1: stats[p]['wins'] += 1

        for p in t2:
            if p not in stats: stats[p] = {'matches': 0, 'wins': 0}
            stats[p]['matches'] += 1
            if winner == 2: stats[p]['wins'] += 1

    stat_list = []
    for player, data in stats.items():
        wins = data['wins']
        matches = data['matches']
        losses = matches - wins
        win_rate = round((wins / matches) * 100, 1)
        stat_list.append({
            'player': player,
            'matches': matches,
            'wins': wins,
            'losses': losses,
            'winRate': win_rate,
        })

    stat_list.sort(key=lambda x: (x['winRate'], x['matches']), reverse=True)

    recent = df.sort_values(by='date', ascending=False).head(10).to_dict('records')
    all_players = sorted(list(stats.keys()))

    return stat_list, recent, all_players
