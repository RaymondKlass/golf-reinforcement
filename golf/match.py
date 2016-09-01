from board import Board

class Match(object):
    
    def __init__(self, player1, player2, holes=9, num_cols=2):
        self.players = (player1, player2,)
        self.score = (0,0)
        self.total_holes = (holes - 1) # Since we're 0 indexed
        
    
    def play_match(self):
        ''' Play all of the holes for a single match '''
        
        for turn in range(self.total_holes):
            board = Board(self.players)
            