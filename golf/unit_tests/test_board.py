''' Tests for Golf board - will include unit and more integration style tests
    as this is the component where much of the logic comes together
'''
import unittest2
from golf.board import Board
from golf.hand import Hand
from golf.players.player_base import Player


class TestBoard(unittest2.TestCase):
    ''' Test the board module - both unit and integration tests '''

    def setUp(self):
        ''' Setup the board module to run through functionality '''

        # let's create a 1 vs 1 game by default - could be extended later
        self.players = [self._generate_base_player() for a in range(2)]
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


    def test_basic_knock(self):
        ''' Basic test of playing the game '''

        self.num_turns = 0

        def _knock(state, possible_moves):
            self.num_turns += 1
            self.assertEqual(state['deck_up'], self.board.deck_visible)
            return 'knock'

        self.players[0].turn_phase_1 = _knock
        self.players[1].turn_phase_1 = _knock

        self.board.play_game()
        self.assertEqual(self.num_turns, 2)


    def test_basic_up_card(self):
        ''' Test Basic player taking the up-card '''

        def _knock_1(state, possible_moves):
            self.assertEqual(state['deck_up'], self.board.deck_visible)
            self.assertEqual(possible_moves, ('face_up_card', 'face_down_card', 'knock',))
            return 'knock'

        def _face_up_1(state, possible_moves):
            self.assertEqual(possible_moves, ('face_up_card', 'face_down_card', 'knock',))
            return 'face_up_card'

        def _face_up_2(card, state, possible_moves):
            self.assertEqual(possible_moves, ('swap',))
            self.assertEqual(self.board.deck_visible, [])
            self.assertEqual(len(state['deck_up']), 0)
            self.new_card = card
            return ('swap', 0, 1)

        self.players[0].turn_phase_1 = _knock_1
        self.players[1].turn_phase_1 = _face_up_1
        self.players[1].turn_phase_2 = _face_up_2

        self.board.play_game()
        self.assertEqual(self.board.hands[1].cards[self.board.hands[1]._coords_to_index(0, 1)], self.new_card)
        self.assertEqual(len(self.board.deck_visible), 1)


    def test_basic_down_card(self):
        ''' test Basic player taking face-down card and swap'''

        def _knock_1(state, possible_moves):
            return 'knock'

        def _face_down_1(state, possible_moves):
            self.assertEqual(possible_moves, ('face_up_card', 'face_down_card', 'knock',))
            return 'face_down_card'

        def _face_down_2(card, state, possible_moves):
            self.assertEqual(possible_moves, ('swap', 'return_to_deck'))
            self.assertEqual(len(self.board.deck_visible), 1)
            self.assertEqual(len(state['deck_up']), 1)
            self.new_card = card
            return ('swap', 1, 1)

        self.players[0].turn_phase_1 = _knock_1
        self.players[1].turn_phase_1 = _face_down_1
        self.players[1].turn_phase_2 = _face_down_2

        self.board.play_game()
        self.assertEqual(self.board.hands[1].cards[self.board.hands[1]._coords_to_index(1, 1)], self.new_card)
        self.assertEqual(len(self.board.deck_visible), 2)


    def test_basic_down_card_return(self):
        ''' test Basic player taking face-down card and return'''

        def _knock_1(state, possible_moves):
            return 'knock'

        def _face_down_1(state, possible_moves):
            self.assertEqual(possible_moves, ('face_up_card', 'face_down_card', 'knock',))
            return 'face_down_card'

        def _face_down_2(card, state, possible_moves):
            self.assertEqual(possible_moves, ('swap', 'return_to_deck'))
            self.assertEqual(len(self.board.deck_visible), 1)
            self.assertEqual(len(state['deck_up']), 1)
            self.new_card = card
            return ('return_to_deck',)

        self.players[0].turn_phase_1 = _knock_1
        self.players[1].turn_phase_1 = _face_down_1
        self.players[1].turn_phase_2 = _face_down_2

        self.board.play_game()
        self.assertEqual(self.board.deck_visible[-1], self.new_card)
        self.assertEqual(len(self.board.deck_visible), 2)

