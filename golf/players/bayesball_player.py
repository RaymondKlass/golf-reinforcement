''' Player based solely on probabilities '''
from golf.players.player_base import Player
from golf.players.player_utils import PlayerUtils
from golf.hand import Hand
import math

class BayesballPlayer(Player, PlayerUtils):
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


    def __init__(self, min_distance=8, card_margin=1, unknown_card_margin=1, num_cols=2, *args, **kwargs):
        ''' Initialize player and set a minimum distance between scores to knock '''

        super(BayesballPlayer, self).__init__(*args, **kwargs)
        self.min_distance = min_distance
        self.num_cols = num_cols

        # Card margin is the amount "better" a known card needs to be than the average card -
        # basically a measure of risk comfort - the face_up card needs to X better than the
        # calculated average card to be considered.
        self.card_margin = card_margin

        # Essentially the discount rate for unknown cards - it's fixed now, but could become
        # dynamic in the future.  It's the amount worse than the average that we will assume
        # our unknown cards are
        self.unknown_card_margin = unknown_card_margin


    def __repr__(self):
        return 'Bayesball_Player'


    def _calc_score_diff(self, state, avg):
        ''' Given the current state, calculate the score differential -
            The key metric for deciding policy for this player
        '''

        self.score = (state['self']['score'] + (((self.num_cols * 2) - len([b for b in state['self']['visible'] if b])) * avg))
        self.min_opp_score = min([a['score']+(((self.num_cols * 2) - len([b for b in a['raw_cards'] if b != None])) *  avg) for a in state['opp']])

        return self.min_opp_score - self.score



    def turn_phase_1(self, state, possible_moves=['face_up_card', 'face_down_card', 'knock']):
        """ Let's calculate an assumption for the opponents hand and then make a decision -
            If we believe our hand to be better, than lets know -
            Otherwise we should take whichever card we think is better, the face-up or face down card

            Extension to the logic - if the other player knocks, then it makes little sense to knock as well -
            so we'll take that possibility away.
        """

        avg_card = self._calc_average_card(state)
        score_diff = self._calc_score_diff(state, avg_card)

        # remove knock from possible_moves if has_knocked == True in state
        if state['has_knocked'] and 'knock' in possible_moves:
            list(possible_moves).remove('knock')

        if (score_diff >= self.min_distance and 'knock' in possible_moves) or \
           (self.score <= self.min_distance and 'knock' in possible_moves) or \
           (self.min_opp_score <= self.min_distance and 'knock' in possible_moves):

            return 'knock'
        else:
            face_up_card = min(state['deck_up'][-1], 10)
            if avg_card - self.card_margin > face_up_card and len([a for a in state['self']['raw_cards'] if a != None and a > face_up_card - self.card_margin]):
                # then we should take the face up card
                return 'face_up_card'
            return 'face_down_card'


    def _calc_score_with_replacement(self, raw_cards, card, position, unknown_card_val):
        ''' Calculate the score by substituting the given card at given position,
            Use the unknown_card_val for cards that are assumed
            Position -> should be Int index of where card should be replaced
        '''

        self_cards = list(raw_cards)

        # Handle the case where no replacement is sought - so we simply don't replace
        if position != None:
            self_cards[position] = card

        self_score = self._calc_score_for_cards(self_cards)
        self_score = self_score + (len([b for b in self_cards if b == None]) * min(unknown_card_val, 10))
        return self_score


    def _calc_score_for_cards(self, cards):
        ''' calculate score for cards '''

        h = Hand(cards)
        return h.score(cards)


    def turn_phase_2(self, card, state, possible_moves=['return_to_deck', 'swap']):
        """ Alternative turn_phase_2 method """

        avg_card = self._calc_average_card(state, card_in_hand=card)
        pos_scores = []

        # Let's try replacing the card_in_hand at every position -
        # then we'll also calculate the possibility of returning to deck
        for i in range(self.num_cols * 2):
            score = self._calc_score_with_replacement(state['self']['raw_cards'],
                                                      card,
                                                      i,
                                                      avg_card)
            row, col = self._calc_row_col_for_index(i)
            pos_scores.append((('swap', row, col,), score,))

        # We also need to consider returning the card back to the deck
        score = self._calc_score_with_replacement(state['self']['raw_cards'],
                                                  None,
                                                  None,
                                                  avg_card)
        pos_scores.append((('return_to_deck',), score))
        pos_scores.sort(key=lambda x: x[1])
        return pos_scores[0][0]
