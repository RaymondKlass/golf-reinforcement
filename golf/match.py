import sys, getopt
from board import Board


class Match(object):

    def __init__(self, player1, player2, holes=9, num_cols=2, verbose=False):
        self.players = [player1, player2,]
        self.scores = [0,0]
        self.total_holes = holes # Since we're 0 indexed
        self.verbose = verbose


    def play_k_matches(self, k):
        ''' Play a lot of independent matches for a more fair comparison '''
        matches = [0,0]
        for i in range(k):

            if self.verbose:
                print('\n **** Starting Match # {} **** \n'.format(i))
            self.play_match(i)

            if self.scores[0] > self.scores[1]:
                matches[int(i % 2)] += 1
            elif self.scores[1] > self.scores[0]:
                matches[int((i+1) % 2)] += 1

            self.scores = [0,0]
        print 'Player 0: {} matches, Player 1: {} matches'.format(matches[0], matches[1])


    def play_match(self, match_num):
        ''' Play all of the holes for a single match '''

        for turn in range(self.total_holes):
            board = Board([self.players[(turn + match_num) % 2], self.players[((turn + match_num) + 1) % 2]], 2, verbose=self.verbose)
            scores = board.play_game()
            for i, score in enumerate(self.scores):
                self.scores[(turn + match_num + i) % 2] += scores[(turn + match_num + i) % 2]


def main(argv):
    # Setup some defaults
    num_matches = 1
    player1 = None
    player2 = None
    verbose = False
    holes = None

    try:
        opts, args = getopt.getopt(argv, "hm:v", ["player1=", "player2=", "matches=", "holes=", "verbose"])
    except:
        print 'python match.py -player1 <player1> -player2 <player2> -m <number of matches> -holes <number of holes> -v <verbose>'
    for opt, arg in opts:
        if opt == '-h':
            print 'python match.py -player1 <player1> -player2 <player2> -m <number of matches> -holes <number of holes> -v <verbose>'
            sys.exit(2)
        elif opt in ("--player1"):
            player1 = arg
        elif opt in ("--player2"):
            player2 = arg
        elif opt in ("-m", "--match"):
            try:
                num_matches = int(arg)
            except ValueError:
                pass
        elif opt in ("--holes"):
            try:
                holes = int(arg)
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

    kwargs = {'verbose': verbose}
    if holes:
        kwargs['holes'] = holes

    match = Match(player1, player2, **kwargs)
    match.play_k_matches(num_matches)


if __name__ == '__main__':
    main(sys.argv[1:])