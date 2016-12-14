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
import random

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

        self.epsilon = 0 # Exploration
        self.discount = 0.3 # Discount future rewards - not sure if the optimal player should do this

        try:
            with open(model_file, 'rb') as model_file:
                self.weights = cPickle.load(model_file)
        except IOError:
            # model does not exist
            if self.verbose:
                print 'Model {} could not be found - starting from scratch'.format(model_file)

            self.weights = self._initialize_blank_model()

    def setup_trainer(self, checkpoint_dir, learning_rate=0.1, eval_freq=10000, epsilon=.4, discount=0.9):
        ''' Setup the training variables
            Args:
                checkpoint_dir: string -> Directory to store checkpoint files
                learning_rate: float -> single rate for now, may change to be a schedule
                eval_freq: integer -> iterations between running an evaluation
        '''

        self.epsilon = .2
        self.discount = 0.3

        self.checkpoint_dir = checkpoint_dir
        self.learning_rate = learning_rate
        self.eval_freq = eval_freq
        self.is_training = True
        self.q_state = None

    def turn_phase_1(self, state, possible_moves=['face_up_card', 'face_down_card', 'knock']):
        ''' Takes the state of the board and responds with the turn_phase_1 move recommended '''
        #print possible_moves
        self._cache_state_derivative_values(state)
        turn = self._take_turn(state, possible_moves)
        #print turn
        return turn


    def update_weights(self, state, card=None, reward=0, possible_moves=[]):
        ''' Takes a new state and executes the weight update '''
        # It's possible this player gets called before they have ever gone - in that case ignore the results
        try:
            old_q_state = dict(self.q_state)
        except TypeError:
            return

        print 'Old Q State'
        print old_q_state

        self._cache_state_derivative_values(state, card)
        self._take_turn(state, possible_moves, card)

        print 'New Q State'
        print self.q_state

        print 'Old2 state'
        print old_q_state

        self._update_weights( q_state_obj=old_q_state,
                              q_prime_state_obj=self.q_state,
                              reward= -1, # Since this update will never result from an exit state
                              learning_rate=self.learning_rate)



    def turn_phase_2(self, card, state, possible_moves=['return_to_deck', 'swap']):
        ''' Takes the state of the board and responds with the turn phase 2 move recommended '''
        self._cache_state_derivative_values(state, card)
        turn = self._take_turn(state, possible_moves, card)
        #print turn
        return turn


    def _take_turn(self, state, possible_moves, card=None):
        """ Since the general move logic will be the same for the first and the second phase
            of the players turn, let's further abstract that out into this method
        """
        turn_decisions = self._calc_move_score(state, possible_moves, card)
        turn_decisions.sort(key=lambda x: x['score'], reverse=True)
        # if we're training then we're going to need to save the value of the Q-State for updating weights later
        # Q(s,a) -> calculated value of the Q-State that we're committing to
        if self.is_training:
            choice = random.random()
            if choice <= self.epsilon:
                # select a random decision
                decision = random.choice(turn_decisions)
            else:
                decision = turn_decisions[0]

            self.q_state = decision
        else:
            decision = turn_decisions[0]

        return decision['action']


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

        print 'Action: {}'.format(action)
        if action == 'knocked':
            raise

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
                cards[location] = card_in_hand
                h = Hand(cards)
                repl_val = (h.score(cards) + (((self.num_cols * 2) - len([b for b in state['self']['visible'] if b]) - 1) * sub))
                feature_cache[key] = self.min_opp_score - repl_val

        print feature_cache

        return [feature_cache['0sigma'],
                feature_cache['1sigma'],
                feature_cache['2sigma'],
                feature_cache['-1sigma'],
                feature_cache['-2sigma']]


    def _update_weights(self, q_state_obj, q_prime_state_obj, reward, learning_rate):
        ''' Update the weights associated for a particular Q-State '''

        #print 'Initial weights for update {}'.format(self.weights)
        if self.verbose:
            print 'Initial weights for update {}'.format(self.weights)

        # difference = [r + gamma * max Q(s`,a`)] - Q(s,a)
        # Going to use a gamma of 1 for no discount on future Q state values,
        # as the card game naturally tends towards lower future rewards already
        print 'PRIME:'
        print q_prime_state_obj
        print 'STATE'
        print q_state_obj
        difference = (reward + q_prime_state_obj['score']) - q_state_obj['score']
        # Now we need to update the weights iteratively using the saved difference and learning rate
        # w_i <- w_i + (learning_rate * difference * f_i(s,a) where f_i is feature i
        for i, w in enumerate(self.weights):
            self.weights[i] = self.weights[i] + (learning_rate * difference * q_state_obj['raw_features'][i]) # adds regularization

        # we should rescale the weights so we don't encounter overflow
        # perhaps subtract the mean
        avg = sum(self.weights) / float(len(self.weights))
        self.weights = [(w-avg) / (max(self.weights+[.1]) * 0.01) for w in self.weights]

        #print 'Weights after update {}'.format(self.weights)
        if self.verbose:
            print 'Weights after update {}'.format(self.weights)


    def _calc_move_score(self, state, actions, card_in_hand=None):
        ''' Takes a vector of features and makes a move based upon history,
            known q-values, and computes the next move.
            Takes card param from turn_phase_2 when called by that method
        '''
        features = []
        if card_in_hand == None:
            # then we're looking at turn phase 1 - so no locations necessary
            for action in actions:
                print 'Extracting features'
                raw_features = self._extract_features_from_state(state, action, location=None, card_in_hand=None)
                score = sum([f * self.weights[i] for i, f in enumerate(raw_features)])
                print 'Score: {}'.format(score)
                features.append({'raw_features': raw_features,
                                 'score': score - 1,
                                 'action': action})
        else:
            # we will need to fan out the swap action to include swapping with all possible
            # locations in the hand
            #print 'Card in hand: {}, card in hand {}'.format(actions, card_in_hand)
            for action in actions:
                print 'Action: {}'.format(action)
                if action == 'swap':
                    for i in range(self.num_cols * 2):

                        raw_features = self._extract_features_from_state(state, action, location=i, card_in_hand=card_in_hand)
                        score = sum([f * self.weights[idx] for idx, f in enumerate(raw_features)])
                        print 'Score2: {}'.format(score)
                        row = int(i % 2)
                        col = int(math.floor(i / 2))
                        features.append({'raw_features':raw_features,
                                         'score': score,
                                         'action': (action, row, col)})
                else:
                    raw_features = self._extract_features_from_state(state, action, location=None, card_in_hand=None)
                    score = sum([f * self.weights[i] for i, f in enumerate(raw_features)])
                    print 'Score3: {}'.format(score)
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

        return [0] * length
