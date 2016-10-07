''' Unit Tests for Hand Logic '''
import unittest2
from random import shuffle

from hand import Hand


class TestHand(unittest2.TestCase):
    ''' Unit tests for the hand class '''

    def setUp(self):
        ''' Bootstrap a deck and a standard hand of cards '''
        print 'Running the setup'
        self.deck = range(12) * 4
        shuffle(self.deck)


    def _load_hand(self, num_cols=2, cards_dealt=None):
        ''' Bootstrap a hand according to preferences passed in
            Args:
                num_cols - Number of columns for the hand
                cards_dealt - Optional array of cards dealt for hand
        '''

        # if the cards to be dealt were not passed in, then we should calculate them
        # from the standard deck loaded into the object at SetUp
        if not cards_dealt:
            cards_dealt = self.deck[:num_cols * 2]
            self.deck = self.deck[num_cols*2:]

        self.cards_dealt = cards_dealt
        self.hand = Hand(cards_dealt = cards_dealt)


    def tearDown(self):
        # Stub for where teardown / cleanuo logic would be stores
        pass


    def test_hand_setup(self):
        ''' Test some initial state on the standard hand '''
        self._load_hand(num_cols=2)

        self.assertEqual(self.hand.cards, self.cards_dealt)
        self.assertEqual(2, self.hand.num_cols)


    def test_hand_visibility(self):
        ''' Test card visibility both for the self and opponent player '''
        self._load_hand(num_cols=2)

        # Test some initial visibility
        self_visible = [card for card in self.hand.visible(is_self=True)]
        opp_visible = [card for card in self.hand.visible(is_self=False)]

        self.assertEqual(opp_visible, [None]*2*2)
        self_vis_index = [c % 2 == 0 for c in range(2*2)] # 2 * 2 in this case reprsents num_cols * num_rows
        for i, card in enumerate(self_visible):
            if self_vis_index[i]:
                self.assertEqual(card, self.cards_dealt[i])
            else:
                self.assertEqual(card, None)



