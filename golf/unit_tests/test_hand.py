''' Unit Tests for Hand Logic '''
import unittest2
from random import shuffle

from golf.hand import Hand, GolfHandOutOfIndexError


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
        # Stub for where teardown / clean-up logic would be stores
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
        self_visible = lambda: [card for card in self.hand.visible(is_self=True)]
        opp_visible = lambda: [card for card in self.hand.visible(is_self=False)]

        self.assertEqual(opp_visible(), [None]*2*2)
        self_vis_index = [c % 2 == 0 for c in range(2*2)] # 2 * 2 in this case reprsents num_cols * num_rows
        for i, card in enumerate(self_visible()):
            if self_vis_index[i]:
                self.assertEqual(card, self.cards_dealt[i])
            else:
                self.assertEqual(card, None)

        # Now we'll go about modelling some game play so we can make sure visibility is correctly handled
        self.hand.swap(row=1, col=1, new_card=7, source_revealed = False)
        self.assertEqual(opp_visible(), [None]*2*2)
        self.assertEqual(self_visible()[self.hand._coords_to_index(1,1)], 7)

        # Let's try a swap that the opp should know about
        self.hand.swap(row=0, col=0, new_card=8, source_revealed=True)
        self.assertEqual(opp_visible()[self.hand._coords_to_index(0,0)], 8)
        self.assertEqual(self_visible()[self.hand._coords_to_index(0,0)], 8)

        # Lets a swap that woul result in hiding a known card from the opp player
        # Let's try a swap that the opp should know about
        self.hand.swap(row=0, col=0, new_card=3, source_revealed=False)
        self.assertEqual(opp_visible()[self.hand._coords_to_index(0,0)], None)
        self.assertEqual(self_visible()[self.hand._coords_to_index(0,0)], 3)


    def test_scoring(self):
        ''' Test the scoring for accuracy with standard and non-standard hands '''

        # zero score, both columns have a match
        self._load_hand(num_cols=2, cards_dealt=[2,2,2,2])
        self.assertEqual(self.hand.score(), 0)

        # test using the score functionlity with a specified set of cards
        self.assertEqual(self.hand.score(cards=[1,2,3,4]), 10)

        # Test scoring using a larger hand
        self._load_hand(num_cols=3, cards_dealt=[3,3,4,5,1,10])
        self.assertEqual(self.hand.score(), 20)
        self.assertEqual(self.hand.score(), self.hand.score(cards=[3,3,4,5,1,10]))


    def test_score_partially_visible_hand(self):
        ''' Test Scoring hands where some of the cards are still hidden,
            used when calculating the score for the state object generated
            during the playing of a match
        '''

        self._load_hand(num_cols=2, cards_dealt=[2,3,4,5])
        # Test the base case before testing incomplete hands
        self.assertEqual(self.hand.score(), 14)

        # Test score with missing cards
        self.assertEqual(self.hand.score(cards=[None, 3,4, None]), 7)
        self.assertEqual(self.hand.score(cards=[None, 5,5,None]), 10)


    def test_coord_to_index(self):
        ''' Test coords to index and index to coords methods -
            these methods should be able to access all cards, and should
            be reciprocal methods
        '''

        self._load_hand(num_cols=2, cards_dealt=[2,3,4,5])
        self.assertEqual(self.hand.cards[self.hand._coords_to_index(0,0)], 2)
        self.assertEqual(self.hand.cards[self.hand._coords_to_index(1,0)], 3)
        self.assertEqual(self.hand.cards[self.hand._coords_to_index(0,1)], 4)
        self.assertEqual(self.hand.cards[self.hand._coords_to_index(1,1)], 5)

        self.assertEqual(self.hand._index_to_coords(1), (1,0))
        self.assertEqual(self.hand._index_to_coords(0), (0,0))
        self.assertEqual(self.hand._index_to_coords(2), (0,1))
        self.assertEqual(self.hand._index_to_coords(3), (1,1))

        # Let's test some exceptions
        with self.assertRaises(GolfHandOutOfIndexError) as cm:
            self.hand._coords_to_index(3,3)

        # Let's test some exceptions
        with self.assertRaises(GolfHandOutOfIndexError) as cm:
            self.hand._coords_to_index(-1,0)

        # Let's test some exceptions
        with self.assertRaises(GolfHandOutOfIndexError) as cm:
            self.hand._coords_to_index(0,-3)

        with self.assertRaises(GolfHandOutOfIndexError) as cm:
            self.hand._index_to_coords(100)

        with self.assertRaises(GolfHandOutOfIndexError) as cm:
            self.hand._index_to_coords(-1)


    def test_shape(self):
        ''' Shape should return (num_rows, num_cols) '''

        self._load_hand(num_cols = 2)
        self.assertEqual(self.hand.shape, (2,2,))

        # Try with a different shape hand
        self._load_hand(num_cols = 5)
        self.assertEqual(self.hand.shape, (2, 5))
