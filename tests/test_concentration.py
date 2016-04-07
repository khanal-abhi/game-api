from unittest import TestCase
from game_mechanics.concentration import Concentration


class ConcentrationTest(TestCase):
    """Will test the class Concentration."""

    def setUp(self):
        self.game = Concentration()

    def test_concentrate_should_instantiate_with_20_cards(self):
        TestCase.assertEqual(self, 20, self.game.cards)

    def test_gameover_false_by_default(self):
        TestCase.assertFalse(self, self.game.gameover,
                             'Game over is not false by default!')

    def test_number_of_rows_is_4(self):
        TestCase.assertEqual(self, 4, self.game.rows)

    def test_number_of_cols_is_5(self):
        TestCase.assertEqual(self, 5, self.game.cols)

    def test_start_game_should_have_4_rows_and_5_colums_in_pairs(self):
        pass

