# Class to represent the playing board for golf
from random import shuffle
from hand import Hand

from hand import Hand

class Board(object):
    # Assemble a board - model game play for a single round

    def __init__(self, players, num_cols):
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
        has_knocked = False
        turn = 0

        while not end_game:
            cur_turn = turn % 2
            options = ('face_up_card', 'face_down_card', 'knock',)
            decision = self.players[cur_turn].turn_phase_1(self.get_state_for_player(cur_turn), options)

            # Increment the turn counter - which also signifies current turn
            turn += 1

            if decision == 'knock':
                # then the player has no turn phase 2
                has_knocked = True
                #print 'knock'
                continue

            if decision == 'face_up_card':
                card = self.deck_up.pop()
                #print 'face up {}'.format(card)
                possible_moves = ('swap',)
            else:
                card = self.deck_down.pop(0)
                #print 'face down {}'.format(card)

                possible_moves = ('swap', 'return_to_deck',)

            decision_two = self.players[cur_turn].turn_phase_2(card,
                                                               self.get_state_for_player(cur_turn),
                                                               possible_moves)

            if decision_two[0] == 'swap':
                card_ret = self.hands[cur_turn % 2].swap(decision_two[1],
                                                         decision_two[2],
                                                         card,
                                                         decision == 'face_up_card')
            else:
                card_ret = card

            self.deck_up.append(card_ret)


            if has_knocked:
                end_game = True

            # Here we need to handle the possibility that the deck goes around an Nth time
            if len(self.deck_down) <= 0:
                cur_up = self.deck_up.pop()
                self.deck_down = list(self.deck_up)
                shuffle(self.deck_down)
                self.deck_up = [cur_up]

            turn += 1

        return [hand.score() for hand in self.hands]

    def get_state_for_player(self, player_id):
        ''' Get game state from a player's perspective '''


        # State would need to describe both players situations
        return {'self': self.hands[player_id].get_state(is_self=True),
                'opp': [self.hands[p].get_state(is_self=False) for p in range(len(self.hands)) if p != player_id],
                'deck_up': self.deck_up}



    def step_turn(self):
        # A simple function to represent moving 1 single turn
        # which could result in several changes in game state

        self.cur_turn += 1 # we increment this and then evaluate the % 2 value
        cur_player = (self.hand1, self.hand2,)[self.cur_turn % 2]

        # At some point we need to select a move for the player - so let's place
        # something here to model that activity
        possible_moves = ('knock', 'swap', 'pickup_top')

        return cur_player.move()
