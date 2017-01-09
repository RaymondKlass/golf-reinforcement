''' Tests for Golf training - will include unit and more integration style tests
    as this is the component where much of the logic comes together
'''
import unittest2
from golf.trainer import Trainer
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


    def setUp(self):
        ''' Setup some basic players '''

        self.players = {'player{}'.format(a): 'player_{}'.format(a) for a in range(1,3)}