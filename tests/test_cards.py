from unittest import TestCase
from game_mechanics.cards import Card

class TestCards(TestCase):
    """Test the card class."""

    def setUp(self):
        self.card = Card(1)

    def tearDown(self):
        self.card = None

    def test_has_a_value(self):
        TestCase.assertTrue(self, self.card.value is not None)