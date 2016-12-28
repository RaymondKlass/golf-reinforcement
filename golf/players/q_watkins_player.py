""" Basic implementation of Q-Learning based player, named after
    Watkins who first introduced Q-Learning, and later proved it's
    convergence in 1992 https://en.wikipedia.org/wiki/Q-learning
"""
import cPickle
import os
import math
import time
import numpy as np
from golf.players.trainable_player_base import TrainablePlayer
from golf.players.player_utils import PlayerUtils
from golf.hand import Hand
import random

class QWatkinsPlayer(TrainablePlayer, PlayerUtils):
    """ Trainable player based on basic Q-Learning through
        hand-crafted features, Q function approximation,
        and simple linear function approximation
    """

    def __init__(self, model_file='file-not-found', num_cols=2, *args, **kwargs):
        """ Initialize player and load model if available -
            otherwise player will start with a randomly initialize model """

        super(QWatkinsPlayer, self).__init__(*args, **kwargs)
        self.num_cols = num_cols
        self.is_training = False # This will be over-written if self.setup_trainer() is run

        self.epsilon = 0 # Exploration
        self.discount = 0.3 # Discount future rewards - not sure if the optimal player should do this
        self.start_model_file = model_file

        try:
            with open(model_file, 'rb') as model_file:
                self.weights = cPickle.load(model_file)
        except IOError:
            # model does not exist
            if self.verbose:
                print 'Model {} could not be found - starting from scratch'.format(model_file)

            self.weights = self._initialize_blank_model()


    def setup_trainer(self, checkpoint_dir, learning_rate=0.1, epsilon=.2, discount=0.3):
        ''' Setup the training variables
            Args:
                checkpoint_dir: string -> Directory to store checkpoint files
                learning_rate: float -> single rate for now, may change to be a schedule
                eval_freq: integer -> iterations between running an evaluation
        '''

        self.epsilon = epsilon
        self.discount = discount

        self.checkpoint_dir = checkpoint_dir
        self.learning_rate = learning_rate
        self.is_training = True
        self.q_state = None

        # Introspect the number of epochs from a checkpoint file in proper format
        try:
            self.starting_epochs = int(self.start_model_file.split('_')[-1].split('.')[0])
        except ValueError:
            # Cannot parse an int from the value
            self.starting_epochs = 0



    def save_checkpoint(self, epochs):
        ''' Save a checkpoint file in the pre-specified directory, in a name - date format '''

        cur_time = str(time.time())
        epochs = self.starting_epochs + epochs
        file_path = os.path.join(self.checkpoint_dir, '{}_{}.pkl')
        with open(file_path, 'wb') as outfile:
            cPickle.dump(self.weights, outfile)



    def turn_phase_1(self, state, possible_moves=['face_up_card', 'face_down_card', 'knock']):
        ''' Takes the state of the board and responds with the turn_phase_1 move recommended '''

        if self.verbose:
            print '\n Turn Phase 1: \n'

        self._cache_state_derivative_values(state)
        turn = self._take_turn(state, possible_moves)
        return turn


    def update_weights(self, state, card=None, reward=0, possible_moves=[]):
        ''' Takes a new state and executes the weight update '''
        # It's possible this player gets called before they have ever gone - in that case ignore the results
        try:
            old_q_state = dict(self.q_state)
        except TypeError:
            return

        self._cache_state_derivative_values(state, card)
        self._take_turn(state, possible_moves, card)

        self._update_weights( q_state_obj=old_q_state,
                              q_prime_state_obj=self.q_state,
                              reward= -1, # Since this update will never result from an exit state
                              learning_rate=self.learning_rate)



    def turn_phase_2(self, card, state, possible_moves=['return_to_deck', 'swap']):
        ''' Takes the state of the board and responds with the turn phase 2 move recommended '''

        if self.verbose:
            print '\n Turn Phase 2: \n'

        self._cache_state_derivative_values(state, card)
        turn = self._take_turn(state, possible_moves, card)
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
                if self.verbose:
                    print 'Taking a random decision for training'
            else:
                decision = turn_decisions[0]
                if self.verbose:
                    print 'Taking the optimal decision'

            self.q_state = decision
        else:
            if self.verbose:
                print 'Taking the optimal decision'

            decision = turn_decisions[0]

        if self.verbose:
            print '\n All decision options: {}'.format(turn_decisions)
            print 'Made decision: {}'.format(decision)

        return decision['action']


    def _cache_state_derivative_values(self, state, card_in_hand=None):
        """ In order to calculate the features that the model is based on, we'll need to know
            a couple of important values - we should just calculate these once per turn phase
        """

        self.avg_card = self._calc_average_card(state, card_in_hand)
        self.card_std_dev = self._calc_std_dev(state)
        self.min_opp_score = min([a['score']+(len([b for b in a['raw_cards'] if b == None]) *  self.avg_card) for a in state['opp']])

        if self.verbose:
            print 'Checking State Derivative Values'
            print 'Avg_card: {}'.format(self.avg_card)
            print 'Card Standard Deviation: {}'.format(self.card_std_dev)
            print 'Min Opp Score: {}'.format(self.min_opp_score)
            print 'State: {}'.format(state)


    def _extract_features_from_state(self, state, replacement_card=None, location=None):
        """
            Calculate the feature vector that we will use.  It is based upon replacing the
            unknown cards with different "scenarios" - calculated with 1 and 2 std dev intervals
        """

        # Calculate the substitution values based on on avg card +/- 1 and 2 sigma values
        substitutions = np.array([ min(max(self.avg_card + (self.card_std_dev * val), 0), 12) for val in [0, 1, 2, -1, -2]])
        result = np.array([])

        for sub in substitutions:
            result = np.append(result, self._calc_score_with_replacement(state['self']['raw_cards'],
                                                                         replacement_card,
                                                                         location,
                                                                         sub))


        # self.min_opp_score - score
        # This score needs to be adjusted - to be the derivative of the score difference
        return result



    def _calc_score_with_replacement(self, raw_cards, card, position, unknown_card_val):
        ''' Calculate the score by substituting the given card at given position,
            Use the unknown_card_val for cards that are assumed
            Position -> should be Int index of where card should be replaced
        '''

        self_cards = list(raw_cards)

        # Handle the case where no replacement is sought - so we simply don't replace
        if position:
            self_cards[position] = card

        self_score = self._calc_score_for_cards(self_cards)
        self_score = self_score + (len([b for b in self_cards if b == None]) * min(unknown_card_val, 10))

        if self.verbose:
            print '\n Cards: {}'.format(self_cards)
            print 'Replacement card : {}'.format(card)
            print 'Replacement card position: {}'.format(position)
            print 'Unknown card value: {}'.format(unknown_card_val)
            print 'Score with replacement: {}'.format(self_score)

        return self_score


    def _calc_score_for_cards(self, cards):
        ''' calculate score for cards '''

        h = Hand(cards)
        return h.score(cards)


    def _calc_swap_all_positions(self, state, replacement_card):
        ''' calculate the features for swapping at all positions '''

        # create a blank 2 dimensional array - which we will fill with new values
        all_features = np.array([[None]*5]*(self.num_rows * 2))

        for i in range(self.num_cols * 2):
            all_features[i] = self._extract_features_from_stats(state, replacement_card, location)

        return all_features


    def _calc_move_score(self, state, actions, card_in_hand=None):
        ''' Takes a vector of features and makes a move based upon history,
            known q-values, and computes the next move.
            Takes card param from turn_phase_2 when called by that method
        '''

        if self.verbose:
            print 'Calculating the move score for actions: {}'.format(actions)

        # for turn phase 1 we should calculate all the possible swaps and then take the maximum value
        # as our decision for each action

        # for phase 2 we should calculate all of the possible moves and act upon the one that is maximal

        features = []
        if card_in_hand == None:
            # then we're looking at turn phase 1 - so no locations necessary
            for action in actions:
                raw_features = self._extract_features_from_state(state, action, location=None, card_in_hand=None)
                # replace score with proper matrix multiplication via numpy
                score = (raw_features * self.weights.transpose())[0,0]

                if self.verbose:
                    print '\n Features for action: {} \n'.format(action)
                    print 'Features: {} \n'.format(raw_features)
                    print 'Weights: {}'.format(self.weights)
                    print 'Score: {} \n'.format(score)

                # We might want ot add the discount in here
                features.append({'raw_features': raw_features,
                                 'score': score,
                                 'action': action})
        else:
            # we will need to fan out the swap action to include swapping with all possible
            # locations in the hand
            for action in actions:
                if action == 'swap':
                    for i in range(self.num_cols * 2):

                        raw_features = self._extract_features_from_state(state, action, location=i, card_in_hand=card_in_hand)
                        #score = sum([f * self.weights[idx] for idx, f in enumerate(raw_features)])

                        # replace score calculation
                        score = (raw_features * self.weights.transpose())[0,0]
                        row = int(i % 2)
                        col = int(math.floor(i / 2))
                        features.append({'raw_features':raw_features,
                                         'score': score,
                                         'action': (action, row, col)})
                else:
                    raw_features = self._extract_features_from_state(state, action, location=None, card_in_hand=None)

                    #score = sum([raw_features[i] * self.weights[i] for i, f in enumerate(raw_features)])
                    # Replace with numpy matrix based calc
                    score = (raw_features * self.weights.transpose())[0,0]

                    if self.verbose:
                        print 'Raw features: {}'.format(raw_features)
                        print 'Weights: {}'.format(self.weights)
                        print 'Score from features: {}'.format(score)

                    # We might want ot add the discount in here
                    features.append({'raw_features': raw_features,
                                        'score': score,
                                        'action': action})
        print '\nFeatures leaving _calc: {}'.format(features)
        return features


    def _update_weights(self, q_state_obj, q_prime_state_obj, reward, learning_rate):
        ''' Update the weights associated for a particular Q-State '''

        if self.verbose:
            print 'Initial weights for update {}'.format(self.weights)

        # difference = [r + gamma * max Q(s`,a`)] - Q(s,a)
        # Going to use a gamma of 1 for no discount on future Q state values,
        # as the card game naturally tends towards lower future rewards already
        difference = (reward + q_prime_state_obj['score']) - q_state_obj['score']
        # Now we need to update the weights iteratively using the saved difference and learning rate
        # w_i <- w_i + (learning_rate * difference * f_i(s,a) where f_i is feature i
        for i in range(self.weights.shape[1]):
            self.weights[0, i] = self.weights[0, i] + (learning_rate * difference * q_state_obj['raw_features'][0, i]) # adds regularization


        #print 'New Weights: {}'.format([(w) / (max(self.weights[0,:]+[.1]) * 0.01) for w in self.weights[0,:]])
        #self.weights = np.matrix([(w) / (max(self.weights+[.1]) * 0.01) for w in self.weights])

        if self.verbose:
            print 'Weights after update {}'.format(self.weights)


    def _initialize_blank_model(self, length=5):
        ''' return a blank model - weights initialized to 0
            Going to check performance with random weight initialization
            first, but in the future it may be preferable to have
            random weights along an even distribution, but that seems
            like an optimization best left for later
        '''

        return np.matrix(np.zeros(length))

