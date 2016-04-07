class Concentration():
    """Concentration class that will establish the gameplay for the game.
    More features will be added as necessary"""

    def __init__(self):
        """Create a game with 20 cards. Will throw an error if an odd number
        of cards is requested."""
        self.cards = 20
        self.gameover = False
        self.rows = 4
        self.cols = 5

