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
        self.assertEqual(len(sets), 4, msg='Wrong number of sets returned')
        # Assert that each set has size p
        for s in sets:
            self.assertEqual(len(s), p, msg='Wrong number of colors in a set')

    def test_get_connected_components(self):
        # Get the components on set {0, 1, 2}
        cs = {0, 1, 2}
        comps = self.decomp_generator.get_connected_components(cs)
        # Assert that we have one component on this color set
        self.assertEquals(len(comps), 1, msg='Wrong number of components')
        # Assert that it has vertices [0, 1, 2]
        self.assertEquals(comps[0].nodes(), [0, 1, 2], msg='Wrong vertex set')
        # Assert that it has edges [(0, 1), (1, 2)]
        self.assertEquals(comps[0].edges(), [(0, 1), (1, 2)],
                msg='Wrong edge set')

    def tearDown(self):
        """Cleans up after tests are run"""

suite = unittest.TestLoader().loadTestsFromTestCase(TestDecompositionGenerator)

if __name__ == '__main__':
    unittest.main()
