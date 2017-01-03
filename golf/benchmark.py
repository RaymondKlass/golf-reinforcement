''' Run a benchmark comparison between players '''
from match import Match


# Maybe only needs to be a simple method
# Will convert later to a class if the complexity waarants

def benchmark_player(player1, player2):
    ''' Run a benchmark match via the match functionality '''

    m = Match(player1, player2)

    # Let's make a benchmark - a standard
    # 1000 Matches

    results = m.play_k_matches(100)
    return results # Results should be a list with results lining up with the
                   # players that were submitted i.e. player1 = results[0]