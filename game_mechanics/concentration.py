from game_mechanics.cards import Card
from random import shuffle


class Concentration:
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
        self.moves = 0

    def shuffle(self):
        """Shuffles the cards so that they are not in a particular sequence"""
        shuffle(self.cards)

    def play(self, a, b):
        """Play the game with two cards."""
        card1 = self.cards[a]
        card2 = self.cards[b]
        if card1.matched:
            raise ValueError('The first card is already matched!')
        if card2.matched:
            raise ValueError('The second card is already matched!')

        self.moves += 1

        if card1.value == card2.value:
            card1.is_matched()
            card2.is_matched()

        return card1, card2, card1.matched
