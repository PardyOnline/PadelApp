import trueskill

# Initialize TrueSkill environment
world = trueskill.GlobalRanking()

class Player:
    def __init__(self, name):
        self.name = name
        self.rating = world.create_rating()

    def update_rating(self, opponents_rating, outcome):
        self.rating = world.rate((self.rating,), (opponents_rating,), [outcome])[0]

class Leaderboard:
    def __init__(self):
        self.players = {}

    def add_player(self, player):
        self.players[player.name] = player

    def rank_players(self):
        return sorted(self.players.values(), key=lambda p: p.rating.mu, reverse=True)

# Example usage
if __name__ == '__main__':
    leaderboard = Leaderboard()
    player1 = Player('Alice')
    player2 = Player('Bob')

    leaderboard.add_player(player1)
    leaderboard.add_player(player2)

    # Simulated outcomes
    player1.update_rating(player2.rating, 1)  # Alice wins against Bob
    player2.update_rating(player1.rating, 0)  # Bob loses to Alice

    ranked_players = leaderboard.rank_players()
    for player in ranked_players:
        print(f'{player.name}: {player.rating}')