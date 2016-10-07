''' Player based solely on probabilities '''
from player_base import Player

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
        }
    '''


    def __init__(self, min_distance=0):
        ''' Initialize player and set a minimum distance between scores to knock '''

        super(BayesPlayer, self).__init__()
        self.min_distance = min_distance



    def _calc_average_card(self, state):
        ''' Figure out the average card value left in the deck '''

        # Let's index the cards from 0-12 and just keep track of the cards that appear first
        cards = [0] * 12
        for hand in [state['self']['raw_cards']] + [a['raw_cards'] for a in state['opp']]:
            for card in hand:
                if card != None:
                    cards[card] += 1

        # Also need to deal with the deck that is face up
        for card in self.deck_up:
            cards[card] += 1

        # Now we should have an index with which to create the missing deck
        self.deck_down = []
        for i in range(12):
            self.deck_down += [cards[i]] * (4 - cards[i])

        return sum(self.deck_down) / len(self.deck_down)



    def _calc_score_diff(self, state, avg):
        ''' Given the current state, calculate the score differential -
            The key metric for deciding policy for this player
        '''

        return min([a['score'] for a in state['opp']]) - state['self']['score']



    def turn_phase_1(self, state, possible_moves=['face_up_card', 'face_down_card', 'knock']):
        """ We're just going to make a random selection at every step """

        self.avg_card = self._calc_average_card()
        if self._calc_score_diff(state, self.avg_card) >= self.min_distance and 'knock' in possible_moves:
            return 'knock'
        else:
            self.avg_card = self._calc_average_card()
            if self.avg_card > stats['deck_up'][0]:
                # then we should take the face up card
                return 'face_up_card'
            return 'face_down_card'


    def turn_phase_2(self, card, state, possible_moves=['return_to_deck', 'swap']):
        """ Again - this will be a random choice """

        min_card_cache = state['cur_player_hand']

