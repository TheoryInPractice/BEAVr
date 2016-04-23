import math
import random
from itertools import combinations

import networkx as nx
from networkx.algorithms import isomorphism
from numpy import random

from drgraph.util import load_palette, map_coloring, map_colorings

class DecompositionGenerator(object):
    layout_margin = 0.15

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
            grid_size = 1
            for index in layout:
                layout[index] = [layout[index][0] + x_offset, layout[index][1] + y_offset]
            x_offset += grid_size
            if x_offset >= grid_len*grid_size:
                x_offset = 0
                y_offset -= grid_size

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


class CountGenerator(object):
    layout_margin = 0.15
    k_pat_count = 3
    subgraph_count = 4

    def __init__(self, graph, pattern, tdd, dptable, coloring, palette_name):
        self.graph = graph
        self.pattern = pattern
        self.tdd = tdd
        self.dptable = dptable
        self.coloring = coloring

        self.palette = load_palette(palette_name)
        self.mapped_coloring = map_coloring(self.palette, self.coloring)

        self.isomorphism_list = None
        self.vertices_list = []

        self.get_patterns()

    def get_patterns(self):
        """Get some k-patterns and complete motifs"""
        self.k_patterns = []
        self.motifs = []

        while len(self.k_patterns) < self.k_pat_count:
            # Get a random set of vertices from the DP table
            vertices = random.choice(self.dptable.keys())
            # Get the root path
            root_path = self.get_root_path(vertices[0])

            # Get a k-pattern from that part of the DP table
            k_pat = self.get_pattern(vertices, root_path)
            # If we didn't get a k-pattern, try again with another vertex set
            if k_pat is None:
                continue
            # Now that we know the vertex set is okay, remember it
            self.vertices_list.append(vertices)
            # Get the vertices on its boundary
            k_pat_boundary_vertices = [root_path[v] for v in k_pat[2].itervalues()]
            # Select those for display
            self.k_patterns.append(k_pat_boundary_vertices)

            motifs = self.get_motifs_for_k_pattern(k_pat, vertices, root_path)
            self.motifs.append(motifs)

    def get_pattern(self, vertices, root_path):
        """Return an interesting k-pattern from the given part of the table"""
        good_pattern = False

        # Copy the part of the table we're interested in
        subtable = list(self.dptable[vertices])
        # Shuffle it to avoid being boring
        random.shuffle(subtable)

        # While we don't have a good pattern
        for k_pat in subtable:
            good_pattern = True
            pi = k_pat[2]
            # If pi is empty
            if len(pi) == 0:
                good_pattern = False
            # Check if we don't have something
            for mapping in pi.itervalues():
                if mapping >= len(root_path):
                    good_pattern = False
                    break
            if good_pattern:
                # Return the good k-pattern
                return k_pat
        # At this point we've looked at every k-pattern and they all looked
        # dreadfully boring, so return None
        return None

    def get_motifs_for_k_pattern(self, k_pat, vertices, root_path):
        """Return a list of subgraphs isomorphic to the motif"""
        motifs = []
        sv = self.get_subforest_vertices(vertices)

        if self.isomorphism_list is None:
            gm = isomorphism.GraphMatcher(self.graph, self.pattern)
            self.isomorphism_list = list(gm.subgraph_isomorphisms_iter())

        for im in self.isomorphism_list:
            matches_k_pat = True
            # Reverse the mapping
            imr = {v: k for k, v in im.iteritems()}
            for v in k_pat[1]:
                # Check that boundary vertices are mapped right
                if v in k_pat[2]:
                    if imr[v] != root_path[k_pat[2][v]]:
                        matches_k_pat = False
                        break
                # Check that non-boundary vertices in the k-pattern are in the
                # right part of the graph
                elif imr[v] not in sv:
                    matches_k_pat = False
                    break
            # Check that im matches the k-pattern
            if matches_k_pat:
                # Append a subgraph
                motifs.append(nx.relabel_nodes(self.pattern, imr))
            # Don't add too many
            if len(motifs) >= self.subgraph_count:
                break

        return motifs

    def get_root_path(self, vertex, top_level=True):
        """Return the root path for the given vertex"""
        parent = self.tdd.successors(vertex)
        if len(parent) == 0:
            return [vertex]

        root_path = self.get_root_path(parent[0], top_level=False)
        if not top_level:
            root_path.append(vertex)
        return root_path

    def get_subforest_vertices(self, vertices):
        """Get the vertices from the union of subtrees rooted at vertices"""
        # Copy the given vertices
        subforest = list(vertices)

        for v in vertices:
            pred = self.tdd.predecessors(v)
            if pred:
                subforest.extend(self.get_subforest_vertices(pred))

        return subforest

    def get_layouts(self):
        k_pattern_layouts = []
        for k_pattern, motifs in zip(self.k_patterns, self.motifs):
            motif_layouts = []
            motif_layouts.append(self.get_layout(self.graph))
            for motif in motifs:
                motif_layouts.append(self.get_layout(self.graph))
            k_pattern_layouts.append(motif_layouts)
                
        # Calculate offset
        y_offset = 0
        x_offset = 0
        for layouts in k_pattern_layouts:
            for layout in layouts:
                grid_size = 1
                for index in layout:
                    layout[index] = [layout[index][0] + x_offset, layout[index][1] + y_offset]
                y_offset -= grid_size
            x_offset += grid_size
            y_offset = 0

        return k_pattern_layouts 

    def get_layout(self, graph):
        layout = None
        tree = self.tdd
        root = self.get_tdd_root()
        try:
            # Nice circular layout if you have graphviz
            from networkx.drawing.nx_agraph import graphviz_layout
            layout = graphviz_layout(tree, prog='twopi',
                    args='-Groot={0}'.format(root))

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

    def get_attributes(self):
        """
        Gets the graph attributes to use for display
        Each column gets an associated list of graph attributes in the
            following form: [ {attributes for the k-pattern graph}, 
                                attribute dictionaries for the motifs instances]
        The returned attributes variable is a list containing the column lists
        """

        attributes = []

        # Default attribute values
        default_size = 300
        edge_width = 1.0
        line_width = 1.0

        layouts = self.get_layouts()

        for k_pattern, motifs, vertices, layout_list in zip(self.k_patterns,
                self.motifs, self.vertices_list, layouts):
            attribute_list = [] # List of attribute dictionaries for a k-pattern column

            # Color vertices in the header
            vertex_colors = []
            line_widths = []
            subforest = self.get_subforest_vertices(vertices)
            for node in self.graph.nodes():
                # Anonymous vertices are white with a normal outline
                if node in subforest:
                    line_widths.append(1)
                    vertex_colors.append([1, 1, 1])
                # Boundary vertices are black with a normal outline
                elif node in k_pattern:
                    line_widths.append(1)
                    vertex_colors.append([0, 0, 0])
                # Other vertices are gray with a thin outline
                else:
                    line_widths.append(0.5)
                    vertex_colors.append([0.8, 0.8, 0.8])

            k_pattern_attributes = {
                "node_color": vertex_colors,
                "width": edge_width,
                "linewidths": line_widths,
                "with_labels": False,
                "pos": layout_list[0]
            }
            attribute_list.append(k_pattern_attributes)

            for motif, layout in zip(motifs, layout_list[1:]):
                # Make the non-motif nodes small, and the boundary nodes big
                node_sizes = []
                for node in self.graph.nodes():
                    if node in k_pattern:
                        node_sizes.append(default_size * 2)
                    elif node in motif.nodes():
                        node_sizes.append(default_size)
                    else:
                        node_sizes.append(default_size * 0.5)

                # Widen outlines of motif nodes
                line_widths = [line_width * 3 if n in motif.nodes() else line_width for n in self.graph.nodes()]

                # Color the nodes
                comp_colors = [self.mapped_coloring[node] for node in self.graph.nodes()]

                # Widen the motif edges
                edge_widths = []
                motif_edges = motif.edges()
                for edge in self.graph.edges():
                    if edge in motif_edges or tuple(reversed(edge)) in motif_edges:
                        edge_widths.append(edge_width * 3)
                    else:
                        edge_widths.append(edge_width)

                # Dashed non-motif edges, solid motif edges
                style = []
                for edge in self.graph.edges():
                    if edge in motif_edges or tuple(reversed(edge)) in motif_edges:
                        style.append("solid")
                    else:
                        style.append("dashed")

                motif_attributes = {
                    "node_size": node_sizes,
                    "linewidths": line_widths,
                    "node_color": comp_colors,
                    "width": edge_widths,
                    "style": style,
                    "with_labels": False,
                    "pos": layout
                }

                attribute_list.append(motif_attributes)

            attributes.append(attribute_list)

        return attributes 

    def get_tdd_root(self):
        """Find the root of the treedepth decomposition"""
        for node in self.tdd.nodes():
            if self.tdd.out_degree(node) == 0:
                return node

class CombineSetGenerator(object):
    def __init__(self, color_set, colors, pattern_size, min_size):
        self.color_set = color_set
        self.colors = colors
        self.pattern_size = pattern_size
        self.min_size = min_size

    def get_color_sets(self):
        unused = self.colors - self.color_set
        low = max(self.min_size-len(self.color_set), 0) - 1
        high = self.pattern_size-len(self.color_set)
        color_list = sorted(list(self.color_set))
        sets = []
        for size in range(high, low, -1):
            sets.append([color_list+list(s) for s in combinations(unused, size)])
        return sets
