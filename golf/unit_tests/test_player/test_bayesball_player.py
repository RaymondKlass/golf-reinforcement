''' Bayesball player - makes decisions based on calculated probabilities, so
    appropriate unit tests would confirm the expected policies
'''

from golf.unit_tests.test_player.player_test_base import PlayerTestBase
from golf.players.bayesball_player import BayesballPlayer

class TestBayesballPlayer(PlayerTestBase):
    ''' Test the policies for the bayesball player '''


    def _setup_bayesball_player(self, min_distance=8, card_margin=1, unknown_card_margin=1, num_cols=2):
        ''' Setup a basic bayesball player whose options can be over-written '''

        self.min_distance = min_distance
        self.card_margin = card_margin
        self.unknown_card_margin = unknown_card_margin
        self.num_cols = num_cols

        self.bayesball_player = BayesballPlayer(min_distance=min_distance,
                                                card_margin=card_margin,
                                                unknown_card_margin=unknown_card_margin,
                                                num_cols=num_cols)


    def test_player_name(self):
        ''' Basic test for setup '''

        self._setup_bayesball_player()
        self.assertEqual(str(self.bayesball_player).lower(), 'Bayesball_Player'.lower())


    def test_calc_score_diff(self):
        ''' Test calculating the score differential between payers '''

        self._setup_bayesball_player()
        deck = range(13) * 4

        with self.subTest(msg='Test where all cards have been revealed (average calc plays no part)'):
            deck_up = []
            player1_state = self._generate_player_state(score=sum(range(1, 5)),
                                                        visible=[True]*4,
                                                        raw_cards=range(1,5))
            player2_state = self._generate_player_state(score=sum(range(2, 6)),
                                                        visible=[True]*4,
                                                        raw_cards=range(2,6))

            state = self._generate_game_state(player1_state, [player2_state], deck_up, False)
            diff = self.bayesball_player._calc_score_diff(state, avg=5)
            self.assertEqual(diff, sum(range(2,6)) - sum(range(1,5)))

        with self.subTest(msg='Test where some cards have been revealed'):
            deck_up = []
            player1_cards = [1, None, 3, None]
            player1_state = self._generate_player_state(score=4,
                                                        visible=[True, False]*2,
                                                        raw_cards=player1_cards)
            player2_cards = [2, None, 4, None]
            player2_state = self._generate_player_state(score=6,
                                                        visible=[True, False]*2,
                                                        raw_cards=player2_cards)

            state = self._generate_game_state(player1_state, [player2_state], deck_up, False)
            diff = self.bayesball_player._calc_score_diff(state, avg=5)
            self.assertEqual(diff, (6+10) - (4+10))


    def test_turn_phase_1(self):
        """ Test turn phase 1 under different scenarios to test probability based logic """

        # State helper functions:
        # def _generate_player_state(self, score, visible, raw_cards, num_rows=2, num_cols=2):
        # def _generate_game_state(self, self_player_state, opp_players_state, deck_up, has_knocked)

        # Setup basic bayesball player
        self._setup_bayesball_player()

        self_state = self._generate_player_state(score=3,
                                                 visible=[True,False,True,False],
                                                 raw_cards=[1,None,2,None])

        opp_state = self._generate_player_state(score=20,
                                                visible=[True,True,False,False],
                                                raw_cards=[10,12,None,None])

        with self.subTest(msg='Test when min_distance is met and other player has not knocked'):
            # This player should choose to knock as the min_distance is met

            state = self._generate_game_state(self_player_state=self_state,
                                              opp_players_state=[opp_state],
                                              deck_up=[10],
                                              has_knocked=False)

            action = self.bayesball_player.turn_phase_1(state)
            self.assertEqual(action, 'knock')

        with self.subTest(msg='Test when min_distance is met and other player has knocked'):
            # This player would not choose to knock - the up card is bad,
            # so they should choose the down card

            state = self._generate_game_state(self_player_state=self_state,
                                              opp_players_state=[opp_state],
                                              deck_up=[10],
                                              has_knocked=True)

            action = self.bayesball_player.turn_phase_1(state)
            self.assertEqual(action, 'face_down_card')

        with self.subTest(msg='Test when min_distance is met, opp has knocked and face_up_card is good'):
            # This player should choose the up card, since the other player has already knocked

            state = self._generate_game_state(self_player_state=self_state,
                                              opp_players_state=[opp_state],
                                              deck_up=[1],
                                              has_knocked=True)

            action = self.bayesball_player.turn_phase_1(state)
            self.assertEqual(action, 'face_up_card')










