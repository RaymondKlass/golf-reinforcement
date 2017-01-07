import sys
import getopt
import json
from board import Board


class Match(object):

    def __init__(self, player1, player2, holes=9, verbose=False):
        self.players = [player1, player2,]
        self.scores = [0,0]
        self.total_holes = holes # Since we're 0 indexed
        self.verbose = verbose
        self.matches = [0] * len(self.players)

        if self.verbose:
            # let's introduce the players
            print 'Player 0 {}'.format(self.players[0])
            print 'Player 1 {}'.format(self.players[1])


    def play_k_matches(self, k):
        ''' Play a lot of independent matches for a more fair comparison '''
        for i in range(k):

            if self.verbose:
                print('\n **** Starting Match # {} **** \n'.format(i))
            scores = self.play_match(i)

            if scores[0] > scores[1]:
                self.matches[1] += 1
            elif scores[1] > scores[0]:
                self.matches[0] += 1

            if self.verbose:
                print '\nMatch {} Results:'.format(i)
                print 'Player 1 Score: {} Player 2 Score: {}'.format(scores[0], scores[1])
                print 'Player 0: {}, Player 1: {}'.format(self.matches[0], self.matches[1])

        print 'Player 0: {} matches, Player 1: {} matches'.format(self.matches[0], self.matches[1])
        return (self.matches[0], self.matches[1])


    def play_match(self, match_num):
        ''' Play all of the holes for a single match '''

        scores = [0,0]

        for turn in range(self.total_holes):
            board = Board([self.players[(turn + match_num) % 2], self.players[((turn + match_num) + 1) % 2]], 2, verbose=self.verbose)

            game_scores = board.play_game()
            for i, score in enumerate(scores):
                scores[(turn + match_num + i) % 2] += game_scores[i]

        return scores


def main(argv):
    # Setup some defaults
    num_matches = 1
    player1 = None
    player1_args = {'init': {}}
    player2 = None
    player2_args = {'init': {}}
    verbose = False
    holes = None

    try:
        opts, args = getopt.getopt(argv, "hm:v", ["player1=", "player2=", "player1_args=", "player2_args=", "matches=", "holes=", "verbose"])
    except:
        print 'python match.py --player1=<player1> --player1_args=<player1_args> --player2=<player2> --player2_args=<player2_args> -m <number of matches> -holes <number of holes> -v <verbose>'
    for opt, arg in opts:
        if opt == '-h':
            print 'python match.py --player1=<player1> --player1_args=<player1_args> --player2=<player2> --player2_args=<player2_args> -m <number of matches> -holes <number of holes> -v <verbose>'
            sys.exit(2)
        elif opt in ("--player1"):
            player1 = arg
        elif opt in ("--player1_args"):
            player1_args = json.loads(arg)
        elif opt in ("--player2"):
            player2 = arg
        elif opt in ("--player2_args"):
            player2_args = json.loads(arg)
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

    player1 = player1(verbose=verbose, **player1_args['init'])
    player2 = player2(verbose=verbose, **player2_args['init'])

    kwargs = {'verbose': verbose}
    if holes:
        kwargs['holes'] = holes

    match = Match(player1, player2, **kwargs)
    match.play_k_matches(num_matches)


if __name__ == '__main__':
    main(sys.argv[1:])