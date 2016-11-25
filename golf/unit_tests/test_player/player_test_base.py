''' Base Class for Player Tests '''
import unittest2
from random import shuffle

from golf.hand import Hand

class PlayerTestBase(unittest2.TestCase):
    ''' Base class for building tests for players '''


    def _load_hands(self, deck=None , num_cols=2, num_hands=2, cards=[]):
        ''' load a configurable state which can be used for tests
            Args:
                deck: If specified - the deck will be used to deal any hands that
                      were not explicitly soecified
                cards: needs to be an array of cards
        '''

        # this is the entire deck - we'll need to remove cards specified above
        # so as to have a valid deck after hands are dealt
        if deck:
            self.deck = deck
        else:
            self.deck = range(13) * 4

        self.hands = []
        # if the cards to be dealt were not passed in, then we should calculate them
        # from the standard deck loaded into the object at SetUp

        for i in range(num_hands):
            try:
                self.hands.append(Hand(cards_dealt=cards[i]))
            except IndexError:
                # This hand has not been explicitly specified, we'll deal it from the deck
                self.hands.append(Hand(cards_dealt=self.deck[:num_cols * 2]))
                self.deck = self.deck[num_cols * 2:]

        # Let's deal the first card
        self.deck_up = []
        self.deck_up.append(self.deck.pop())


    def _deck_minus_hands(self, deck, cards, shuffle=True):
        ''' Return a deck for which the cards specified have been removed '''

        # First we'll create an index of the cards given, and the cards in the deck
        deck_index = {a:0 for a in range(13)}
        card_index = {a:0 for a in range(13)}

        for card in deck:
            deck_index[card] += 1

        for card in cards:
            card_index += 1

        deck_minus_cards = []
        for card_val in deck_index.keys():
            deck_minus_cards += [card_val] * (deck_index[card_val] - card_index[card_val])

        shuffle(deck_minus_cards)
        return deck_minus_cards


    def _get_state_for_hand(self, hand_index):
        """ Return the State for the hand at hand_index """

        # Comes directly from golf.board.get_state_for_player
        return {'self': self.hands[hand_index].get_state(),
                'opp': [self.hands[p] for p in range(len(self.hands)) if p != hand_index],
                'deck_up': self.deck_up}