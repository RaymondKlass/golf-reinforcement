''' Tests for Golf training - will include unit and more integration style tests
    as this is the component where much of the logic comes together
'''
import unittest2
from golf.trainer import Trainer
from golf.players.trainable_player_base import TrainablePlayer
from mock import call, patch, Mock


class MockBoard(object):
    ''' Tiny class to mock board responses '''

    def __init__(self, match_num, player_scores=[3,10]):
        self.match_num = match_num
        self.cur_turn = 0
        self.player_scores = player_scores

    def play_game(self):
        scores = [self.player_scores[(self.cur_turn + self.match_num + i) % 2] for i in range(2)]
        self.cur_turn += 1
        return scores


class TestTrainer(unittest2.TestCase):
    ''' test the train module which controls multi-hole and multi-game matches '''


    def _setup_players(self, trainable_index=0, num_players=2):
        """ Setup players - with the option to make them trainable """

        self.players = []

        for i in range(num_players):
            player = TrainablePlayer()
            if i == trainable_index:
                player.is_trainable = True

            self.players.append(player)


    def test_creation_params(self):
        """ Test the initialization of params for the trainer class """

        trainable_player_index = 1
        self._setup_players(trainable_index=trainable_player_index)
        trainer = Trainer(self.players[0],
                          self.players[1],
                          trainable_player='player2',
                          checkpoint_epochs=100)

        for i in range(2):
            self.assertEqual(trainer.players[i], self.players[i])

        self.assertEqual(trainer.total_holes, 9)
        self.assertEqual(trainer.trainable_player, trainable_player_index)
        self.assertEqual(trainer.checkpoint_epochs, 100)





