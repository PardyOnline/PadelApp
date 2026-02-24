import pandas as pd
import os
from datetime import datetime

DATA_DIR = 'data'
DATA_FILE = os.path.join(DATA_DIR, 'matches.csv')
CSV_HEADER = "date,team1_player1,team1_player2,team2_player1,team2_player2,set1_team1,set1_team2,set2_team1,set2_team2,set3_team1,set3_team2,winner_team"

def init_csv():
    """Ensures the directory and file exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        with open(DATA_FILE, 'w') as f:
            f.write(CSV_HEADER + "\n")

def get_raw_csv():
    """Returns the raw CSV string."""
    init_csv()
    with open(DATA_FILE, 'r') as f:
        return f.read()

def clear_csv():
    """Wipes the database."""
    init_csv()
    with open(DATA_FILE, 'w') as f:
        f.write(CSV_HEADER + "\n")

def save_uploaded_csv(file_stream):
    """Overwrites the database with an uploaded file."""
    init_csv()
    file_stream.save(DATA_FILE)

def get_matches():
    """Loads matches into a Pandas DataFrame."""
    init_csv()
    try:
        df = pd.read_csv(DATA_FILE)
        # Convert NaN to empty strings for the frontend
        return df.fillna('')
    except pd.errors.EmptyDataError:
        return pd.DataFrame()

def save_match(form):
    """Calculates winner and saves a new match to CSV."""
    init_csv()
    
    # Calculate winner based on sets
    t1_sets = t2_sets = 0
    s1t1, s1t2 = int(form['set1_team1']), int(form['set1_team2'])
    s2t1, s2t2 = int(form['set2_team1']), int(form['set2_team2'])
    
    if s1t1 > s1t2: t1_sets += 1
    else: t2_sets += 1
        
    if s2t1 > s2t2: t1_sets += 1
    else: t2_sets += 1
        
    # Handle optional 3rd set
    s3t1 = form.get('set3_team1', '')
    s3t2 = form.get('set3_team2', '')
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
        'set1_team1': s1t1,
        'set1_team2': s1t2,
        'set2_team1': s2t1,
        'set2_team2': s2t2,
        'set3_team1': s3t1,
        'set3_team2': s3t2,
        'winner_team': winner_team
    }])
    
    new_row.to_csv(DATA_FILE, mode='a', header=False, index=False)

def get_dashboard_stats():
    """Uses Pandas to calculate all player stats for the frontend."""
    df = get_matches()
    if df.empty:
        return [], [], []

    stats = {}
    
    # Iterate through matches to calculate stats
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

    # Convert to list of dictionaries and calculate Win Rate
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
            'winRate': win_rate
        })
    
    # Sort by Win Rate (descending), then by Matches played
    stat_list.sort(key=lambda x: (x['winRate'], x['matches']), reverse=True)
    
    # Prepare Recent Matches (last 10)
    recent = df.sort_values(by='date', ascending=False).head(10).to_dict('records')
    
    # Unique players list for autocomplete
    all_players = sorted(list(stats.keys()))

    return stat_list, recent, all_players

