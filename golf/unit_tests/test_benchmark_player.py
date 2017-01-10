''' Tests for Golf benchmark
'''
import unittest2
from golf.benchmark import benchmark_player
from mock import call, patch, Mock

class TestBenchmarkPlayer(unittest2.TestCase):
    ''' test the benchmark_player method which evaluates a set of players '''

    @patch('golf.benchmark.Match')
    def test_benchmark_player(self, mock_match):
        """ Test benchmark player """

        match_instance = Mock()

        mock_match.return_value = match_instance
        match_instance.play_k_matches.return_value = (10, 5)
        result = benchmark_player('player1', 'player2', 20)

        self.assertEqual(result, (10,5,))
        self.assertEqual(mock_match.call_count, 1)
        mock_match.assert_called_with('player1', 'player2')
        match_instance.play_k_matches.assert_called_with(20)
