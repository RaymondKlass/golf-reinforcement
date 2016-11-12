""" Test the logic around the random player """
from golf.unit_tests.test_player.player_test_base import PlayerTestBase
from golf.players.random_player import RandomPlayer

class TestRandomPlayer(PlayerTestBase):
    """ Test the Random Player
        Since this is the base-line player, tests to make sure that the
        moves it makes are simply legal should be sufficient.
    """

    def setUp(self):
        """ Setup the player and hands """

        # Load the players and their state
        self._load_hands()
        self.player = RandomPlayer()


    def test_turn_phase_1(self):
        """ Test turn Phase 1 - should be one of the possible moves - ['face_up_card', 'face_down_card', 'knock'] """

        for _ in range(100):
            # Test phase 1 - 100 times and validate that all the moves are valid
            state = self._get_state_for_hand(0)
            move = self.player.turn_phase_1(state)
            self.assertIn(move, ['face_up_card', 'face_down_card', 'knock'])



    def test_turn_phase_2(self):
        """ Test turn Phase 2 - should be a valid move, and a valid card selection if appropriate """

        for _ in range(100):
            # Test 100 repetitions since moves made are random
            state = self._get_state_for_hand(0)
            move = self.player.turn_phase_2(self.deck_up[-1], state)
            self.assertIn(move[0], ['return_to_deck', 'swap'])

            # Let's also check that is 'swap' was chosen the row, column are valid
            if move[0] == 'swap':
                self.assertLess(move[1], 2)
                self.assertLess(move[2], 2)
                self.assertGreaterEqual(move[1], 0)
                self.assertGreaterEqual(move[2], 0)