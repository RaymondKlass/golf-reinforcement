''' Player based solely on probabilities '''
from player_base import Player
import math

class BayesballPlayer(Player):
    ''' Class defining a player based on probability of that moment
        Will take into account action based rules defined as follows:
        1.  Assume unknown cards are worth average value of the unassigned
            cards - where unassigned cards are those not in the discard or known
            quantities.
        2.  Knock if your score is N points lower than you opponent - or your score is
            1 or less
        3.  If the card up is a match for a column - then use it
        4.  If the card up is lower than the average available card, then exchange it for the highest
            non-columned card.
        5.  If up card is high then take the down card - exchange it for the highest non-column card,
            or if one doesn't exist then place it face up

    # Note the state object that is returned is arranged specifically:
        {'self': { 'score': int value of the known cards,
                  'visible': list of booleans w/ length (num rows X num columns),
                  'raw_cards': list of ints representing visible cards in hand -
                               length (num rows X num_cols), None represents unknown cards,
                  'num_rows': int number of rows - only 2 for now,
                  'num_cols': int number of columns
                 },
         'opp': { Same as above ^ }
         'deck_up': list of card in the discard pile (which both players have seen)
        }
    '''


    def __init__(self, min_distance=1, num_cols=2):
        ''' Initialize player and set a minimum distance between scores to knock '''

        super(BayesballPlayer, self).__init__()
        self.min_distance = min_distance
        self.num_cols = num_cols



    def _calc_average_card(self, state):
        ''' Figure out the average card value left in the deck '''

        # Let's index the cards from 0-12 and just keep track of the cards that appear first
        cards = [0] * 13

        # Let's iterate through the self, opp, and deck_up cards and increment the index for them
        for hand in [a for a in state['self']['raw_cards'] if a != None] + \
                    [a for a in state['opp']['raw_cards'] if a != None] + \
                    state['deck_up']:
            for card in hand:
                cards[card] += 1

        # Now we should have an index with which to create the missing deck
        deck_down = []
        for i in range(13):
            self.deck_down += [i] * (4 - cards[i])

        return sum([min(a, 10) for a in deck_down]) / float(len(deck_down))



    def _calc_score_diff(self, state, avg):
        ''' Given the current state, calculate the score differential -
            The key metric for deciding policy for this player
        '''

        return min([a['score']+(((self.num_cols * 2) - len([b for b in a['visible'] if b])) *  avg) for a in state['opp']]) - \
               (state['self']['score'] + (((self.num_cols * 2) - len([b for b in state['self']['visible'] if b])) * avg))



    def turn_phase_1(self, state, possible_moves=['face_up_card', 'face_down_card', 'knock']):
        """ Let's calculate an assumption for the opponents hand and then make a decision -
            If we believe our hand to be better, than lets know -
            Otherwise we should take whichever card we think is better, the face-up or face down card
        """

        avg_card = self._calc_average_card()
        if self._calc_score_diff(state, avg_card) >= self.min_distance and 'knock' in possible_moves:
            return 'knock'
        else:
            face_up_card = min(state['deck_up'][0], 10)
            if avg_card > face_up_card and len([a for a in state['self']['raw_cards'] if a and a > avg_card]):
                # then we should take the face up card
                return 'face_up_card'
            return 'face_down_card'


    def turn_phase_2(self, card, state, possible_moves=['return_to_deck', 'swap']):
        """ Getting to this point means that we've chosen a card.
            If 'swap' is the only option, we must swap -
            Otherwise we have the option of replacing the card back on the deck

            Our policy here should be to replace the highest-difference card with the
            card in-hand, assuming that unknown cards are equal to the average card -
            and of course taking into account column null scoring
        """

        avg_card = _calc_average_card(state)

        # Let's start by pairing off cards
        columns = [(state['self']['raw_cards'][a], state['self']['raw_cards'][a+1],) \
                   for a in range(len(state['self']['raw_cards'])) if a % 2 == 0]

        # We need to figure out where the best place to put the `card` would be
        # So Let's rate our options
        # Best - complete and un-completed column
        # Better - replace a card of known-higher-value
        # Good - replace an unknown card of assumed higher-value
        # Bad - replace a known card equal or lesser value (this onw shouldn't happen)

        best_replacement = None
        replacement_value = 0

        for i, pair in enumerate(columns):
            # i is the col - so index is i * 2 + (index of pair - either 0 or 1)
            if pair[0] == pair[1]:
                # This is the case that the 2 cards form a completed column - i.e. 0 score
                continue

            # we should replace pair[0] and / or pair[1] with avg_card if they are == None
            if pair[0] == None:
                pair[0] = avg_card

            if pair[1] == None:
                pair[1] = avg_card

            if pair[0] > pair[1] and (best_replacement == None or pair[0] > replacement_value):
                best_replacement = i*2
                replacement_value = pair[0]

            if pair[1] >= pair[0] and (best_replacement == None or pair[1] > replacement_value):
                best_replacement = (i*2) + 1
                replacement_value = pair[1]

        if best_replacement != None and (replacement_value > card or 'return_to_deck' not in possible_moves):
            return ('swap', row=best_replacement % 2, col=math.floor(best_replacement / 2))

        if 'return_to_deck' in possible_moves:
            return ('return_to_deck',)
