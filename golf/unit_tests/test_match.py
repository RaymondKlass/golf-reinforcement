''' Tests for Golf matches - will include unit and more integration style tests
    as this is the component where much of the logic comes together
'''
import unittest2
from golf.match import Match
from mock import patch, Mock


class MockBoard(object):
    ''' Tiny class to mock board responses '''

    def __init__(self, match_num, player_scores=[3,10]):
        self.match_num = match_num
        self.cur_turn = 0
        self.player_scores = player_scores

    def play_game(self):
        scores = [self.player_scores[(self.cur_turn + self.match_num + i) % 2] for i in range(2)]
        print 'Scores: {}'.format(scores)
        self.cur_turn += 1
        return scores


class TestMatch(unittest2.TestCase):
    ''' test the match module which controls multi-hole and multi-game matches '''


    def setUp(self):
        ''' Setup some basic players '''

        self.players = {'player{}'.format(a): 'player_{}'.format(a) for a in range(1,3)}



    def test_creation_params(self):
        ''' Test creating a class and confirming the init params '''

        players = ['player_{}'.format(a) for a in range(2)]
        m = Match( holes=8, verbose=False, **self.players)
        self.assertEqual(m.players[0], self.players['player1'])
        self.assertEqual(m.players[1], self.players['player2'])
        self.assertEqual(m.total_holes, 8)
        self.assertEqual(m.verbose, False)


    @patch('golf.match.Board')
    def test_play_first_match(self, board_mock):
        ''' Test playing a single match where player 1 goes first'''

        match_num = 0
        num_holes = 9
        player_scores = [3,10]
        match = Match(holes=num_holes, verbose=False, **self.players)

        board_mock.return_value = MockBoard(match_num=match_num, player_scores=player_scores)
        match.play_match(match_num)
        for i in range(2):
            self.assertEqual(match.scores[i], player_scores[i] * num_holes)


    @patch('golf.match.Board')
    def test_play_second_match(self, board_mock):
        ''' Test playing a single match where player 2 goes first'''

        match_num = 1
        num_holes = 9
        player_scores = [3,10]
        match = Match(holes=num_holes, verbose=False, **self.players)

        board_mock.return_value = MockBoard(match_num=match_num, player_scores=player_scores)
        match.play_match(match_num)
        for i in range(2):
            self.assertEqual(match.scores[i], player_scores[i] * num_holes)
