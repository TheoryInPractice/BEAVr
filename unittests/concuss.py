#
# This file is part of BEAVr, https://github.com/theoryinpractice/beavr/, and is
# Copyright (C) North Carolina State University, 2016. It is licensed under
# the three-clause BSD license; see LICENSE.
#

import unittest

import networkx as nx

from beavr.concuss import visualizerbackend

class TestDecompositionGenerator(unittest.TestCase):

    def setUp(self):
        """ Sets up the necessary objects to run"""
        self.graph = nx.Graph()
        self.graph.add_nodes_from(range(6))
        self.graph.add_edges_from([(0,1), (1,2), (1,3), (2,3), (3,4), (4,5)])
        self.coloring = range(6)

        self.decomp_generator = visualizerbackend.DecompositionGenerator(
                self.graph, self.coloring)

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

        # Get the components on set {0, 1, 5}
        cs = {0, 1, 5}
        comps = self.decomp_generator.get_connected_components(cs)
        # Assert that we have two components on this color set
        self.assertEquals(len(comps), 2, msg='Wrong number of components')
        # Assert that component 0 has vertices [0, 1]
        self.assertEquals(comps[0].nodes(), [0, 1], msg='Wrong vertex set')
        # Assert that it has edges [(0, 1)]
        self.assertEquals(comps[0].edges(), [(0, 1)],
                msg='Wrong edge set')
        # Assert that component 1 has vertices [5]
        self.assertEquals(comps[1].nodes(), [5], msg='Wrong vertex set')
        # Assert that it has no edges
        self.assertEquals(comps[1].edges(), [], msg='Wrong edge set')

    def test_get_tree_layout(self):
        # Get a tree layout of the whole original graph
        layout = self.decomp_generator.get_tree_layout(self.graph)
        # Assert that all the vertices lie within the rectangle [0.05, 0.95]^2
        for point in layout.values():
            self.assertTrue(point[0] >= 0.05,
                    msg='point[0] too small ({0})'.format(point[0]))
            self.assertTrue(point[0] <= 0.95,
                    msg='point[0] too large ({0})'.format(point[0]))
            self.assertTrue(point[1] >= 0.05,
                    msg='point[1] too small ({0})'.format(point[1]))
            self.assertTrue(point[1] <= 0.95,
                    msg='point[1] too large ({0})'.format(point[1]))

    def tearDown(self):
        """Cleans up after tests are run"""


class TestCountGenerator(unittest.TestCase):

    def setUp(self):
        """ Sets up the necessary objects to run"""
        # TODO

        #self.CSG = visualizerbackend.CountGenerator(graph, tdd, k_patterns,\
        #                                            motifs, coloring)

    def test_get_layouts(self):
        pass

    def test_get_attributes(self):
        pass

    def tearDown(self):
        """Cleans up after tests are run"""


class TestCombineSetGenerator(unittest.TestCase):

    def setUp(self):
        """ Sets up the necessary objects to run"""
        color_set = set([0,6])  # Colors used in pattern coloring
        colors = set(range(10))  # All colors in graph
        pat_size = 4  # Number of nodes in pattern
        min_size = 2  # Smallest possible number of colors used by pattern

        self.CSG = visualizerbackend.CombineSetGenerator(color_set, colors,
                                                         pat_size, min_size)

    def test_get_color_sets(self):
        sets = self.CSG.get_color_sets()

        self.assertEquals(len(sets), 3)
        self.assertTrue(len(sets[0])>=len(sets[1])>=len(sets[2]))
        self.assertEquals(sets[0], [[0, 6, 1, 2], [0, 6, 1, 3], [0, 6, 1, 4],
                          [0, 6, 1, 5], [0, 6, 1, 7], [0, 6, 1, 8], [0, 6, 1, 9],
                          [0, 6, 2, 3], [0, 6, 2, 4], [0, 6, 2, 5], [0, 6, 2, 7],
                          [0, 6, 2, 8], [0, 6, 2, 9], [0, 6, 3, 4], [0, 6, 3, 5],
                          [0, 6, 3, 7], [0, 6, 3, 8], [0, 6, 3, 9], [0, 6, 4, 5],
                          [0, 6, 4, 7], [0, 6, 4, 8], [0, 6, 4, 9], [0, 6, 5, 7],
                          [0, 6, 5, 8], [0, 6, 5, 9], [0, 6, 7, 8], [0, 6, 7, 9],
                          [0, 6, 8, 9]])
        self.assertEquals(sets[1], [[0, 6, 1], [0, 6, 2], [0, 6, 3], [0, 6, 4],
                          [0, 6, 5], [0, 6, 7], [0, 6, 8], [0, 6, 9]])
        self.assertEquals(sets[2], [[0,6]])

    def tearDown(self):
        """Cleans up after tests are run"""


suite = unittest.TestLoader().loadTestsFromTestCase(TestDecompositionGenerator)
suite = unittest.TestLoader().loadTestsFromTestCase(TestCombineSetGenerator)

if __name__ == '__main__':
    unittest.main()
