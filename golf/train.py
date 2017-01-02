''' Train a player by playing against them - also supporting validation '''

import sys
import getopt
import json
from board import Board
from benchmark import benchmark_player


class Match(object):

    def __init__(self, player1, player2, trainable_player=None, holes=9, checkpoint_epochs=None, verbose=False):
        self.players = [player1, player2,]
        self.scores = [0,0]
        self.total_holes = holes # Since we're 0 indexed
        self.verbose = verbose
        self.trainable_player = trainable_player

        if self.trainable_player != None:
            self.trainable_player = int(self.trainable_player.split('player')[-1]) - 1

        # array of tuples to hold the results from evaluation
        self.eval_results = []

        self.checkpoint_epochs = checkpoint_epochs
        if not self.checkpoint_epochs and self.verbose:
            print 'You chose training, but have not specified a number of epochs to save model at - saving and evaluation ' \
                  'will only occur at the end of the game.'

        if self.verbose:
            # let's introduce the players
            print 'Player 0 {}'.format(self.players[0])
            print 'Player 1 {}'.format(self.players[1])


    def train_k_epochs(self, k):
        ''' Play a lot of independent matches for a more fair comparison '''
        for i in range(k):

            if self.verbose or True:
                print('\n **** Starting epoch # {} **** \n'.format(i))
            scores = self.play_match(i)

            if self.verbose or True:
                print 'Player 1 Score: {} Player 2 Score: {}'.format(scores[0], scores[1])

            if self.checkpoint_epochs and i and not (i+1) % self.checkpoint_epochs:
                # For now we'll use the checkpoint epochs as a measure of when to save
                # and when to evaulate the model.
                if self.verbose or True:
                    print 'Reached {} epochs - now starting an evaluation'.format(i)

                self.process_checkpoint(i)

        if self.verbose or True:
            print 'Finished training player - going to run a final evaluation and save a checkpoint'

        self.process_checkpoint(k)


    def process_checkpoint(self, epoch):
        """ It's time for a checkpoint - so we will run evaluation and then save a checkpoint file """

        # Let's run an evaulation - first we'll need to set both players to not be in training mode
        if self.trainable_player != None and self.trainable_player >= 0 and self.trainable_player < len(self.players):
            self.players[self.trainable_player].is_trainable = False

        result = benchmark_player(*self.players)
        self.eval_results.append(result)

        if self.verbose:
            print 'Evaluation results: '
            for i, player in self.players:
                print 'Player{}: {} : {}'.format(i, player, result[i])

        # Now we should save the trainable player - and make it trainable again
        if self.trainable_player != None and self.trainable_player >= 0 and self.trainable_player < len(self.players):
            self.players[self.trainable_player].is_trainable = True
            self.players[self.trainable_player].save_checkpoint(epoch)

        if self.verbose:
            print 'Finished saving checkpoint for epoch: {}'.format(epoch)


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
    num_epochs = 1
    player1 = None
    player1_args = {'init': {}, 'train': {}}
    player2 = None
    player2_args = {'init': {}, 'train': {}}
    verbose = False
    holes = None
    trainable_player = None
    checkpoint_epochs = None

    try:
        opts, args = getopt.getopt(argv, "e:v", ["player1=", "player2=", "player1_args=", "player2_args=", "epochs=", "holes=", "verbose", 'trainable=', "checkpoint_epochs="])
    except:
        print 'python golf/train.py --player1 <player1> --player1_args <player1 arg json> --player2 <player2> --player2_args <player2 arg json> ' \
              '-e <number of training epochs> -=holes <number of holes> -v <verbose> --trainable= <trainable_player> --checkpoint_epochs <epochs between saving checkpoints>'

    opts, args = getopt.getopt(argv, "e:v", ["player1=", "player2=", "player1_args=", "player2_args=", "epochs=", "holes=", "verbose", 'trainable=', "checkpoint_epochs="])

    for opt, arg in opts:
        if opt == '-h':
            print 'python golf/train.py --player1 <player1> --player2 <player2> -e <number of epochs> --holes <number of holes> -v <verbose> --trainable=player2'
            sys.exit(2)
        elif opt in ("--player1"):
            player1 = arg
        elif opt in ("--player1_args"):
            player1_args = json.loads(arg)
        elif opt in ("--player2"):
            player2 = arg
        elif opt in ("--player2_args"):
            player2_args = json.loads(arg)
        elif opt in ("-e", "--epochs"):
            try:
                num_epochs = int(arg)
            except ValueError:
                pass
        elif opt in ("--holes"):
            try:
                holes = int(arg)
            except ValueError:
                pass
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("--trainable"):
            trainable_player = str(arg)
        elif opt in ("--checkpoint_epochs"):
            checkpoint_epochs = int(arg)

    # Players need to be specified by file.ClassName
    player1 = player1.split('.')
    player2 = player2.split('.')

    player1 = getattr(__import__("players.{}".format(player1[0]), fromlist=[player1[1]]), player1[1])
    player2 = getattr(__import__("players.{}".format(player2[0]), fromlist=[player2[1]]), player2[1])

    player1 = player1(verbose=verbose, **player1_args['init'])
    if trainable_player == 'player1':
        player1.setup_trainer(**player1_args['train'])

    player2 = player2(verbose=verbose, **player2_args['init'])
    if trainable_player == 'player2':
        print 'Player 2 args: {}'.format(player2_args)
        player2.setup_trainer(**player2_args['train'])


    kwargs = {'verbose': verbose}
    if holes:
        kwargs['holes'] = holes

    match = Match(player1, player2, trainable_player=trainable_player, checkpoint_epochs=checkpoint_epochs, **kwargs)

    match.train_k_epochs(num_epochs)


if __name__ == '__main__':
    main(sys.argv[1:])