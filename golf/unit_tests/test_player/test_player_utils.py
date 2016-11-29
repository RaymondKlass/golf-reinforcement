''' Test the utility functions found in PlayerUtils '''
from golf.players.player_utils import PlayerUtils
from golf.unit_tests.test_player.player_test_base import PlayerTestBase

class TestPlayerUtils(PlayerTestBase):
    ''' Test the utility functions found in the player_utils '''

    def _setup_player_utils(self):
        ''' Setup player utils with dependencies '''

        self.player_utils = PlayerUtils()


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
        self._setup_player_utils()

        calc_avg = self.player_utils._calc_average_card(self._get_state_for_hand(0))

        # only deducting one players-worth of cards, since the player would not know about the
        # other player's state just yet
        self.assertEqual(calc_avg, (300 - sum([a for i, a in enumerate(range(4)) if i % 2 == 0]) - sum([min(a, 10) for a in self.deck_up])) / 49.0)
