''' Tests for Golf matches - will include unit and more integration style tests
    as this is the component where much of the logic comes together
'''
import unittest2
from golf.match import Match
from mock import patch, Mock


class TestMatch(unittest2.TestCase):
    ''' test the match module which controls multi-hole and multi-game matches '''


    def test_creation_params(self):
        ''' Test creating a class and confirming the init params '''

        players = ['player_{}'.format(a) for a in range(2)]
        m = Match(player1 = players[0], player2=players[1], holes=8, verbose=False)
        self.assertEqual(m.players[0], players[0])
        self.assertEqual(m.players[1], players[1])
        self.assertEqual(m.total_holes, 8)
        self.assertEqual(m.verbose, False)
