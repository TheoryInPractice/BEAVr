import unittest

import networkx as nx

from drgraph.concuss import visualizerbackend

class TestDecompositionGenerator(unittest.TestCase):

    def setUp(self):
        """ Sets up the necessary objects to run"""
        self.graph = nx.Graph()
        self.graph.add_nodes_from(range(6))
        self.graph.add_edges_from([(0,1), (1,2), (1,3), (2,3), (3,4), (4,5)])
        self.coloring = range(6)

        self.decomp_generator = visualizerbackend.DecompositionGenerator(
                self.graph, self.coloring)

    def test_four_color_sets(self):
        p = 3
        # Make four color sets of size p
        sets = self.decomp_generator.four_color_sets(set(self.coloring), p)
        # Assert that we got four sets
        self.assertEquals(len(sets), 4)
        # Assert that each set has size p
        for s in sets:
            self.assertEquals(len(s), p)

    def tearDown(self):
        """Cleans up after tests are run"""

suite = unittest.TestLoader().loadTestsFromTestCase(TestDecompositionGenerator)

if __name__ == '__main__':
    unittest.main()
