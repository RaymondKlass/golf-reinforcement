''' Run a benchmark comparison between players '''
from match import Match

def benchmark_player(player1, player2, num_matches=10):
    ''' Run a benchmark match via the match functionality
        Args:
            player1: A golf player
            player2: A golf player
        Returns:
            list with results in the order of players given
    '''

    m = Match(player1, player2)

    results = m.play_k_matches(num_matches)
    return results