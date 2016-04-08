class Card():
    """This is the card class that will hold the cards """

    def __init__(self, value):
        """Initializes a card with the given value and matched property to
        false"""
        self.value = value
        self.matched = False

    def is_matched(self):
        """Sets matched to true."""
        self.matched = True