''' Tests for Golf matches - will include unit and more integration style tests
    as this is the component where much of the logic comes together
'''
import unittest2
from golf.board import Board
from golf.hand import Hand
from golf.players.player_base import Player


class TestBoard(unittest2.TestCase):
    ''' Test the match module - both unit and integration tests '''

    def setUp(self):
        ''' Setup the board module to run through functionality '''

        # let's create a 1 vs 1 game by default - could be extended later
        self.players = [self._generate_base_player()] * 2
        self.num_cols = 2

        # No need to test the verbose flag - we'll leave it turned off
        self.verbose = False
        self.board = Board(self.players, self.num_cols, self.verbose)


    def _generate_base_player(self):
        ''' return a very basic player - which tests must over-write
            the logic of - for validation and assertion.
        '''

        return Player()


    def test_dealing_hands(self):
        ''' Test dealing 2 hands - make sure hands are correct, and
            remaining deck is also correct
        '''

        # Test the initial state of the deck and the board
        self.assertEqual(len(self.board.deck_visible), 0)
        self.assertEqual(len(self.board.deck_down), 52)
        self.assertEqual(len(self.board.hands), 0)

        # deal the hands
        self.board._deal_hands()

        # num_cols * 2(num_rows) * 2(num
        self.assertEqual(len(self.board.deck_down), 52 - (self.num_cols * 2 * len(self.players)))
        self.assertEqual(len(self.board.hands), len(self.players))

        # We should also make sure that the cards that have been dealt to the players along
        # with the rest of the deck add up to the correct 52 card deck
        cards_in_hand = [c for c in sum([h.cards for h in self.board.hands], [])]

        self.assertEqual(len(cards_in_hand), self.num_cols * len(self.players) * 2)

        # to test equality - we need to create a deck of sorted cards
        fresh_deck = (range(13) * 4).sort()
        used_deck = (cards_in_hand + self.board.deck_down).sort()

        self.assertEqual(fresh_deck, used_deck)


    def test_get_state(self):
        ''' Test getting the state from player's hands '''

        self.board._deal_hands()
        self.assertEqual(self.players[0], self.board.players[0])
        state = self.board.get_state_for_player(0)
        self.assertEqual(state['self'], self.board.hands[0].get_state(is_self=True))
        self.assertEqual(state['opp'][0], self.board.hands[1].get_state(is_self=False))

        state = self.board.get_state_for_player(1)
        self.assertEqual(state['self'], self.board.hands[1].get_state(is_self=True))
        self.assertEqual(state['opp'][0], self.board.hands[0].get_state(is_self=False))

        self.assertEqual(state['deck_up'], self.board.deck_visible)
