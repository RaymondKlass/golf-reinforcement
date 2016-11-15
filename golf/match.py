import sys, getopt
from board import Board


class Match(object):

    def __init__(self, player1, player2, holes=9, num_cols=2, verbose=False):
        self.players = [player1, player2,]
        self.scores = [0,0]
        self.total_holes = (holes - 1) # Since we're 0 indexed
        self.verbose = verbose


    def play_k_matches(self, k):
        ''' Play a lot of independent matches for a more fair comparison '''
        matches = [0,0]
        for i in range(k):

            if self.verbose:
                print('Starting Match # {}'.format(i))
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
            board = Board([self.players[turn % 2], self.players[(turn + 1) % 2]], 2, verbose=self.verbose)
            scores = board.play_game()
            for i, score in enumerate(self.scores):
                self.scores[i] += scores[i]


def main(argv):
    # Setup some defaults
    num_matches = 1
    player1 = None
    player2 = None
    verbose = False

    try:
        opts, args = getopt.getopt(argv, "hm:v", ["player1=", "player2=", "matches=", "verbose"])
    except:
        print 'python match.py -player1 <player1> -player2 <player2> -m <number of matches> -v <verbose>'
    for opt, arg in opts:
        if opt == '-h':
            print 'python match.py -player1 <player1> -player2 <player2> -m <number of matches> -v <verbose>'
            sys.exit(2)
        elif opt in ("-pa", "--player1"):
            player1 = arg
        elif opt in ("-pb", "--player2"):
            player2 = arg
        elif opt in ("-m", "--match"):
            try:
                num_matches = int(arg)
            except ValueError:
                pass
        elif opt in ("-v", "--verbose"):
            verbose = True

    # Players need to be specified by file.ClassName
    player1 = player1.split('.')
    player2 = player2.split('.')

    player1 = getattr(__import__("players.{}".format(player1[0]), fromlist=[player1[1]]), player1[1])
    player2 = getattr(__import__("players.{}".format(player2[0]), fromlist=[player2[1]]), player2[1])

    player1 = player1(verbose=verbose)
    player2 = player2(verbose=verbose)

    match = Match(player1, player2, verbose=verbose)
    match.play_k_matches(num_matches)


if __name__ == '__main__':
    main(sys.argv[1:])