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

        For the 1st phase, the player needs to make a decision between [knock, face_up_card, face_down_card]
        - Values should be based on player-score differentials, or in other words the utility of each Action
        - best guaranteed replacement value (0 for face_down_card)
        - best replacement value assuming average card (for all unknown cards - up or down)
        - min replacement value (lowest possible replacement value)
        - max replacement value (highest possible replacement value)

        For the 2nd phase, the player needs to decide [return_card, replace a specific card]

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


    def _initialize_blank_model(self):
        ''' return a blank model - random weights in the correct format '''

        return None # this needs to be implemented