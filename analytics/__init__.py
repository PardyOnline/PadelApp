# Re-exports everything so main.py continues to work with `import analytics` unchanged.
# Add new public functions here as modules are built out — nothing else should change.

from .data import (
    DATA_FILE,
    init_csv,
    get_raw_csv,
    clear_csv,
    save_uploaded_csv,
    get_matches,
    save_match,
)
from .player_stats import basic_player_stats
from .ratings import get_trueskill_ratings
from .dashboard import get_all_dashboard_data

# Uncomment as modules are built out:
# from .team_stats import get_partnership_stats, get_best_partnerships
# from .history import get_monthly_stats, get_player_of_the_month
# from .insights import get_close_matches, get_upsets
