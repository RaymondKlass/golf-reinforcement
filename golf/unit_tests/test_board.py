''' Tests for Golf matches - will include unit and more integration style tests
    as this is the component where much of the logic comes together
'''
import unittest2
from golf.board import Board
from golf.hand import Hand
from golf.players.player_base import Player


class TestBoard(unittest2.TestCase):
    ''' Test the match module - both unit and integration tests '''

    def setUp(self):
        ''' Setup the board module to run through functionality '''

        # let's create a 1 vs 1 game by default - could be extended later
        self.players = [self._generate_base_player()] * 2
        self.num_cols = 2

        # No need to test the verbose flag - we'll leave it turned off
        self.verbose = False


    def _generate_base_player(self):
        ''' return a very basic player - which tests must over-write
            the logic of - for validation and assertion.
        '''

        return Player()