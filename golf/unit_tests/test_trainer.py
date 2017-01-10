''' Tests for Golf training - will include unit and more integration style tests
    as this is the component where much of the logic comes together
'''
import unittest2
from golf.trainer import Trainer
from golf.players.trainable_player_base import TrainablePlayer
from mock import call, patch, Mock


class MockBoard(object):
    ''' Tiny class to mock board responses '''

    def __init__(self, match_num, player_scores=[3,10]):
        self.match_num = match_num
        self.cur_turn = 0
        self.player_scores = player_scores

    def play_game(self):
        scores = [self.player_scores[(self.cur_turn + self.match_num + i) % 2] for i in range(2)]
        self.cur_turn += 1
        return scores


class TestTrainer(unittest2.TestCase):
    ''' test the train module which controls multi-hole and multi-game matches '''


    def _setup_players_and_trainer(self, trainable_index=0, num_players=2, trainer_args={}):
        """ Setup players - with the option to make them trainable """

        self.players = []

        for i in range(num_players):
            player = TrainablePlayer()
            if i == trainable_index:
                player.is_trainable = True

            self.players.append(player)

        self.trainer = Trainer(self.players[0],
                               self.players[1],
                               trainable_player='player{}'.format(trainable_index + 1),
                               **trainer_args)


    def test_creation_params(self):
        """ Test the initialization of params for the trainer class """

        trainable_player_index = 1
        self._setup_players_and_trainer(trainable_index=trainable_player_index,
                                        trainer_args={'checkpoint_epochs': 100})

        for i in range(2):
            self.assertEqual(self.trainer.players[i], self.players[i])

        self.assertEqual(self.trainer.total_holes, 9)
        self.assertEqual(self.trainer.trainable_player, trainable_player_index)
        self.assertEqual(self.trainer.checkpoint_epochs, 100)
        self.assertEqual(len(self.trainer.eval_results), 0)


    @patch('golf.trainer.Board')
    def test_play_first_match(self, board_mock):
        ''' Test playing a single match '''

        num_holes = 9
        player_scores = [3,10]

        self._setup_players_and_trainer(trainable_index=1,
                                        trainer_args={'checkpoint_epochs': 100})

        with self.subTest(msg='Test a single match where player 1 goes first'):
            match_num = 0
            board_mock.return_value = MockBoard(match_num=match_num, player_scores=player_scores)
            scores = self.trainer.play_match(match_num)
            for i in range(2):
                self.assertEqual(scores[i], player_scores[i] * num_holes)

            # We want to make sure that we're alternating calls to board
            calls = [call([self.players[0], self.players[1]],2,verbose=False),
                     call([self.players[1], self.players[0]],2,verbose=False)] * 5
            calls = calls[:len(calls)-1]

            board_mock.assert_has_calls(calls)

        with self.subTest(msg='Test a single match where player 2 goes first'):
            match_num = 1
            board_mock.return_value = MockBoard(match_num=match_num, player_scores=player_scores)
            scores = self.trainer.play_match(match_num)
            for i in range(2):
                self.assertEqual(scores[i], player_scores[i] * num_holes)

            # We want to make sure that we're alternating calls to board
            calls = [call([self.players[1], self.players[0]],2,verbose=False),
                     call([self.players[0], self.players[1]],2,verbose=False)] * 5
            calls = calls[:len(calls)-1]

            board_mock.assert_has_calls(calls)


    def test_train_k_epochs(self):
        """ Test training k epochs - making sure process_checkpoint is called properly """

        self._setup_players_and_trainer(trainable_index=0,
                                        trainer_args={'checkpoint_epochs': 10})

        def return_match_winner(match_num):
            if match_num % 3 == 0:
                # second player wins
                return [50, 10]
            else:
                return [10, 50]

        self.trainer.play_match = return_match_winner
        self.trainer.process_checkpoint = Mock()
        self.trainer.players[0].update_learning_rate = Mock()
        self.trainer.eval_results = [100,20]

        self.trainer.train_k_epochs(100)

        # process checkpoint should be called 10 times during training -
        # and one final time when all k epochs are done
        self.assertEqual(11, self.trainer.process_checkpoint.call_count)

        # Let's make sure the calls were also proper
        calls = [call((i*10) - 1) for i in range(1, 11)]
        calls.append(call(100))
        self.trainer.process_checkpoint.assert_has_calls(calls)

        self.assertEqual(100, self.trainer.players[0].update_learning_rate.call_count)
        lr_calls = [call(i, [100, 20]) for i in range(100)]
        self.trainer.players[0].update_learning_rate.assert_has_calls(lr_calls)


    @patch('golf.trainer.benchmark_player')
    def test_process_checkpoint(self, benchmark_mock):
        """ Test processing checkpoints during training """

        benchmark_mock.return_value = (12,30,)
        self._setup_players_and_trainer(trainable_index=1,
                                        trainer_args={'checkpoint_epochs': 10})

        # We'll need a special class to intercept the @property and introspect calls
        class IsTrainablePlayer(object):

            def __init__(self):
                self._is_trainable = True
                self.calls = []

            @property
            def is_trainable(self):
                return self._is_trainable

            @is_trainable.setter
            def is_trainable(self, value):
                self._is_trainable = value
                self.calls.append(value)

        self.trainer.players[1] = IsTrainablePlayer()
        self.trainer.players[1].save_checkpoint = Mock()

        self.trainer.process_checkpoint(10)

        self.assertEqual(benchmark_mock.call_count, 1)
        self.assertEqual([False, True], self.trainer.players[1].calls)
        self.trainer.players[1].save_checkpoint.assert_called_with(10)
        self.assertEqual(self.trainer.eval_results, [[30, 12,]])
