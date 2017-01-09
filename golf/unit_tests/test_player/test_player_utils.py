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
        self.assertEqual(calc_avg, (300 - sum([a for i, a in enumerate(range(4)) if i % 2 == 0]) \
                                    - sum([min(a, 10) for a in self.deck_up])) / 49.0)


    def test_calc_row_col(self):
        """ Test calculation to determine the row / column for a particular index
            By Definition:
                Cards are encoded as a single array
                with i % 2 == 0 cards in the bottom row
                and i @ 2 != 0 cards in the top row

            Therefore for a 2 column game:
            index 0 = 0,0
            index 1 = 1,0
            index 2 = 0,1
            index 3 = 1,1
        """

        self._setup_player_utils()

        self.assertEqual(self.player_utils._calc_row_col_for_index(0), (0,0,))
        self.assertEqual(self.player_utils._calc_row_col_for_index(1), (1,0,))
        self.assertEqual(self.player_utils._calc_row_col_for_index(2), (0,1,))
        self.assertEqual(self.player_utils._calc_row_col_for_index(3), (1,1,))


    def test_calc_known_cards(self):
        """ Test calculation of the known cards from the state object """

        self._setup_player_utils()

        self_cards = [1,2,None,3]
        opp1_cards = [5,6,7,None]
        opp2_cards = [None,12,5,7]

        basic_state = {'self': {'raw_cards': self_cards},
                       'opp': [{'raw_cards': opp1_cards},
                               {'raw_cards': opp2_cards}],
                       'deck_up': [8,9]}

        # the output of this is an ordered array of # of cards that exist at each key
        all_cards = {0: 0,
                     1: 1,
                     2: 1,
                     3: 1,
                     4: 0,
                     5: 2,
                     6: 1,
                     7: 2,
                     8: 1,
                     9: 1,
                     10: 0,
                     11: 0,
                     12: 1}

        with self.subTest(msg='Test calc_known_cards without a card in hand'):
            cards = self.player_utils._calc_known_cards(basic_state)
            self.assertEqual(all_cards.values(), cards)

        with self.subTest(msg='Test calc known cards with a card in hand'):
            cards = self.player_utils._calc_known_cards(basic_state, 10)
            ac = dict(all_cards)
            ac[10] += 1
            self.assertEqual(ac.values(), cards)


    def test_calc_unknown_cards(self):
        """ Test calculating the unknown cards """

        known_cards = {a:0 for a in range(13)}
        unknown_cards = [[a] * 4 for a in range(13) if a not in [5,8,10]]

        known_cards[5] = 3
        unknown_cards += [5]

        known_cards[8] = 2
        unknown_cards += [8,8]

        known_cards[10] = 4

        self._setup_player_utils()

        self.assertEqual(self.player_utils._calc_unknown_cards(known_cards.values()).sort(), unknown_cards.sort())


    def test_calc_standard_dev(self):
        """ Test utility method to calculate the standard deviation of an array of unknown cards """

        self._setup_player_utils()

        def return_known_cards(*args, **kwargs):
            return []

        def return_unknown_cards(*args, **kwargs):
            return range(10)

        # over-write the standard methods
        self.player_utils._calc_known_cards = return_known_cards
        self.player_utils._calc_unknown_cards = return_unknown_cards

        # By definition the Standard deviation of range(10) = 2.872281323
        self.assertEqual(round(self.player_utils._calc_std_dev(None), 5),
                         round(2.872281323, 5))

