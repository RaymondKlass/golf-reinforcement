''' Mixin with utility functions to be added to a player or trainable player if desired '''
import numpy as np
import math

class PlayerUtils(object):
    ''' Utility functions that players can use as a mixin '''


    def _calc_known_cards(self, state, card_in_hand=None):
        ''' return an index of known cards '''

        # Let's index the cards from 0-12 and just keep track of the cards that appear first
        cards = [0] * 13

        h = [a for a in state['self']['raw_cards'] if a != None] + \
                    [a for a in sum([b['raw_cards'] for b in state['opp']], []) if a != None] + \
                    state['deck_up']

        # Let's iterate through the self, opp, and deck_up cards and increment the index for them
        for card in [a for a in state['self']['raw_cards'] if a != None] + \
                    [a for a in sum([b['raw_cards'] for b in state['opp']], []) if a != None] + \
                    state['deck_up']:
            cards[card] += 1

        if card_in_hand != None:
            cards[card_in_hand] += 1

        return cards


    def _calc_unknown_cards(self, known_cards):
        ''' Calculate unknown cards from known cards '''

        # Now we should have an index with which to create the missing deck
        deck_down = []
        for i in range(13):
            deck_down += [i] * (4 - known_cards[i])

        return deck_down


    def _calc_average_card(self, state, card_in_hand=None):
        ''' Figure out the average card value left in the deck '''

        cards = self._calc_known_cards(state, card_in_hand)
        deck_down = self._calc_unknown_cards(cards)

        num_known_cards = sum(cards)
        known_cards =  sum([[i]*a for i, a in enumerate(cards)], [])

        return (300 - sum([min(a, 10) for a in known_cards])) / (52.0 - num_known_cards)


    def _calc_std_dev(self, state):
        ''' Calculate the standard deviation of the remaining cards '''

        cards = self._calc_known_cards(state)
        deck_down = self._calc_unknown_cards(cards)
        return np.std(deck_down)


    def _calc_row_col_for_index(self, index):
        ''' Calculate the row, col for a given card index '''

        row = int(i % 2)
        col = int(math.floor(i / 2))
        return (row, col,)