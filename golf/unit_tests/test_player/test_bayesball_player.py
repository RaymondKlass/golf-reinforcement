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


    def test_calc_average_card(self):
        ''' Test calculating the average card remaining in the deck '''

        deck = range(13) * 4
        self.assertEqual(len(deck), 52)

        # We mark cards 10 and over as 10
        deck_sum = lambda d: sum([min(10, a) for a in d])

        # There are 300 points in a full deck
        self.assertEqual(deck_sum(deck), 300)

        # Let's remove some cards
        hands = [range(4), range(4)]
        self.assertEqual(sum(sum(hands, [])), 12)

        deck_left = self._deck_minus_cards(cards=sum(hands, []), deck=deck)
        self._load_hands(cards=hands, deck=deck_left)
        self._setup_bayesball_players()

        calc_avg = self.bayesball_player._calc_average_card(self._get_state_for_hand(0))

        # only deducting one players-worth of cards, since the player would not know about the
        # other player's state just yet
        self.assertEqual(calc_avg, (300 - sum([a for i, a in enumerate(range(4)) if i % 2 == 0]) - sum([min(a, 10) for a in self.deck_up])) / 49.0)


