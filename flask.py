from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import analytics
import os

app = Flask(__name__, template_folder='templates')
app.secret_key = 'padel_secret_key' # Required for flashing messages

@app.route('/')
def index():
    # Load data from Pandas
    stats, recent_matches, all_players = analytics.get_dashboard_stats()
    raw_csv = analytics.get_raw_csv()
    
    # Extract data specifically for Chart.js
    chart_labels = [s['player'] for s in stats]
    chart_data = [s['winRate'] for s in stats]

    # Get active tab from URL (defaults to dashboard)
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
    analytics.save_match(request.form)
    # Redirect back to dashboard with a query parameter to open the correct tab
    return redirect(url_for('index', view='dashboard'))

@app.route('/download')
def download_csv():
    analytics.init_csv()
    return send_file(analytics.DATA_FILE, as_attachment=True, download_name='padel_history.csv')

@app.route('/upload', methods=['POST'])
def upload_csv():
    if 'csv_file' in request.files:
        file = request.files['csv_file']
        if file.filename.endswith('.csv'):
            analytics.save_uploaded_csv(file)
    return redirect(url_for('index', view='data'))

@app.route('/clear', methods=['POST'])
def clear_data():
    analytics.clear_csv()
    return redirect(url_for('index', view='dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

