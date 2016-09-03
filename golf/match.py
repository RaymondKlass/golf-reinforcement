from board import Board

class Match(object):

    def __init__(self, player1, player2, holes=9, num_cols=2):
        self.players = [player1, player2,]
        self.scores = [0,0]
        self.total_holes = (holes - 1) # Since we're 0 indexed


    def play_k_matches(self, k):
        ''' Play a lot of independent matches for a more fair comparison '''
        matches = [0,0]
        for _ in range(k):
            self.play_match()

            if self.scores[0] > self.scores[1]:
                matches[0] += 1
            elif self.scores[1] > self.scores[0]:
                matches[1] += 1

            self.scores = [0,0]
        print 'Player 0: {} matches, Player 1: {} matches'.format(matches[0], matches[1])


    def play_match(self):
        ''' Play all of the holes for a single match '''

        for turn in range(self.total_holes):
            board = Board([self.players[turn % 2], self.players[(turn + 1) % 2]], 2)
            scores = board.play_game()
            for i, score in enumerate(self.scores):
                self.scores[i] += scores[i]


if __name__ == '__main__':
    from random_player import RandomPlayer

    player1 = RandomPlayer()
    player2 = RandomPlayer()
    match = Match(player1, player2)
    match.play_k_matches(100)