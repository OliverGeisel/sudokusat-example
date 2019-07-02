from unittest import TestCase

import my_solver.oliver.encoder.Encoder  as enc
from my_solver.oliver.encoder.Position import Position


class TestEncoder(TestCase):
    def test_convert_pos_into_var(self):
        pos_111 = Position(1, 1, 1)
        pos_999 = Position(9, 9, 9)
        self.assertEqual("1", enc.convert_pos_into_var(pos_111, 9))
        self.assertEqual("729", enc.convert_pos_into_var(pos_999, 9))

        self.assertEqual(str(4 * 9 ** 2 + 3 * 9 + 8), enc.convert_pos_into_var(Position(5, 4, 8), 9))

    def test_convert_var_into_pos(self):
        pos = Position(5, 4, 8)

        self.assertEqual("548", enc.convert_var_into_pos(449, 9).to_string())
        self.assertEqual("111", enc.convert_var_into_pos(1, 9).to_string())
        print(pos.to_string())
