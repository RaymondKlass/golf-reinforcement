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
        self._is_trainable = False # This will be over-written if self.setup_trainer() is run

        self.epsilon = 0 # Exploration
        self.start_model_file = model_file

        try:
            with open(model_file, 'rb') as model_file:
                self.weights = cPickle.load(model_file)

                if self.verbose:
                    print 'Successfully loaded model'

        except IOError:
            # model does not exist
            if self.verbose:
                print 'Model {} could not be found - starting from scratch'.format(model_file)

            self.weights = self._initialize_blank_model()


    @property
    def is_trainable(self):
        return self._is_trainable


    @is_trainable.setter
    def is_trainable(self, value):
        """ Set the training value - so that a single player can be 'switched' between
            training and playing optimally.  This will be important for running the
            player in evaluation mode
        """

        if not value and self.is_trainable:
            # We were in trainable mode - now we should archive the values and set optimal ones for the time being
            # For now the only param which explcictly needs to be reset is epsilon
            self.hyperparam_archive = {'epsilon': self.epsilon }
            # Reset the various params to optimal vals
            self.epsilon = 0
        elif value and not self.is_trainable:
            # Training was off - now if should be turned back on
            if self.hyperparam_archive and 'epsilon' in self.hyperparam_archive:
                self.epsilon = self.hyperparam_archive['epsilon']

        self._is_trainable = value


    def setup_trainer(self, checkpoint_dir, learning_rate=0.0001, epsilon=0.2, discount=0.99, *args, **kwargs):
        ''' Setup the training variable
            Args:
                checkpoint_dir: string -> Directory to store checkpoint files
                learning_rate: float -> single rate for now, may change to be a schedule
                eval_freq: integer -> iterations between running an evaluation
        '''

        self.epsilon = epsilon
        self.discount = discount
        self.checkpoint_dir = checkpoint_dir
        self.learning_rate = learning_rate
        self._is_trainable = True
        self.q_state = None

        # Introspect the number of epochs from a checkpoint file in proper format
        try:
            self.starting_epochs = int(self.start_model_file.split('_')[-1].split('.')[0])
        except ValueError:
            # Cannot parse an int from the value
            self.starting_epochs = 0



    def save_checkpoint(self, epochs):
        ''' Save a checkpoint file in the pre-specified directory, in a name - date format '''

        cur_time = str(time.time()).replace('.', '_')
        epochs = self.starting_epochs + epochs
        file_path = os.path.join(self.checkpoint_dir, '{}_{}.pkl'.format(cur_time, epochs))

        with open(file_path, 'wb') as outfile:
            cPickle.dump(self.weights, outfile)

        if self.verbose:
            print 'Saved checkpoint: {}'.format(file_path)


    def turn_phase_1(self, state, possible_moves=['face_up_card', 'face_down_card', 'knock']):
        ''' Takes the state of the board and responds with the turn_phase_1 move recommended '''

        if self.verbose:
            print 'Turn Phase 1: '
            print 'State: {}'.format(state)

        self._cache_state_derivative_values(state)
        turn = self._take_turn(state, possible_moves)
        return turn


    def update_weights(self, state, card=None, reward=0, possible_moves=[]):
        ''' Takes a new state and executes the weight update '''
        # It's possible this player gets called before they have ever gone - in that case ignore the results

        try:
            old_q_state = dict(self.q_state)
        except TypeError:
            print 'Return without success'
            return

        self._cache_state_derivative_values(state, card)

        # For the update weights - this needs to be the optimal move - so no epsilon randomness should be used
        self._take_turn(state, possible_moves, card, epsilon=0)

        self._update_weights( q_state_obj=old_q_state,
                              q_prime_state_obj=self.q_state,
                              reward=reward, # Since this update will never result from an exit state
                              learning_rate=self.learning_rate)



    def turn_phase_2(self, card, state, possible_moves=['return_to_deck', 'swap']):
        ''' Takes the state of the board and responds with the turn phase 2 move recommended '''

        if self.verbose:
            print 'Turn Phase 2: '
            print 'State: {} \n Card: {}'.format(state, card)

        self._cache_state_derivative_values(state, card)
        turn = self._take_turn(state, possible_moves, card)
        return turn


    def _take_turn(self, state, possible_moves, card=None, epsilon=None):
        """ Since the general move logic will be the same for the first and the second phase
            of the players turn, let's further abstract that out into this method
        """
        turn_decisions = self._calc_move_score(state, possible_moves, card)
        turn_decisions.sort(key=lambda x: x['score'], reverse=True)
        # if we're training then we're going to need to save the value of the Q-State for updating weights later
        # Q(s,a) -> calculated value of the Q-State that we're committing to

        if self.is_trainable:
            if epsilon == None:
                epsilon = self.epsilon

            choice = random.random()
            if choice < epsilon:
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

        return decision['action']


    def _cache_state_derivative_values(self, state, card_in_hand=None):
        """ In order to calculate the features that the model is based on, we'll need to know
            a couple of important values - we should just calculate these once per turn phase
        """

        self.avg_card = self._calc_average_card(state, card_in_hand)
        self.card_std_dev = self._calc_std_dev(state)
        self.min_opp_score = min([a['score']+(len([b for b in a['raw_cards'] if b == None]) *  self.avg_card) for a in state['opp']])
        self.self_avg_score = state['self']['score'] + len([b for b in state['self']['raw_cards'] if b == None]) * self.avg_card


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

        return result


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


    def _calc_swap_all_positions(self, state, replacement_card):
        ''' calculate the features for swapping at all positions '''

        # create a blank 2 dimensional array - which we will fill with new values
        all_features = np.array([[None]*5]*(self.num_cols * 2))

        for i in range(self.num_cols * 2):
            all_features[i] = self._extract_features_from_state(state, replacement_card, i)

        return all_features


    def _calc_scores(self, raw_features):
        ''' Expects a potentially multi-dimensional numpy array raw_features
            which will be used to compute the score for each row of features
        '''

        #result =  (self.min_opp_score - self.self_avg_score) - (self.min_opp_score - raw_features)
        result = self.min_opp_score - raw_features
        result = np.dot(result, np.transpose(self.weights))

        return result


    def _calc_move_score(self, state, actions, card_in_hand=None):
        ''' Takes a vector of features and makes a move based upon history,
            known q-values, and computes the next move.
            Takes card param from turn_phase_2 when called by that method
        '''


        features = []
        for action in actions:
            if action in ('face_up_card', 'face_down_card',):
                # In this case we should try all of the swaps and take the maximum
                if action == 'face_up_card':
                    replacement = state['deck_up'][-1]
                else:
                    replacement = self.avg_card

                raw_features = self._calc_swap_all_positions(state, replacement)
                result = self._calc_scores(raw_features)
                max_result = max(result.flatten())

                features.append({'raw_features': raw_features[list(result.flatten()).index(max_result)],
                                 'score': max_result,
                                 'action': action})


            elif action in ('knock', 'return_to_deck',):
                # Send for the single feature calculation with no replacement - not sure this is 100% representative from
                # a probability calc standpoint - should the assummed no replacement take into account the placing
                # of the card in hand back on the top of the deck?  Does it already?
                raw_features = self._extract_features_from_state(state, replacement_card=None, location=None)
                result = self._calc_scores(raw_features)
                features.append({'raw_features': raw_features,
                                 'score': result,
                                 'action': action})

            elif action == 'swap':
                # Calculate all of the swap values
                raw_features = self._calc_swap_all_positions(state, card_in_hand)
                result = self._calc_scores(raw_features)
                for i, score in enumerate(result.flatten()):
                    row, col = self._calc_row_col_for_index(i)
                    features.append({'raw_features': raw_features[i],
                                     'score': score,
                                     'action': (action, row, col)})

        return features


    def _update_weights(self, q_state_obj, q_prime_state_obj, reward, learning_rate):
        ''' Update the weights associated for a particular Q-State '''

        # It's possible the weights have changed since the score calculation (in the case of the final weight update
        # so it's possible we need to re-calculate the score of the old_q_state

        q_state_obj['score'] = self._calc_scores(q_state_obj['raw_features'])

        # difference = [r + gamma * max Q(s`,a`)] - Q(s,a)
        # Going to use a gamma of 1 for no discount on future Q state values,
        # as the card game naturally tends towards lower future rewards already
        difference = (reward + (self.discount * q_prime_state_obj['score'])) - q_state_obj['score']

        # Now we need to update the weights iteratively using the saved difference and learning rate
        # w_i <- w_i + (learning_rate * difference * f_i(s,a) where f_i is feature i
        self.weights = self.weights + (learning_rate * difference * q_state_obj['raw_features'])


    def _initialize_blank_model(self, length=5):
        ''' return a blank model - weights initialized to 0
            Going to check performance with random weight initialization
            first, but in the future it may be preferable to have
            random weights along an even distribution, but that seems
            like an optimization best left for later
        '''

        return np.zeros(length)
