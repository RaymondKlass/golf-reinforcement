''' Player based solely on probabilities '''
from golf.players.player_base import Player
from golf.players.player_utils import PlayerUtils
import math

class BayesballPlayer(Player, PlayerUtils):
    ''' Class defining a player based on probability of that moment
        Will take into account action based rules defined as follows:
        1.  Assume unknown cards are worth average value of the unassigned
            cards - where unassigned cards are those not in the discard or known
            quantities.
        2.  Knock if your score is N points lower than you opponent - or your score is
            1 or less
        3.  Take the score given by the best replacement of the face_up and face_down cards
            use the card that gives the best return.
        4.  Analyze the scores given by substituting the card in all available positions -
            move forward with the one that lowers the score most, or (if possible), return
            it to the deck if no position lowers the score

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

            # Should also probably replace this logic with replacing either the deck_up at all positions
            # or an assummed `avg_card` at the locations.

            action_scores = []

            # First let's calculate the face_up_card value
            face_up_card = min(state['deck_up'][-1], 10)

            face_up_scores = []
            for i in range(self.num_cols * 2):
                score = self._calc_score_with_replacement(state['self']['raw_cards'],
                                                          face_up_card,
                                                          i,
                                                          avg_card)
                face_up_scores.append(score)
            action_scores.append(('face_up_card', min(face_up_scores),))

            # Now we should calculate the face down score - this is easy - it's jusrt replacing with the avg card
            # Let's first make sure that the average card doesn't make a column
            if avg_card % 1 == 0:
                avg_card = avg_card + 0.0001

            face_down_scores = []

            for i in range(self.num_cols * 2):
                score = self._calc_score_with_replacement(state['self']['raw_cards'],
                                                          avg_card,
                                                          i,
                                                          avg_card)
                face_down_scores.append(score)

            action_scores.append(('face_down_card', min(face_down_scores),))
            action_scores.sort(key=lambda x: x[1])
            return action_scores[0][0]


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

        if 'return_to_deck' in possible_moves:
            # We also need to consider returning the card back to the deck
            score = self._calc_score_with_replacement(state['self']['raw_cards'],
                                                      None,
                                                      None,
                                                      avg_card)
            pos_scores.append((('return_to_deck',), score))

        pos_scores.sort(key=lambda x: x[1])
        return pos_scores[0][0]
