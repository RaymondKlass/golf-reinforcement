# Represent a single player's hand during the game

class Hand(object):

    def __init__(self, cards_dealt):
        # Cards are encoded as a single array
        # with i % 2 == 0 cards in the bottom row
        # and i @ 2 != 0 cards in the top row

        if len(cards_dealt) % 2 != 0:
            print('Number of cards dealt must be divisible by 2')
            raise

        self.cards = cards_dealt
        self.num_cols = len(cards_dealt) / 2

        # We start off with the bottom cards revealed to us
        self.self_revealed = [c % 2 == 0 for c in range(len(self.cards))]
        self.opp_revealed = [False] * len(self.cards)


    @property
    def score(self):
        # Score the current hand according to the rules

        # First we should split the hand into pairs (the columns)
        columns = [(self.cards[a], self.cards[a+1]) for a in range(len(self.cards)) if a % 2 == 0]
        score = 0

        for pair in columns:
            if pair[0] == pair[1]:
                continue
            for p in pair:
                score += min(10, p)

        return score


    @property
    def shape(self):
        return (2, self.num_cols)


    def __str__(self):
        # Printable Version of a players hand
        # that reveals everything (all information)
        return '  '.join('  {}\n {}'.format([self.cards[i] for i in range(len(self.cards)) if i % 2 == 0],
                                         [self.cards[i] for i in range(len(self.cards)) if i % 2 != 0]))



    def swap(self, row, col, new_card, source_revealed = False):
        # swap the card by row and column with the newly given card
        old_card = self.cards[(col * 2) + row]
        self.cards[(col * 2) + row] = new_card
        self.self_revealed[(col * 2) + row] = True
        self.opp_revealed[(col * 2) + row] = source_revealed
        return old_card
