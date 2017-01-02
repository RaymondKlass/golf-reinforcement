''' Base class for trainable players '''

from golf.players.player_base import Player

class TrainablePlayer(Player):

    def __repr__(self):
        return 'Trainable Player'


    def __init__(self, *args, **kwargs):
        super(TrainablePlayer, self).__init__(*args, **kwargs)
        self._is_trainable = False


    @property
    def is_training(self):
        return self._is_training


    @is_training.setter
    def is_training(self, value):
        """ Set the training value - so that a single player can be 'switched' between
            training and playing optimally.  This will be important for running the
            player in evaluation mode
        """

        # Here we're going to simply set the value - but each model should over-ride
        # this method to archive values etc for when values are changed again.
        self._is_training = value


    @staticmethod
    def valid_trainable_args(self):
        """ Setup the list of arguments that are acceptable for training -
        """

        return dict()


    def setup_trainer(self):
        """ Trainable players are required to implement this one additional method
            to the methods that are already required in Player base class.

            This method should setup the additional parameters etc needed to
            train the player through actual game play - such as learning rate etc.
        """

        raise NotImplementedError


    def update_weights(self, state, card=None, reward=0, possible_moves=[]):
        """ Trainable players should implement this method so that weight updates
            can happen after a turn
        """

        raise NotImplementedError