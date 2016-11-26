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


    def _deck_minus_cards(self, deck, cards, shuffle_cards=True):
        ''' Return a deck for which the cards specified have been removed '''

        # First we'll create an index of the cards given, and the cards in the deck
        deck_index = {a:0 for a in range(13)}
        card_index = {a:0 for a in range(13)}

        for card in deck:
            deck_index[card] += 1

        for card in cards:
            card_index[card] += 1

        new_deck = []
        for card_val in deck_index.keys():
            new_deck += [card_val] * (deck_index[card_val] - card_index[card_val])

        if shuffle_cards:
            shuffle(new_deck)

        return new_deck


    def _generate_player_state(self, score, visible, raw_cards, num_rows=2, num_cols=2):
        ''' Convenience function to manually generate a valid state for a player

            Return:
                dict - In the form of { 'score': int value of the known cards,
                                        'visible': list of booleans w/ length (num rows X num columns) -
                                                   indicating whether the card has been seen by the owner,
                                        'raw_cards': list of ints representing visible cards in hand -
                                                    length (num rows X num_cols), None represents unknown cards,
                                        'num_rows': int number of rows - only 2 for now,
                                        'num_cols': int number of columns
                                      }
        '''
        return {'score': score,
                'visible': visible,
                'raw_cards': raw_cards,
                'num_rows': num_rows,
                'num_cols': num_cols}


    def _generate_game_state(self, self_player_state, opp_players_state, deck_up, has_knocked):
        ''' Convenience function to generate a valid game state '''

        return {'self': self_player_state,
                'opp': opp_players_state,
                'deck_up': deck_up,
                'has_knocked': has_knocked}


    def _get_state_for_hand(self, hand_index, has_knocked=False):
        """ Return the State for the hand at hand_index """

        # Comes directly from golf.board.get_state_for_player
        return {'self': self.hands[hand_index].get_state(is_self=True),
                'opp': [self.hands[p].get_state() for p in range(len(self.hands)) if p != hand_index],
                'deck_up': self.deck_up,
                'has_knocked': has_knocked}