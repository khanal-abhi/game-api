from unittest import TestCase
from game_mechanics.cards import Card


class TestCards(TestCase):
    """Test the card class."""

    def setUp(self):
        self.card = Card(1)

    def tearDown(self):
        self.card = None

    def test_has_a_value(self):
        TestCase.assertEqual(self, 1, self.card.value)

    def test_has_a_matched_boolean(self):
        TestCase.assertTrue(self, self.card.matched is not None)

    def test_has_matched_as_false_by_default(self):
        TestCase.assertFalse(self, self.card.matched)