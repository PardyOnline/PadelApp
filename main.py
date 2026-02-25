from flask import Flask, render_template, request, redirect, url_for, send_file
import trueskill
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'padel_secret_key'

# Setup Data directory
DATA_DIR = 'data'
DATA_FILE = os.path.join(DATA_DIR, 'matches.csv')
CSV_HEADER = "date,team1_player1,team1_player2,team2_player1,team2_player2,set1_team1,set1_team2,set2_team1,set2_team2,set3_team1,set3_team2,winner_team"

def init_csv():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        with open(DATA_FILE, 'w') as f:
            f.write(CSV_HEADER + "\n")

# ==========================================
# CORE LOGIC: TrueSkill + Pandas
# ==========================================
def get_dashboard_data():
    init_csv()
    try:
        df = pd.read_csv(DATA_FILE).fillna('')
    except pd.errors.EmptyDataError:
        df = pd.DataFrame()

    # Initialize TrueSkill environment
    ts_env = trueskill.TrueSkill(draw_probability=0.0) # Padel doesn't have draws
    player_ratings = {}
    player_stats = {}

    def get_rating(name):
        if name not in player_ratings:
            player_ratings[name] = ts_env.create_rating()
            player_stats[name] = {'matches': 0, 'wins': 0}
        return player_ratings[name]

    if not df.empty:
        # Sort chronologically to calculate ratings over time correctly
        df_chronological = df.sort_values(by='date', ascending=True)

        for _, row in df_chronological.iterrows():
            # Get players
            t1p1, t1p2 = row['team1_player1'], row['team1_player2']
            t2p1, t2p2 = row['team2_player1'], row['team2_player2']
            winner = row['winner_team']

            # Update basic stats
            for p in [t1p1, t1p2]:
                get_rating(p) # Ensure they exist
                player_stats[p]['matches'] += 1
                if winner == 1: player_stats[p]['wins'] += 1
            for p in [t2p1, t2p2]:
                get_rating(p)
                player_stats[p]['matches'] += 1
                if winner == 2: player_stats[p]['wins'] += 1

            # 2v2 TRUESKILL MATH
            t1_ratings = (get_rating(t1p1), get_rating(t1p2))
            t2_ratings = (get_rating(t2p1), get_rating(t2p2))

            if winner == 1:
                # Team 1 is rank 0 (winner), Team 2 is rank 1 (loser)
                new_t1, new_t2 = ts_env.rate([t1_ratings, t2_ratings], ranks=[0, 1])
            else:
                # Team 2 is rank 0 (winner), Team 1 is rank 1 (loser)
                new_t1, new_t2 = ts_env.rate([t1_ratings, t2_ratings], ranks=[1, 0])

            # Save new ratings back to dictionary
            player_ratings[t1p1], player_ratings[t1p2] = new_t1[0], new_t1[1]
            player_ratings[t2p1], player_ratings[t2p2] = new_t2[0], new_t2[1]

    # Format data for the Premium Frontend
    stats_list = []
    for player in player_stats:
        wins = player_stats[player]['wins']
        matches = player_stats[player]['matches']
        rating = player_ratings[player]
        
        # A player's conservative TrueSkill is usually (mu - 3*sigma). We format it to a readable number.
        skill_score = max(0, int((rating.mu - 3 * rating.sigma) * 100)) 

        stats_list.append({
            'player': player,
            'matches': matches,
            'wins': wins,
            'losses': matches - wins,
            'winRate': round((wins / matches) * 100, 1) if matches > 0 else 0,
            'trueSkill': skill_score # We can use this on the frontend later!
        })

    # Sort Leaderboard by TrueSkill score, then by Win Rate
    stats_list.sort(key=lambda x: (x['trueSkill'], x['winRate']), reverse=True)

    recent_matches = df.sort_values(by='date', ascending=False).head(10).to_dict('records') if not df.empty else []
    all_players = sorted(list(player_stats.keys()))
    
    with open(DATA_FILE, 'r') as f:
        raw_csv = f.read()

    return stats_list, recent_matches, all_players, raw_csv

# ==========================================
# FLASK WEB ROUTES
# ==========================================

@app.route('/')
def index():
    stats, recent_matches, all_players, raw_csv = get_dashboard_data()
    
    # We will pass TrueSkill scores to Chart.js!
    chart_labels = [s['player'] for s in stats]
    chart_data = [s['winRate'] for s in stats] 
    active_tab = request.args.get('view', 'dashboard')

    return render_template('index.html', 
                           stats=stats,
                           recent_matches=recent_matches,
                           all_players=all_players,
                           chart_labels=chart_labels,
                           chart_data=chart_data,
                           raw_csv=raw_csv,
                           active_tab=active_tab)

@app.route('/add', methods=['POST'])
def add_match():
    init_csv()
    form = request.form
    
    # Calculate winner
    t1_sets = t2_sets = 0
    if int(form['set1_team1']) > int(form['set1_team2']): t1_sets += 1
    else: t2_sets += 1
    if int(form['set2_team1']) > int(form['set2_team2']): t1_sets += 1
    else: t2_sets += 1
        
    s3t1, s3t2 = form.get('set3_team1', ''), form.get('set3_team2', '')
    if s3t1 and s3t2:
        if int(s3t1) > int(s3t2): t1_sets += 1
        else: t2_sets += 1
            
    winner_team = 1 if t1_sets > t2_sets else 2

    new_row = pd.DataFrame([{
        'date': datetime.now().strftime('%Y-%m-%d'),
        'team1_player1': form['team1_player1'].strip(),
        'team1_player2': form['team1_player2'].strip(),
        'team2_player1': form['team2_player1'].strip(),
        'team2_player2': form['team2_player2'].strip(),
        'set1_team1': int(form['set1_team1']), 'set1_team2': int(form['set1_team2']),
        'set2_team1': int(form['set2_team1']), 'set2_team2': int(form['set2_team2']),
        'set3_team1': s3t1, 'set3_team2': s3t2,
        'winner_team': winner_team
    }])
    
    new_row.to_csv(DATA_FILE, mode='a', header=False, index=False)
    return redirect(url_for('index', view='dashboard'))

@app.route('/download')
def download_csv():
    init_csv()
    return send_file(DATA_FILE, as_attachment=True, download_name='padel_history.csv')

@app.route('/clear', methods=['POST'])
def clear_data():
    init_csv()
    with open(DATA_FILE, 'w') as f:
        f.write(CSV_HEADER + "\n")
    return redirect(url_for('index', view='dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
