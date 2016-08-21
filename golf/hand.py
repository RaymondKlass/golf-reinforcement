# Represent a single player's hand during the game

class Hand(object):
    
    def __init__(self, cards_dealt):
        # Cards are encoded as a single array 
        # with i % 2 == 0 cards in the bottom row
        # and i @ 2 != 0 cards in the top row
        
        if cards_dealt % 2 != 0:
            print('Number of cards dealt must be divisible by 2')
            raise 
        
        self.cards = cards_dealt
        self.num_cols = cards_dealt / 2
        
        # We start off with the bottom cards revealed to us
        self.self_revealed = [c % 2 == 0 for c in range(self.cards)]
        self.opp_revealed = [False] * len(self.cards)
        
    
    @property
    def score(self):
        # Score the current hand according to the rules
        
        # First we should split the hand into pairs (the columns)
        columns = [(a[i], a[i+1]) for a in range(len(self.cards)) if a % 2 == 0]
        score = 0
        
        for pair in columns:
            if pair[0] == pair[1]:
                continue
            for p in pair:
                score += min(10, p)
        
        return score
    
    
    def __str__(self):
        # Printable Version of a players hand
        # that reveals everything (all information)
        return '  '.join('  {}\n {}'.format([c for c in self.cards if c % 2 != 0],
                                         [c for c in self.cards if c % 2 == 0]))
                                         
    
    
    def _swap(self, row, col, new_card, source_revealed = False):
        # swap the card by row and column with the newly given card
        self.cards[(row * self.num_cols) + col] = new_card
        
        self.revealed[(row * self.num_cols) + col] = source_revealed