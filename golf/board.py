# Class to represent the playing board for golf
from random import shuffle
from hand import Hand

from hand import Hand

class Board(object):
    # Assemble a board - model game play for a single round

    def __init__(self, players, num_cols, verbose=False):
        ''' Args:
                players: set of players
                num_cols: game board layout
        '''

        self.players = players
        self.num_cols = num_cols

        # A little cheat here - we're modeling a deck as 0 -> 12
        # In this scenario, a King = 0, Ace = 1, and
        self.deck_down = (range(13) * 4)
        shuffle(self.deck_down)
        self.deck_up = []
        self.hands = []
        self.verbose = verbose
        self.has_knocked = False


    @property
    def deck_visible(self):
        return self.deck_up


    def _deal_hands(self):
        # Deal the hands to the players - respecting the player - dealing rotation

        dealt = self.deck_down[:self.num_cols*4]
        self.deck_down = self.deck_down[self.num_cols * 4:]
        self.hands.append(Hand([dealt[i] for i in range(len(dealt)) if i % 2 == 0]))
        self.hands.append(Hand([dealt[i] for i in range(len(dealt)) if i % 2 != 0]))


    def play_game(self):
        ''' Initially the top face down card becomes the face up card, then thing proceed '''

        deck_up = self.deck_down.pop(0)
        self.deck_up.append(deck_up)
        self._deal_hands()
        end_game = False
        self.has_knocked = False
        turn = 0

        if self.verbose:
            print '\n Starting hole \n'

        while not end_game:
            # Check to see if the other player already knocked
            if self.has_knocked:
                # this makes sure that this is the last turn
                end_game = True

            cur_turn = turn % 2

            if self.verbose:
                print '\n{} {} turn phase 1'.format(self.players[cur_turn], cur_turn)

            options = ('face_up_card', 'face_down_card', 'knock',)

            if self.verbose:
                state = self.get_state_for_player(cur_turn)
                print 'Self: {}'.format(state['self'])
                print 'Opp: {}'.format(state['opp'])
                print 'Face Up Card: {}'.format(state['deck_up'][-1])

            decision = self.players[cur_turn].turn_phase_1(self.get_state_for_player(cur_turn), options)

            if self.verbose:
                print 'Decision phase 1: {} \n'.format(decision)

            # Increment the turn counter - which also signifies current turn
            turn += 1

            if decision == 'knock':
                # then the player has no turn phase 2
                self.has_knocked = True
                if hasattr(self.players[cur_turn], 'is_trainable') and self.players[cur_turn].is_trainable:
                    self.players[cur_turn].update_weights(self.get_state_for_player(cur_turn), card=None, reward=0, possible_moves=['knock'])

                continue

            if decision == 'face_up_card':
                card = self.deck_up.pop()
                #print 'face up {}'.format(card)
                possible_moves = ('swap',)
            else:
                card = self.deck_down.pop(0)
                #print 'face down {}'.format(card)

                possible_moves = ('swap', 'return_to_deck',)

            if self.verbose:
                print '\n{} {} turn phase 2'.format(self.players[cur_turn], cur_turn)
                state = self.get_state_for_player(cur_turn)
                print 'Card-in-hand: {}'.format(card)

            # For trainable players - we need to update the new state - which
            # is dependent on the old state
            new_state = self.get_state_for_player(cur_turn)

            # This is where we need to update the weights if the player with the current turn is "trainable"
            if hasattr(self.players[cur_turn], 'is_trainable') and self.players[cur_turn].is_trainable:
                self.players[cur_turn].update_weights(new_state, card, reward=0, possible_moves=possible_moves)

            decision_two = self.players[cur_turn].turn_phase_2(card,
                                                               new_state,
                                                               possible_moves)

            if self.verbose:
                print 'Decision phase 2: {}'.format(decision_two)

            if decision_two[0] == 'swap':
                card_ret = self.hands[cur_turn % 2].swap(decision_two[1],
                                                         decision_two[2],
                                                         card,
                                                         decision == 'face_up_card')
            else:
                card_ret = card

            self.deck_up.append(card_ret)

            if self.verbose:
                state = self.get_state_for_player(cur_turn)
                print 'End State - Self: {}'.format(state['self'])


            # Here we need to handle the possibility that the deck goes around an Nth time
            if len(self.deck_down) <= 0:
                cur_up = self.deck_up.pop()
                self.deck_down = list(self.deck_up)
                shuffle(self.deck_down)
                self.deck_up = [cur_up]

            # Here we're just going to update the current players score - a final update will happen at the end of the
            # game as a sort of 'exit' move
            if hasattr(self.players[cur_turn], 'is_trainable') and self.players[cur_turn].is_trainable:
                self.players[cur_turn].update_weights(self.get_state_for_player(cur_turn), card=None, reward=0, possible_moves=['knock'])


        # Since the game is over, we will need to make a final weight update to any trainable players with their proper reward
        for i, player in enumerate(self.players):
            if hasattr(player, 'is_trainable') and player.is_trainable:
                if self.verbose:
                    print 'Final Update of weights for player {}'.format(i)

                reward = self.hands[i % 2].score() - float(self.hands[(i+1) % 2].score())
                new_state = self.get_state_for_player(i%2)
                player.update_weights(new_state, card=None, reward=reward, possible_moves=['knock'])


        if self.verbose:
            for i, hand in enumerate(self.hands):
                print '{}: {} Hand {}'.format(self.players[i], i, hand.cards)

        return [hand.score() for hand in self.hands]

    def get_state_for_player(self, player_id):
        ''' Get game state from a player's perspective '''


        # State would need to describe both players situations
        return {'self': self.hands[player_id].get_state(is_self=True),
                'opp': [self.hands[p].get_state(is_self=False) for p in range(len(self.hands)) if p != player_id],
                'deck_up': self.deck_up,
                'has_knocked': self.has_knocked}
