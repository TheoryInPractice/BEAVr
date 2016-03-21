import math

from numpy import random
import networkx as nx

class DecompositionGenerator(object):
    def __init__(self, graph, coloring):
        self.graph = graph
        self.coloring = coloring

    def get_connected_components(self, color_set):
        """
        A generator for connected components given a specific color set

        :param color_set: The color set
        :return: A generator for connected components (subgraphs) induced by
                 color_set
        """

        # Make an empty set to store vertices
        vertices = set()

        # Find vertices that are colored with colors in color_set
        for index, color in enumerate(self.coloring):
            if color in color_set:
                vertices.add(index)

        return list(nx.connected_component_subgraphs( self.graph.subgraph(vertices) ))

    def get_tree_layouts( self, connected_components, coloring ):
        layouts = []
        for connected_component in connected_components:
            layouts.append( self.get_tree_layout(connected_component) )

        # Calculate offset
        y_offset = 0
        x_offset = 0
        grid_len = int(math.ceil(math.sqrt(len(layouts))))
        # TODO: Find a good value for this
        for layout in layouts:
            grid_size = 10
            for index in layout:
                layout[index] = [layout[index][0] + x_offset, layout[index][1] + y_offset]
            x_offset += grid_size
            if x_offset > grid_len*grid_size:
                x_offset = 0
                y_offset += grid_size

        return layouts

    def get_tree_layout( self, connected_component ):
        layout = None
        tree = self.get_underlying_tree( connected_component )
        try:
            # Nice circular layout if you have graphviz
            from networkx.drawing.nx_agraph import graphviz_layout
            layout = graphviz_layout(tree,prog='twopi',root=str(tree.root),args='-Gsize="2,2"')
        except ImportError:
            # Spring layout if you do not have grahpviz
            layout = nx.spring_layout(tree)
        return layout

    def get_underlying_tree( self, connected_component ):
        # Find the root (color with only one occurrence)
        root = None
        colors = [self.coloring[node] for node in connected_component.nodes()]
        for index, color in enumerate(colors):
            colors[index] = 'Not a color'
            if color not in colors:
                root = connected_component.nodes()[index]
                break
            colors[index] = color

        # If we can't find a root, something's wrong!
        if root == None:
            print 'WARNING: Coloring this has no root', colors
            return connected_component

        # Create a new NetworkX graph to represent the tree
        tree = nx.Graph()
        tree.add_node( root )

        # Remove the root from the connected component
        connected_component = nx.Graph(connected_component)
        connected_component.remove_node( root )

        # Every new connected component is a subtree
        for sub_cc in nx.connected_component_subgraphs( connected_component ):
            subtree = self.get_underlying_tree(sub_cc)
            tree = nx.compose( tree, subtree )
            tree.add_edge( root, subtree.root )

        # Root field for use in recursive case to connect tree and subtree
        tree.root = root
        return tree
    
    def four_color_sets(self, C, p):
        # We want at least a few extra colors
        assert p <= len(C) - 3, 'p too large for C'
        # Randomly permute C
        Cs = random.permutation(sorted(C)).tolist()
        # Make an empty set for our output
        sets = []
        # If we have a lot of colors, do something nice
        if 2 * p + 1 <= len(C):
            # First $p$ colors
            sets.append(frozenset(Cs[:p]))
            # Next $p$ colors
            sets.append(frozenset(Cs[p:2*p]))
            # Overlap those two sets
            sets.append(frozenset(Cs[p//2:3*p//2]))
            # First $p-1$ colors, and one unique color
            sets.append(frozenset(Cs[:p-1] + [Cs[2*p]]))
        # If we don't have a lot of colors, do a cramped version of the same thing
        else:
            # First $p$ colors
            sets.append(frozenset(Cs[:p]))
            # Last $p$ colors
            sets.append(frozenset(Cs[-p:]))
            # Overlap those two sets
            sets.append(frozenset(Cs[(len(C)-p)//2:(p-len(C))//2]))
            # First $p-1$ colors, and last color
            sets.append(frozenset(Cs[:p-1] + [Cs[-1]]))

        return sets
