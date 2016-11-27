''' Base class for trainable players '''

from golf.players.player_base import Player

class TrainablePlayer(Player):

    def __repr__(self):
        return 'Trainable Player'


    def setup_trainer(self):
        """ Trainable players are required to implement this one additional method
            to the methods that are already required in Player base class.

            This method should setup the additional parameters etc needed to
            train the player through actual game play - such as learning rate etc.
        """

        raise NotImplementedError