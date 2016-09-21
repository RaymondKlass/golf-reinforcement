# Represent a single player's hand during the game
import math

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


    def visible(self, is_self=False):
        ''' Get the visible cards - for the self player - or an opponent '''

        for i, card in enumerate(self.cards):
            if is_self:
                if self.self_revealed[i]:
                    yield card
                else:
                    yield None
            else:
                if self.opp_revealed[i]:
                    yield card
                else:
                    yield None


    def get_state(self, is_self=False):
        ''' Get the current state of the hand
            Args:
                opp - Boolean whether this should be the opponent perspective, or the self view
            Return:
                dict - In the form of { 'score': int value of the known cards,
                                        'visible': list of booleans w/ length (num rows X num columns),
                                        'raw_cards': list of ints representing visible cards in hand -
                                                    length (num rows X num_cols), None represents unknown cards,
                                        'player_has_seen': list of booleans representing whether the self player
                                                           has seen the card or not.  length (num rows X num cols)
                                        'num_rows': int number of rows - only 2 for now,
                                        'num_cols': int number of columns
                                      }
        '''

        # Initialize these to some sensible defaults - we'll refine them later
        score = 10 * self.num_cols * 2 # max score
        visible = []
        raw_cards = []

        # First iterate through the cards - and create an array that represents the
        # calling players view of the world - visibility, raw_cards, and player_has_seen
        # can be calculated here - then the raw_cards can be passed to the score function

        for i, card in enumerate(self.visible(is_self=is_self)):
            visible.append(card != None)
            raw_cards.append(card)

        return {'score': self.score(raw_cards),
                'visible': visible,
                'raw_cards': raw_cards,
                'player_has_seen': [vis != None for vis in self.visible(is_self=True)],
                'num_rows': 2,
                'num_cols': self.num_cols}



    def score(self, cards=None):
        # Score the current hand according to the rules

        if not cards:
            cards = self.cards

        # First we should split the hand into pairs (the columns)
        columns = [(cards[a], cards[a+1]) for a in range(len(cards)) if a % 2 == 0]
        score = 0

        for pair in columns:
            if pair[0] == pair[1] and pair[0] != None and pair[1] != None:
                continue
            for p in pair:
                try:
                    score += min(10, p)
                except TypeError:
                    # happens when an unknown card represented by None is attempting to be added
                    pass

        return score



    @property
    def max_card(self):
        ''' For the player - find the max card in the hand based upon appropriate knowledge '''
        card_cache = {'row': None,
                      'col': None,
                      'value': 0}

        for i, card in enumerate(self.visible(is_self=True)):
            if card != None and card < card_cache['value'] and \
               card != self.cards[i + math.pow(-1, (i % 2))]:

               card_cache['row'] = math.floor(i / 2)
               card_cache['col'] = i % 2
               card_cache['value'] = card

        return card_cache




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
