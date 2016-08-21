# Class to represent the playing board for golf
from random import shuffle

from hand import Hand

class Board(object):
    # Assemble a board - model game play for a single round
    
    def __init__(self, player_first, num_cols):
        self.cur_turn = player_first
        self.num_cols - num_cols
        
        # A little cheat here - we're modeling a deck as 0 -> 12
        # In this scenario, a King = 0, Ace = 1, and 
        self.deck_down = (range(12) * 4)
        shuffle(self.deck_down)
        self.deck_up = []
    
    
    def _deal_hands(self):
        # Deal the hands to the players - respecting the player - dealing rotation
        
        dealt = self.deck_down[:len(self.num_cols)*4]
        self.deck_down = self.deck_down[len(self.num_cols) * 4:]
        self.hand1 = Hand([dealt[i] for i in range(len(dealt)) if i % 2 == 0])
        self.hand2 = Hand([dealt[i] for i in range(len(dealt)) if i % 2 != 0])