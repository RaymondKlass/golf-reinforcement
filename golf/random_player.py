# A Random player - who makes their choice randomly at every step 
import random
from player_base import Player

class RandomPlayer(Player):
    
    def turn_phase_1(self, state, possible_moves=['face_up_card', 'face_down_card', 'knock']):
        """ We're just going to make a random selection at every step """
        
        return random.choice(possible_moves)
        
        
    def turn_phase_2(self, card, state, possible_moves=['return_to_deck', 'swap']):
        """ Again - this will be a random choice """
        
        choice = random.choice(possible_moves)
        
        if choice == 'swap':
            # We need to figure out which card we'll be swapping with
            # we should do this at random too
            
            dims = self.hand.shape()
            rand_row = random.randint(0,dims[0]-1)
            rand_column = random.randint(0, dims[1]-1)
            self.board.swap(card, rand_row, rand_col)
        
        else:
            self.board.return_to_deck(card)