# golf-reinforcement <a href="https://travis-ci.org/RaymondKlass/golf-reinforcement/"><img src="https://travis-ci.org/RaymondKlass/golf-reinforcement.svg?branch=master"></a>
Golf Card Game as a reinforcement learning problem

## General Description
https://en.wikipedia.org/wiki/Golf_(card_game)#Four-card_golf

## Scoring
Aces: 1 pt
2-10: Worth face value
Jack & Queen: Worth 10 pts
King: Worth 0 pts

A column is when 2 cards in a vertical column are the same value (i.e. both jacks).  The column is scored as 0 pts

## Objective
Lowest score.

## Play
Each player's turn has 2 phases.  During the first, they may draw the face-down card from the deck, draw the face-up card, or knock.  If the player takes the face-up card, they must replace one of their face-down cards with it.  If the player draws the face-down card, they may either replace one of their face-down cards, or they may place the card on top of the face-up stack.  If the player knocks, then they may not do anything else - each of the other players get exactly 1 turn to make any improvements, and then scores are totaled.  

## Matches
```python match.py --player1=random_player.RandomPlayer --player2=random_player.RandomPlayer -m 10```

## Training
```python match.py --player1=q_watkins_player.QWatkinsPlayer --player2=bayesball_player.BayesballPlayer -e 100 --checkpoint_epochs=10 --player1_args='{"train":{ "checkpoint_dir": "Some/Directory"}, "init": {}} --trainable=player1```