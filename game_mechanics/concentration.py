from game_mechanics.cards import Card
from random import shuffle

class Concentration():
    """Concentration class that will establish the gameplay for the game.
    More features will be added as necessary"""

    def __init__(self):
        """Create a game with 20 cards. Will throw an error if an odd number
        of cards is requested."""
        self.cards = []
        for x in xrange(2):
            for y in xrange(10):
                self.cards.append(Card(y))

        self.gameover = False
        self.rows = 4
        self.cols = 5

    def shuffle(self):
        """Shuffles the cards so that they are not in a particular sequence"""
        shuffle(self.cards)