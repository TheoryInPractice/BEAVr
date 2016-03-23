import unittest
from drgraph.concuss import visualizerbackend

class TestDecompositionGenerator(unittest.TestCase):

    def setUp(self):
        """ Sets up the necessary data structures and variables before tests are run """
        graph = nx.Graph()
        graph.add_nodes_from(range(6))
        graph.add_edges_from([(0,1), (1,2), (1,3), (2,3), (3,4), (4,5)])
        coloring = range(6)

        decomp_generator(graph, coloring)

    def tearDown(self):
        """ Cleans up after tests are run """

suite = unittest.TestLoader().loadTestsFromTestCase(TestDecompositionGenerator)

if __name__ == '__main__':
    unittest.main()
