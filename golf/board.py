# Class to represent the playing board for golf
from random import shuffle
from hand import Hand

from hand import Hand

class Board(object):
    # Assemble a board - model game play for a single round
    
    def __init__(self, players, num_cols):
        ''' Args:
                players: set of players
                num_cols: game board layout
        '''
        
        self.player = players
        self.num_cols - num_cols
        
        # A little cheat here - we're modeling a deck as 0 -> 12
        # In this scenario, a King = 0, Ace = 1, and 
        self.deck_down = (range(12) * 4)
        shuffle(self.deck_down)
        self.deck_up = []
    
    
    @property 
    def deck_visible(self):
        return self.deck_up[-1]
    
    
    def _deal_hands(self):
        # Deal the hands to the players - respecting the player - dealing rotation
        
        dealt = self.deck_down[:len(self.num_cols)*4]
        self.deck_down = self.deck_down[len(self.num_cols) * 4:]
        self.hand1 = Hand([dealt[i] for i in range(len(dealt)) if i % 2 == 0])
        self.hand2 = Hand([dealt[i] for i in range(len(dealt)) if i % 2 != 0])
        
    
    def step_turn(self):
        # A simple function to represent moving 1 single turn
        # which could result in several changes in game state
        
        self.cur_turn += 1 # we increment this and then evaluate the % 2 value
        cur_player = (self.hand1, self.hand2,)[self.cur_turn % 2]
        
        # At some point we need to select a move for the player - so let's place
        # something here to model that activity
        possible_moves = ('knock', 'swap', 'pickup_top')
        
        return cur_player.move()
            