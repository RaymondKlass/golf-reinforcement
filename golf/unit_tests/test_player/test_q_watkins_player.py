''' Q Watkins player - makes decisions based on q-learning
'''
import numpy as np
from golf.unit_tests.test_player.player_test_base import PlayerTestBase
from golf.players.q_watkins_player import QWatkinsPlayer

class TestQWatkinsPlayer(PlayerTestBase):
    ''' Test the policies for the Q Watkins player '''

    def setUp(self):
        self.q_watkins = QWatkinsPlayer()


    def test_player_name(self):
        ''' Basic test for setup '''

        self.assertEqual(str(self.q_watkins).lower(), 'Q Watkins Player'.lower())