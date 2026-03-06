from flask import Flask, render_template, request, redirect, url_for, send_file
from analytics import get_all_dashboard_data, save_match, clear_csv, save_uploaded_csv, DATA_FILE, init_csv

app = Flask(__name__)
app.secret_key = 'padel_secret_key'

# ==========================================
# FLASK WEB ROUTES
# ==========================================

@app.route('/')
def index():
    data = get_all_dashboard_data()
    active_tab = request.args.get('view', 'dashboard')
    return render_template('index.html',
                           stats=data['stats'],
                           recent_matches=data['recent_matches'],
                           all_players=data['all_players'],
                           chart_labels=data['chart_labels'],
                           chart_data=data['chart_data'],
                           raw_csv=data['raw_csv'],
                           active_tab=active_tab,
                           total_matches=data['total_matches'],
                           top_ranked_player=data['top_ranked_player'],
                           top_ranked_score=data['top_ranked_score'])

@app.route('/add', methods=['POST'])
def add_match():
    save_match(request.form)
    return redirect(url_for('index', view='dashboard'))

@app.route('/download')
def download_csv():
    init_csv()
    return send_file(DATA_FILE, as_attachment=True, download_name='padel_history.csv')

@app.route('/upload', methods=['POST'])
def upload_csv():
    file = request.files.get('csv_file')
    if file and file.filename.endswith('.csv'):
        save_uploaded_csv(file)
    return redirect(url_for('index', view='data'))

@app.route('/clear', methods=['POST'])
def clear_data():
    clear_csv()
    return redirect(url_for('index', view='dashboard'))

@app.route('/rankings')
def rankings():
    data = get_all_dashboard_data()
    selected_player = request.args.get('player', '').strip()
    return render_template('ranking.html',
                           rankings=data['stats'],
                           all_players=data['all_players'],
                           selected_player=selected_player)

if __name__ == '__main__':
    app.run(debug=True)

