import unittest

from lark import UnexpectedToken, UnexpectedCharacters

from wuerfelbecher import parser, statistics
from wuerfelbecher.parser import ACTION_SUM, ACTION_ADD, ACTION_SELECT


class TestParser(unittest.TestCase):
    def setUp(self):
        statistics.init_statcounter()

    def test_parse_roll(self):
        self.assertEqual(parser.SetToRoll(1, 6, None, None, []), parser.parse_roll("d6"))
        self.assertEqual(parser.SetToRoll(1, 6, None, None, []), parser.parse_roll("1d6"))
        self.assertEqual(parser.SetToRoll(1, 6, None, None, []), parser.parse_roll("d6"))
        self.assertEqual(parser.SetToRoll(1, 6, None, None, []), parser.parse_roll("1d6"))
        self.assertEqual(parser.SetToRoll(2, 6, None, None, []), parser.parse_roll("2d6"))

        self.assertEqual(parser.SetToRoll(3, 20, None, None, []), parser.parse_roll("3d20"))

        self.assertEqual(parser.SetToRoll(3, 20, None, None, []), parser.parse_roll("3d20"))
        self.assertEqual(parser.SetToRoll(3, 20, 2, None, [ACTION_SELECT]), parser.parse_roll("3d20(2)"))
        self.assertEqual(parser.SetToRoll(3, 20, 3, None, [ACTION_SELECT]), parser.parse_roll("3d20(4)"))
        self.assertEqual(parser.SetToRoll(3, 20, 3, None, [ACTION_SELECT, ACTION_SUM]), parser.parse_roll("3d20(3)+"))

        self.assertEqual(parser.SetToRoll(1, 6, None, 2, [ACTION_SUM, ACTION_ADD]), parser.parse_roll("d6+2"))
        self.assertEqual(parser.SetToRoll(2, 6, None, -4, [ACTION_SUM, ACTION_ADD]), parser.parse_roll("2d6-4"))

        self.assertEqual(parser.SetToRoll(2, 6, None, None, [ACTION_SUM]), parser.parse_roll("2d6+"))
        self.assertEqual(parser.SetToRoll(2, 6, None, 0, [ACTION_SUM, ACTION_ADD]), parser.parse_roll("2d6+0"))


        with self.assertRaises(UnexpectedCharacters):
            parser.parse_roll("foo")
        with self.assertRaises(UnexpectedCharacters):
            parser.parse_roll("d6+4!")
        with self.assertRaises(UnexpectedToken):
            parser.parse_roll("4+d6+4")

    def test_parse_stats(self):
        self.assertEqual(parser.parse_stats("d6"), 6)
        self.assertEqual(parser.parse_stats(" d6 "), 6)

if __name__ == "__main__":
    unittest.main()
