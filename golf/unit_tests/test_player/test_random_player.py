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


    def test_turn_phase_1(self):
        """ Test turn Phase 1 - should be one of the possible moves - ['face_up_card', 'face_down_card', 'knock'] """

        pass