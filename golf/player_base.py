# Base player class

class Player(object):
    
    def __init__(self, hand):
        self.hand = hand
    
    
    def turn_phase_1(self, state, possible_moves=['face_up_card', 'face_down_card', 'knock']):
        """ Phase 1 of the turn - needs to choose to 
            1.  Take card face up
            2.  Take face down card from top of deck
            3.  Knock
        """
        raise NotImplementedError
    
    
    def turn_phase_2(self, state):
        """ If player gets here, then they need to exchange the card with one of their cards
            or place the card on the top of the discard pile if they drew a face down card """
            
        raise NotImplementedError
        