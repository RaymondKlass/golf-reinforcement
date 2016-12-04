""" Basic implementation of Q-Learning based player, named after
    Watkins who first introduced Q-Learning, and later proved it's
    convergence in 1992 https://en.wikipedia.org/wiki/Q-learning
"""
import cPickle
from golf.players.trainable_player_base import TrainablePlayer
from golf.players.player_utils import PlayerUtils

class QWatkins(TrainablePlayer, PlayerUtils):
    """ Trainable player based on basic Q-Learning through
        hand-crafted features, Q function approximation,
        and simple linear function approximation
    """

    def __init__(self, model_file, num_cols=2, *args, **kwargs):
        """ Initialize player and load model if available -
            otherwise player will start with a randomly initialize model """

        self.num_cols = num_cols
        self.is_training = False # This will be over-written if self.setup_trainer() is run

        try:
            with open(model_file, 'rb') as model_file:
                self.model = cPickle.load(model_file)
        except IOError:
            # model does not exist
            if self.verbose:
                print 'Model {} could not be found - starting from scratch'.format(model_file)

            self.model = self._initialize_blank_model()


    def turn_phase_1(self, state, possible_moves=['face_up_card', 'face_down_card', 'knock']):
        ''' Takes the state of the board and responds with the turn_phase_1 move recommended '''

        pass


    def turn_phase_2(self, card, state, possible_moves=['return_to_deck', 'swap']):
        ''' Takes the state of the board and responds with the turn phase 2 move recommended '''

        pass


    def _extract_features_from_state(self, state, action):
        ''' Takes an input state and outputs a vector of features for use with model
            - Should be specific for which turn_phase we are, but otherwise selecting
              fewer features here will help reduce the complexity of the search space
            - Need to represent not only the value, but also the Q-value as these features
              will be used as a way to describe the value of a Q-State
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
        - replacement value - unknown cards +1 Sigma
        - replacement value - unknown cards +2 Sigma
        - replacement value - unknown cards -1 Sigma
        - replacement value - unknown cards -2 Sigma
        """

        return None


    def _update_weights(self, features, learning_rate):
        ''' Update the weights associated for a particular Q-State '''

        # Still need to figure out the best way to pass and update from the game's
        # exit state - as there's not normally an endpoint for it - so I may
        # need to add the spec to the trainable player base class

        pass


    def _calc_next_move(self, state, possible_actions, epsilon_lift=0):
        ''' Takes a vector of features and makes a move based upon history,
            known q-values, and computes the next move.

            epsilon_lift is used to artificially inflate the Q values for
            Q-States that have been rarely or not visited.  Helpful for exploration
        '''

        pass


    def _initialize_blank_model(self, length=5):
        ''' return a blank model - random weights between -1 and 1
            Going to check performance with random weight initialization
            first, but in the future it may be preferable to have
            random weights along an even distribution, but that seems
            like an optimization best left for later
        '''

        return [(random.random() * 2) - 1 for _ in range(length)]

