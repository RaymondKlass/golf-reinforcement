import sys, getopt
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


def main(argv):

    '''
    inputfile = ''
    outputfile = ''
    try:
       opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
       print 'test.py -i <inputfile> -o <outputfile>'
       sys.exit(2)
    for opt, arg in opts:
       if opt == '-h':
          print 'test.py -i <inputfile> -o <outputfile>'
          sys.exit()
       elif opt in ("-i", "--ifile"):
          inputfile = arg
       elif opt in ("-o", "--ofile"):
          outputfile = arg
    '''

    # Setup some defaults
    num_matches = 1
    player1 = None
    player2 = None
    verbose = False

    try:
        opts, args = getopt.getopt(argv, "hp1:p2:m:v", ["player1=", "player2=", "matches=", "verbose"])
    except:
        print 'python match.py -p1 <player1> -p2 <player2> -m <number of matches> -v <verbose>'
    for opt, arg in opts:
        if opt == '-h':
            print 'python match.py -p1 <player1> -p2 <player2> -m <number of matches> -v <verbose>'
            sys.exit(2)
        elif opt in ("-p1", "--player1"):
            player1 = arg
        elif opt in ("-p2", "--player2"):
            player2 = arg
        elif opt in ("-m", "--match"):
            match = arg
        elif opt in ("-v", "--verbose"):
            verbose = True



    from random_player import RandomPlayer

    player1 = RandomPlayer()
    player2 = RandomPlayer()
    match = Match(player1, player2)
    match.play_k_matches(100)




if __name__ == '__main__':

    main(sys.argv[1:])
