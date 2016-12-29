# Base player class

class Player(object):

    def __init__(self, verbose=False, *args, **kwargs):
        self.verbose = verbose


    def __repr__(self):
        return 'Player'


    @staticmethod
    def valid_args():
        """ Return a dict of valid arguments that will be passed to the particular module,
            the key is the arg expected from execution, the value is the key to be passed
            to the __init__ method
        """

        return {'verbose': 'verbose'}



    def turn_phase_1(self, state, possible_moves=['face_up_card', 'face_down_card', 'knock']):
        """ Phase 1 of the turn - needs to choose to
            1.  Take card face up
            2.  Take face down card from top of deck
            3.  Knock
            Args:
                state: State object that hold the current state from the player's perspective
                possible_moves: List of Strings that describe the possible moves
            Return:
                String representing the chosen move
        """
        raise NotImplementedError


    def turn_phase_2(self, card, state, possible_moves=['return_to_deck', 'swap']):
        """ If player gets here, then they need to exchange the card with one of their cards
            or place the card on the top of the discard pile if they drew a face down card """

        raise NotImplementedError
