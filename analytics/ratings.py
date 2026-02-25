# All rating model implementations in one place — ELO, TrueSkill, duo ELO, form index.
# Centralised here because models share helper utilities (margin scaling, decay functions)
# and cross-reference each other (e.g. duo ELO seeds from player ELO).
#   covers: TrueSkill, regularised ELO + log margin, opponent-adjusted ELO, duo ELO, form index

from .data import get_matches


def get_elo_ratings(initial_elo=1000, k_factor=32):
    """Computes per-player ELO from 2v2 match history."""
    df = get_matches()
    if df.empty:
        return []

    ratings = {}
    records = {}

    def _ensure_player(name):
        if not name:
            return
        if name not in ratings:
            ratings[name] = float(initial_elo)
            records[name] = {'matches': 0, 'wins': 0}

    for _, row in df.iterrows():
        t1_names = [row['team1_player1'], row['team1_player2']]
        t2_names = [row['team2_player1'], row['team2_player2']]
        winner = int(row['winner_team'])

        for name in t1_names + t2_names:
            _ensure_player(name)

        team1_elo = (ratings[t1_names[0]] + ratings[t1_names[1]]) / 2
        team2_elo = (ratings[t2_names[0]] + ratings[t2_names[1]]) / 2

        expected_t1 = 1 / (1 + 10 ** ((team2_elo - team1_elo) / 400))
        expected_t2 = 1 - expected_t1

        actual_t1 = 1.0 if winner == 1 else 0.0
        actual_t2 = 1.0 if winner == 2 else 0.0

        delta_t1 = k_factor * (actual_t1 - expected_t1)
        delta_t2 = k_factor * (actual_t2 - expected_t2)

        for name in t1_names:
            ratings[name] += delta_t1
            records[name]['matches'] += 1
            if winner == 1:
                records[name]['wins'] += 1

        for name in t2_names:
            ratings[name] += delta_t2
            records[name]['matches'] += 1
            if winner == 2:
                records[name]['wins'] += 1

    result = []
    for player, elo in ratings.items():
        matches = records[player]['matches']
        wins = records[player]['wins']
        losses = matches - wins
        result.append({
            'player': player,
            'elo': round(elo),
            'matches': matches,
            'wins': wins,
            'losses': losses,
        })

    result.sort(key=lambda x: x['elo'], reverse=True)
    return result


def get_trueskill_ratings():
    """Computes TrueSkill ratings from CSV match history with margin-of-victory scaling."""
    try:
        import trueskill
    except ImportError:
        return []

    df = get_matches()
    if df.empty:
        return []

    env = trueskill.TrueSkill(draw_probability=0.0)
    ratings = {}

    def _ensure_player(name):
        if name and name not in ratings:
            ratings[name] = env.Rating()

    def _margin_scale(set_scores, k=0.1):
        """Returns 1.0 + k * (avg_abs_set_margin / 6)."""
        margins = [abs(s[0] - s[1]) for s in set_scores]
        if not margins:
            return 1.0
        return 1.0 + k * (sum(margins) / len(margins) / 6)

    for _, row in df.iterrows():
        t1_names = [row['team1_player1'], row['team1_player2']]
        t2_names = [row['team2_player1'], row['team2_player2']]
        for name in t1_names + t2_names:
            _ensure_player(name)

        set_scores = [
            (int(row['set1_team1']), int(row['set1_team2'])),
            (int(row['set2_team1']), int(row['set2_team2'])),
        ]
        s3t1, s3t2 = row.get('set3_team1', ''), row.get('set3_team2', '')
        if s3t1 != '' and s3t2 != '':
            try:
                set_scores.append((int(s3t1), int(s3t2)))
            except (ValueError, TypeError):
                pass

        t1_sets = sum(1 for a, b in set_scores if a > b)
        t2_sets = sum(1 for a, b in set_scores if b > a)
        ranks = [0, 1] if t1_sets > t2_sets else [1, 0]

        scale = _margin_scale(set_scores)
        t1_old = [ratings[n] for n in t1_names]
        t2_old = [ratings[n] for n in t2_names]

        new_t1, new_t2 = env.rate([t1_old, t2_old], ranks=ranks)

        # Apply margin scale to the mu delta only to avoid inflation
        for i, name in enumerate(t1_names):
            old_mu = ratings[name].mu
            new_mu = old_mu + (new_t1[i].mu - old_mu) * scale
            ratings[name] = trueskill.Rating(mu=new_mu, sigma=new_t1[i].sigma)

        for i, name in enumerate(t2_names):
            old_mu = ratings[name].mu
            new_mu = old_mu + (new_t2[i].mu - old_mu) * scale
            ratings[name] = trueskill.Rating(mu=new_mu, sigma=new_t2[i].sigma)

    result = []
    for player, r in ratings.items():
        if not player:
            continue
        conservative = round(r.mu - 3 * r.sigma, 2)
        result.append({
            'player': player,
            'mu': round(r.mu, 2),
            'sigma': round(r.sigma, 2),
            'conservative': conservative,
        })

    result.sort(key=lambda x: x['conservative'], reverse=True)
    return result
