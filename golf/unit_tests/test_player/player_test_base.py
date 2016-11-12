''' Base Class for Player Tests '''
import unittest2
from random import shuffle

from golf.hand import Hand

class PlayerTestBase(unittest2.TestCase):
    ''' Base class for building tests for players '''

    def _load_state(self, num_cols=2, self_cards=None, opp_cards=None):
        ''' load a configurable state which can be used for tests '''

        # this is the entire deck - we'll need to remove cards specified above
        # so as to have a valid deck after hands are dealt
        self.deck = range(13) * 4

        # if the cards to be dealt were not passed in, then we should calculate them
        # from the standard deck loaded into the object at SetUp
        if self_cards:
            cards_dealt = self_cards
        else:
            cards_dealt = self.deck[:num_cols * 2]
            self.deck = self.deck[num_cols*2:]

        self.cards_dealt = cards_dealt
        self.hand = Hand(cards_dealt = cards_dealt)

        if opp_cards:
            opp_cards = opp_cards
        else:
            opp_cards = self.deck[:num_cols * 2]
            self.deck = self.deck[num_cols*2:]


        self.opp_hand = Hand(cards_dealt = opp_cards)