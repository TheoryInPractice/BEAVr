import unittest
from drgraph import util

class TestUtil(unittest.TestCase):

    def setUp(self):
        """ Sets up the necessary data structures and variables before tests are run """

    def tearDown(self):
        """ Cleans up after tests are run """

    def test_load_palette(self):
        """ Tests load_palette """
        expected_first = [0.89411764,0.10196078,0.10980392]
        expected_last = [0.8,0.8,0.8]
        expected_length = 74

        color_palette = util.load_palette("brewer")
        
        actual_length = len(color_palette)
        actual_first = color_palette[0]
        actual_last = color_palette[-1]

        self.assertEqual(expected_length, actual_length,
                         msg="Number of colors in palette")

        self.assertEqual(3, len(color_palette[0]), 
                         msg="Ensuring colors have 3 values for RGB format")

        for exp, act in zip(expected_first, actual_first):
            diff = abs(exp - act)
            self.assertTrue(diff < 0.0001, msg="First color in palette" +\
                            "\n  Expected: " + str(expected_first) + \
                            "\n  Actual:   " + str(actual_first))

        for exp, act in zip(expected_last, actual_last):
            diff = abs(exp - act)
            self.assertTrue(diff < 0.0001, msg="First color in palette" +\
                            "\n  Expected: " + str(expected_last) + \
                            "\n  Actual:   " + str(actual_last))

    def test_map_colorings(self):
        """ Tests map_colorings"""
        colorings = [[7, 3, 6, 2, 0], [1, 3, 7, 5]]
        color_palette = [(a,b,c) for a in [0,1] for b in [0,1] for c in [0,1]]
        expected_mapped = [[(1,1,1), (0,1,1), (1,1,0), (0,1,0), (0,0,0)],
                           [(0,0,1), (0,1,1), (1,1,1), (1,0,1)]]
        
        actual_mapped = util.map_colorings(color_palette, colorings)

        for exp_map_col, act_map_col in zip(expected_mapped, actual_mapped):
            for exp, act in zip(exp_map_col, act_map_col):
                self.assertEqual(exp, act, msg="Mapped colorings" +\
                                "\n  Expected: " + str(exp_map_col) + \
                                "\n  Actual:   " + str(act_map_col))

    def test_map_coloring(self):
        """ Tests map_coloring"""
        coloring = [7, 3, 6, 2, 0]
        color_palette = [(a,b,c) for a in [0,1] for b in [0,1] for c in [0,1]]
        expected_mapped = [(1,1,1), (0,1,1), (1,1,0), (0,1,0), (0,0,0)]
        
        actual_mapped = util.map_coloring(color_palette, coloring)

        for exp, act in zip(expected_mapped, actual_mapped):
            self.assertEqual(exp, act, msg="Mapped coloring" +\
                            "\n  Expected: " + str(expected_mapped) + \
                            "\n  Actual:   " + str(actual_mapped))

suite = unittest.TestLoader().loadTestsFromTestCase(TestUtil)

if __name__ == '__main__':
    unittest.main()
