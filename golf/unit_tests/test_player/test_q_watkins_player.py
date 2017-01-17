''' Q Watkins player - makes decisions based on q-learning
'''
import numpy as np
from golf.unit_tests.test_player.player_test_base import PlayerTestBase
from golf.players.q_watkins_player import QWatkinsPlayer

class TestQWatkinsPlayer(PlayerTestBase):
    ''' Test the policies for the Q Watkins player '''

    def setUp(self):
        self.q_watkins = QWatkinsPlayer()


    def test_player_name(self):
        ''' Basic test for setup '''

        self.assertEqual(str(self.q_watkins).lower(), 'Q Watkins Player'.lower())


    def test_setup_trainer(self):
        # test setting up a basic trainer

        # def setup_trainer(self, checkpoint_dir, learning_rate=0.00001, epsilon=0.2, discount=0.7, *args, **kwargs):
        self.assertEqual(self.q_watkins.is_trainable, False)

        self.q_watkins.setup_trainer(checkpoint_dir='my_checkpoint_dir',
                                     learning_rate=0.001,
                                     epsilon=0.25,
                                     discount=0.8)

        self.assertEqual(self.q_watkins.is_trainable, True)
        self.assertEqual(self.q_watkins.checkpoint_dir, 'my_checkpoint_dir')
        self.assertEqual(self.q_watkins.learning_rate, 0.001)
        self.assertEqual(self.q_watkins.epsilon, 0.25)
        self.assertEqual(self.q_watkins.discount, 0.8)
