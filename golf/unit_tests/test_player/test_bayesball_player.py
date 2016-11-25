''' Bayesball player - makes decisions based on calculated probabilities, so
    appropriate unit tests would confirm the expected policies
'''

from golf.unit_tests.test_player.player_test_base import PlayerTestBase
from golf.players.bayesball_player import BayesballPlayer

class TestBayesballPlayer(PlayerTestBase):
    ''' Test the policies for the bayesball player '''


    def _setup_bayesball_players(self, min_distance=8, card_margin=1, unknown_card_margin=1, num_cols=2):
        ''' Setup a basic bayesball player whose options can be over-written '''

        self.min_distance = min_distance
        self.card_margin = card_margin
        self.unknown_card_margin = unknown_card_margin
        self.num_cols = num_cols

        self.bayesball_player = BayesballPlayer(min_distance=min_distance,
                                                card_margin=card_margin,
                                                unknown_card_margin=unknown_card_margin,
                                                num_cols=num_cols)


    def test_player_name(self):
        ''' Basic test for setup '''

        self._setup_bayesball_players()
        self.assertEqual(str(self.bayesball_player).lower(), 'Bayesball_Player'.lower())