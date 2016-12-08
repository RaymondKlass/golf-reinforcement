""" Basic implementation of Q-Learning based player, named after
    Watkins who first introduced Q-Learning, and later proved it's
    convergence in 1992 https://en.wikipedia.org/wiki/Q-learning
"""
import cPickle
import math
import random
from golf.players.trainable_player_base import TrainablePlayer
from golf.players.player_utils import PlayerUtils
from golf.hand import Hand

class QWatkinsPlayer(TrainablePlayer, PlayerUtils):
    """ Trainable player based on basic Q-Learning through
        hand-crafted features, Q function approximation,
        and simple linear function approximation
    """

    def __init__(self, model_file='file-no-found', num_cols=2, *args, **kwargs):
        """ Initialize player and load model if available -
            otherwise player will start with a randomly initialize model """

        super(QWatkinsPlayer, self).__init__(*args, **kwargs)
        self.num_cols = num_cols
        self.is_training = False # This will be over-written if self.setup_trainer() is run

        try:
            with open(model_file, 'rb') as model_file:
                self.weights = cPickle.load(model_file)
        except IOError:
            # model does not exist
            if self.verbose:
                print 'Model {} could not be found - starting from scratch'.format(model_file)

            self.weights = self._initialize_blank_model()

    def setup_trainer(self, checkpoint_dir, learning_rate=0.1, eval_freq=10000):
        ''' Setup the training variables
            Args:
                checkpoint_dir: string -> Directory to store checkpoint files
                learning_rate: float -> single rate for now, may change to be a schedule
                eval_freq: integer -> iterations between running an evaluation
        '''

        self.checkpoint_dir = checkpoint_dir
        self.learning_rate = learning_rate
        self.eval_freq = eval_freq
        self.is_training = True


    def turn_phase_1(self, state, possible_moves=['face_up_card', 'face_down_card', 'knock']):
        ''' Takes the state of the board and responds with the turn_phase_1 move recommended '''
        self._cache_state_derivative_values(state)
        return self._take_turn(state, possible_moves)


    def turn_phase_2(self, card, state, possible_moves=['return_to_deck', 'swap']):
        ''' Takes the state of the board and responds with the turn phase 2 move recommended '''
        self._cache_state_derivative_values(state, card)
        return self._take_turn(state, possible_moves, card)


    def _take_turn(self, state, possible_moves, card=None):
        """ Since the general move logic will be the same for the first and the second phase
            of the players turn, let's further abstract that out into this method
        """

        turn_decisions = self._calc_move_score(state, possible_moves, card)
        turn_decisions.sort(key=lambda x: x['score'], reverse=True)

        print turn_decisions
        return turn_decisions[0]['action']


    def _cache_state_derivative_values(self, state, card_in_hand=None):
        """ In order to calculate the features that the model is based on, we'll need to know
            a couple of important values - we should just calculate these once per turn phase
        """

        self.avg_card = self._calc_average_card(state, card_in_hand)
        self.card_std_dev = self._calc_std_dev(state)
        self.min_opp_score = min([a['score']+(((self.num_cols * 2) - len([b for b in a['raw_cards'] if b != None])) *  self.avg_card) for a in state['opp']])


    def _extract_features_from_state(self, state, action, location=None, card_in_hand=None):
        ''' Takes an input state and outputs a vector of features for use with model
            - Should be specific for which turn_phase we are, but otherwise selecting
              fewer features here will help reduce the complexity of the search space
            - Need to represent not only the value, but also the Q-value as these features
              will be used as a way to describe the value of a Q-State
            - Location is only provided for phase_2 when the action is replacing a card at an
              actual specific location (index value passed)
            - Card - value of the card in hand - used during the turn_phase_2
        '''

        """
        Let's list the features that might make sense to extract

        These features need to take into account the action that is going to be performed
        as they represent the Q-State and not the Value of the current position -
        our agent needs to make decisions based upon these values, so if they don't encode
        what makes a difference in the decision, then I'm not sure they would be effective

        Features for the first and the second phases of the turn should be identical -
        need to make sure that the features are dependent on the expected outcome of the action -
        The numbers below represent values that would change if / when the player looks to
        replace a card with either the unknown (assumed) card, or the face-up one - or
        chooses to knock - ending their turn.

        # So here's a first go at the features - all should be ratios with opponents score
        - expected replacement value - treat unknown cards as average
        - replacement value - unknown cards for self +1 Sigma
        - replacement value - unknown cards for self +2 Sigma
        - replacement value - unknown cards for self -1 Sigma
        - replacement value - unknown cards for self -2 Sigma

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
        """

        # this is where the real stuff gets done
        # We'll need to figure out the current score differential associated with the Q-State
        # We have access to the min opponent score - which is cached through self.min_opp_score

        # Let's assemble the feature vector in a dictionary and then return it via a fixed
        # transformation function so that we provide it consistently
        feature_cache = {'0sigma': 0,
                         '1sigma': 1,
                         '2sigma': 2,
                         '-1sigma': -1,
                         '-2sigma': -2}

        # make sure that when computing the replacement card with std_dev we adhere to
        # the bounds of a standard deck - 0 <= card <= 12
        feature_vals = {key: min(max(self.avg_card + (self.card_std_dev * val), 0), 12) for key, val in feature_cache.iteritems()}

        if action in ('knock', 'return_to_deck',):
            # this is the special case that we will not be replacing any cards
            for key, replacement in feature_vals.iteritems():
                self_score = (state['self']['score'] + (((self.num_cols * 2) - len([b for b in state['self']['visible'] if b])) * replacement))
                feature_cache[key] = self.min_opp_score - self_score

        elif action == 'face_up_card':
            # we know the replacement value since the card is exposed: state['deck_up'][-1]
            # we'll still need to replace both the unknown cards with the assumptions + use the deck_up card
            for key, sub in feature_vals.iteritems():
                # We'll need to try all of the possible replacement spots for the card - then take the min
                repl_vals = []
                for loc in range(self.num_cols * 2):
                    cards = list(state['self']['raw_cards'])
                    cards[loc] = state['deck_up'][-1]
                    h = Hand(cards)
                    repl_vals.append((h.score(cards) + (((self.num_cols * 2) - len([b for b in state['self']['visible'] if b]) - 1) * sub)))
                feature_cache[key] = self.min_opp_score - min(repl_vals)

        elif action == 'face_down_card':
            replacement_card = self.avg_card
            if replacement_card % 1 == 0:
                # check if the average card is an integer - since we don't want o possibly imply that the replacement
                # would be a solumn match - choosing to avoid this situation - let's add a tiny bit to it - to avoid this
                replacement_card += 0.0001

            for key, sub in feature_vals.iteritems():
                # We'll need to try all of the possible replacement spots for the card - then take the min
                repl_vals = []
                for loc in range(self.num_cols * 2):
                    cards = list(state['self']['raw_cards'])
                    cards[loc] = replacement_card
                    h = Hand(cards)
                    repl_vals.append((h.score(cards) + (((self.num_cols * 2) - len([b for b in state['self']['visible'] if b]) - 1) * sub)))
                feature_cache[key] = self.min_opp_score - min(repl_vals)

        elif action == 'swap':
            # We should swap at a specific location
            for key, sub in feature_vals.iteritems():
                # We'll need to try all of the possible replacement spots for the card - then take the min
                cards = list(state['self']['raw_cards'])
                print 'Location for swap {}'.format(location)
                cards[location] = card_in_hand
                h = Hand(cards)
                repl_val = (h.score(cards) + (((self.num_cols * 2) - len([b for b in state['self']['visible'] if b]) - 1) * sub))
                feature_cache[key] = self.min_opp_score - repl_val

        return [feature_cache['0sigma'],
                feature_cache['1sigma'],
                feature_cache['2sigma'],
                feature_cache['-1sigma'],
                feature_cache['-2sigma']]


    def _update_weights(self, features, learning_rate):
        ''' Update the weights associated for a particular Q-State '''

        # Still need to figure out the best way to pass and update from the game's
        # exit state - as there's not normally an endpoint for it - so I may
        # need to add the spec to the trainable player base class

        pass


    def _calc_move_score(self, state, actions, card_in_hand=None):
        ''' Takes a vector of features and makes a move based upon history,
            known q-values, and computes the next move.
            Takes card param from turn_phase_2 when called by that method
        '''
        features = []
        if card_in_hand == None:
            print 'Card in hand none: {}, card in hand {}'.format(actions, card_in_hand)
            # then we're looking at turn phase 1 - so no locations necessary
            for action in actions:
                raw_features = self._extract_features_from_state(state, action, location=None, card_in_hand=None)
                score = sum([f * self.weights[i] for i, f in enumerate(raw_features)])
                features.append({'raw_features': raw_features,
                                 'score': score,
                                 'action': action})
        else:
            # we will need to fan out the swap action to include swapping with all possible
            # locations in the hand
            for action in actions:
                if action == 'swap':
                    for i in range(self.num_cols * 2):

                        print 'Calling swap with location: {}'.format(i)

                        raw_features = self._extract_features_from_state(state, action, location=i, card_in_hand=card_in_hand)
                        print 'Value for i {}'.format(i)
                        score = sum([f * self.weights[idx] for idx, f in enumerate(raw_features)])
                        print 'Value2 for i {}'.format(i)
                        row = int(i % 2)
                        col = int(math.floor(i / 2))
                        print 'Considering row: {}, col {}, i: {}'.format(row, col, i)
                        features.append({'raw_features':raw_features,
                                         'score': score,
                                         'action': (action, row, col)})
                else:
                    raw_features = self._extract_features_from_state(state, action, location=None, card_in_hand=None)
                    score = sum([f * self.weights[i] for i, f in enumerate(raw_features)])
                    features.append({'raw_features': raw_features,
                                        'score': score,
                                        'action': action})
        return features

    def _initialize_blank_model(self, length=5):
        ''' return a blank model - random weights between -1 and 1
            Going to check performance with random weight initialization
            first, but in the future it may be preferable to have
            random weights along an even distribution, but that seems
            like an optimization best left for later
        '''

        return [(random.random() * 2) - 1 for _ in range(length)]

