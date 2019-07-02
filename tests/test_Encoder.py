from unittest import TestCase

import my_solver.oliver.encoder.Encoder  as enc
from my_solver.oliver.encoder.Position import Position


class TestEncoder(TestCase):
    def test_convert_pos_into_var(self):
        self.assertEqual(str(5 * 9 ** 2 + 4 * 9 + 8), enc.convert_pos_into_var(Position(5, 4, 8), 9))
        print(str(5 * 9 ** 2 + 4 * 9 + 8))

    def test_convert_var_into_pos(self):
        pos = Position(5, 4, 8)
        self.assertEqual(str(548), enc.convert_var_into_pos(449, 9).to_string())
        print(pos.to_string())
