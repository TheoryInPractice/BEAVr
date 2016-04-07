import math
from itertools import combinations

from numpy import random
import networkx as nx

class DecompositionGenerator(object):
    layout_margin = 0.05

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
        v_set = set()

        # Find vertices that are colored with colors in color_set
        for index, color in enumerate(self.coloring):
            if color in color_set:
                v_set.add(index)

        cc_list = []
        for new_cc in nx.connected_component_subgraphs(self.graph.subgraph(v_set)):
            found = False
            for n in new_cc.node:
                new_cc.node[n]['color'] = self.coloring[n]
            for i, cc in enumerate(cc_list):
                if nx.is_isomorphic(new_cc, cc, node_match=self.nm):
                    cc_list[i].occ += 1
                    found = True
                    break
            if not found:
                new_cc.occ = 1
                cc_list.append(new_cc)
        return cc_list

    def nm(self, n1, n2):
        return n1['color'] == n2['color']

    def get_tree_layouts(self, connected_components, coloring):
        layouts = []
        for connected_component in connected_components:
            layouts.append(self.get_tree_layout(connected_component))
        # Calculate offset
        y_offset = 0
        x_offset = 0
        grid_len = int(math.ceil(math.sqrt(len(layouts))))
        # TODO: Find a good value for this
        for layout in layouts:
            grid_size = 1.5
            for index in layout:
                layout[index] = [layout[index][0] + x_offset, layout[index][1] + y_offset]
            x_offset += grid_size
            if x_offset >= grid_len*grid_size:
                x_offset = 0
                y_offset += grid_size

        return layouts

    def get_tree_layout(self, connected_component):
        layout = None
        tree = self.get_underlying_tree(connected_component)
        try:
            # Nice circular layout if you have graphviz
            from networkx.drawing.nx_agraph import graphviz_layout
            layout = graphviz_layout(tree, prog='twopi', root=str(tree.root))

            # Scale to fit grid, since twopi seems to ignore the size option
            min_x = min(pos[0] for pos in layout.values())
            max_x = max(pos[0] for pos in layout.values())
            min_y = min(pos[1] for pos in layout.values())
            max_y = max(pos[1] for pos in layout.values())

            center_x = min_x + (max_x - min_x) / 2
            center_y = min_y + (max_y - min_y) / 2
            # Re-center, scale and shift to fit the desired bounding box
            try:
                x_scale = (0.5 - self.layout_margin - 0.005) / (center_x - min_x)
            except ZeroDivisionError:
                x_scale = 1
            try:
                y_scale = (0.5 - self.layout_margin - 0.005) / (center_y - min_y)
            except ZeroDivisionError:
                y_scale = 1
            for vert, pos in layout.iteritems():
                layout[vert] = ((pos[0] - center_x) * x_scale + 0.5,
                        (pos[1] - center_y) * y_scale + 0.5)

        except ImportError:
            # Spring layout if you do not have grahpviz
            layout = nx.spring_layout(tree, scale=1-2*self.layout_margin-0.01,
                    center=(0.5, 0.5))
        return layout

    def get_underlying_tree(self, connected_component):
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
        tree.add_node(root)

        # Remove the root from the connected component
        connected_component = nx.Graph(connected_component)
        connected_component.remove_node(root)

        # Every new connected component is a subtree
        for sub_cc in nx.connected_component_subgraphs(connected_component):
            subtree = self.get_underlying_tree(sub_cc)
            tree = nx.compose(tree, subtree)
            tree.add_edge(root, subtree.root)

        # Root field for use in recursive case to connect tree and subtree
        tree.root = root
        return tree


class CombineSetGenerator(object):
    def __init__(self, color_set, colors, pattern_size, min_size):
        self.color_set = color_set
        self.colors = colors
        self.pattern_size = pattern_size
        self.min_size = min_size

    def get_color_sets(self):
        unused = self.colors - self.color_set
        start = max(self.min_size-len(self.color_set), 0)
        color_list = sorted(list(self.color_set))
        sets = []
        for size in range(start, self.pattern_size+1-len(self.color_set)):
            sets.append([color_list+list(s) for s in combinations(unused, size)])
        sets.reverse()
        return sets
