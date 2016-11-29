''' Mixin with utility functions to be added to a player or trainable player if desired '''

class PlayerUtils(object):
    ''' Utility functions that players can use as a mixin '''


    def _calc_average_card(self, state):
        ''' Figure out the average card value left in the deck '''

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

        # Now we should have an index with which to create the missing deck
        deck_down = []
        for i in range(13):
            deck_down += [i] * (4 - cards[i])

        num_known_cards = sum(cards)
        known_cards =  sum([[i]*a for i, a in enumerate(cards)], [])

        return (300 - sum([min(a, 10) for a in known_cards])) / (52.0 - num_known_cards)