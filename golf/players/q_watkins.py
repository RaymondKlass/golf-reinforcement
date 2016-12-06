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
        self._cache_state_derivative_values(state)
        return self._take_turn(state, possible_moves)


    def _take_turn(self, state, possible_moves):
        """ Since the general move logic will be the same for the first and the second phase
            of the players turn, let's further abstract that out into this method
        """

        turn_decision = [(action, self._calc_move_score(state, action),) for action in possible_moves]
        sorted_moves = turn_decision.sort(key=lambda x: x[1], reverse=True)
        return sorted_moves[0][0]


    def _cache_state_derivative_values(self, state):
        """ In order to calculate the features that the model is based on, we'll need to know
            a couple of important values - we should just calculate these once per turn phase
        """

        self.avg_card = self._calc_average_card(state)
        self.card_std_dev = self._calc_std_dev(state)



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

        # this is where the real stuff gets done
        #


        return None


    def _update_weights(self, features, learning_rate):
        ''' Update the weights associated for a particular Q-State '''

        # Still need to figure out the best way to pass and update from the game's
        # exit state - as there's not normally an endpoint for it - so I may
        # need to add the spec to the trainable player base class

        pass


    def _calc_move_score(self, state, action):
        ''' Takes a vector of features and makes a move based upon history,
            known q-values, and computes the next move.
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

