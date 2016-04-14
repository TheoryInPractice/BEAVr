from os.path import basename, splitext
import collections

from networkx import Graph

from drgraph.dataloader import DataLoader

class Factory(object):
    """ Wrapper allowing DataLoaderFactory to create a ConcussDataLoader """

    def create(self, archive, parser):
        """
        Creates ConcussDataLoader with given vis archive and parsed
        configuration
        """
        return ConcussDataLoader(archive, parser)


class ConcussDataLoader(DataLoader):
    """ Loads data provided by the CONCUSS pipeline """

    def load(self):
        """
        Load data from self.archive
        :returns: loads and stores graph and colorings
        """
        self.graph = self.load_graph()
        self.pattern = self.load_pattern()
        self.colorings = self.load_colorings()
        self.big_component = self.load_big_component()
        self.table = self.load_dp_table()

    def load_graph(self):
        """
        Loads graph data from the data loader's archive
        Graph filename must be specified in visinfo.cfg
        :returns: graph
        """
        graph_name = self.parser.get('graphs', 'graph')

        # Get extension of graph file, which indicates storage format
        graph_ext = splitext( graph_name )[1]
        # Get correct reader for graph's format, based on file extension
        graph_reader = self.get_graph_reader(graph_ext)

        # Open graph as file object
        with self.archive.open(graph_name, 'r') as graph_file:
            # Use correct reader to get and return NetworkX graph from graph file
            return graph_reader(graph_file)

    def load_pattern(self):
        """
        Loads graph data from the data loader's archive
        Pattern filename must be specified in visinfo.cfg
        :returns: graph
        """
        pattern_name = self.parser.get('graphs', 'motif')

        # Get extension of graph file, which indicates storage format
        pattern_ext = splitext(pattern_name)[1]
        # Get correct reader for graph's format, based on file extension
        graph_reader = self.get_graph_reader(pattern_ext)

        # Open graph as file object
        with self.archive.open(pattern_name, 'r') as pattern_file:
            # Use correct reader to get and return NetworkX graph from graph file
            return graph_reader(pattern_file)

    def load_big_component(self):
        """
        Loads the largest component found by CONCUSS.

        This component is always in the file count/big_component.txt in
        edgelist format.
        :returns: graph
        """
        comp_name = 'count/big_component.txt'

        # Get extension of graph file, which indicates storage format
        comp_ext = splitext(comp_name)[1]
        # Get correct reader for graph's format, based on file extension
        graph_reader = self.get_graph_reader(comp_ext)

        # Open graph as file object
        with self.archive.open(comp_name, 'r') as comp_file:
            # Use correct reader to get and return NetworkX graph from graph file
            return graph_reader(comp_file)

    def load_colorings(self):
        """
        Loads node color data from the data loader's archive
        coloring files must be under color/colorings/
        :returns: list of colorings, where each coloring is list of RBG tuples
        """
        colorings = []
        files = self.archive.namelist()
        files.sort()
        nodes = 0
        for f in files:
            if 'color/colorings/' == f[:16] and 'color/colorings/' != f:
                coloring = []
                with self.archive.open(f) as coloring_file:
                    for line in coloring_file:
                        line = line.strip()
                        if ':' not in line:
                            continue
                        node, color = line.split(':')
                        node = int(node)
                        color = int(color)
                        while len(coloring) <= node:
                            coloring.append(0)
                        coloring[node] = color
                colorings.append(coloring)
        if len(colorings) == 0:
            colorings = [0]
        return colorings

    def load_dp_table(self):
        """
        Read the dynamic programming table provided by CONCUSS

        Returns: $table$ - a dictionary which has the following format:
        key: tuple of vertices
        value: a list of lists each of which has the format:
               [count, k_pat_vertices, k_pat_boundary]
               where $count$ is an integer,
                     $k_pat_vertices$ is a list of vertices
                     $k_pat_boundary$ is a dictionary representing pi
                     where pi maps vertices in $k_pat_vertices$ to labels
        """

        import ast
        dp_table_filename = "count/dp_table.txt"
        table = {}
        with self.archive.open(dp_table_filename, 'r') as dp_table_file:
            line = dp_table_file.readline().strip()
            # Read until we reach eof
            while line != "":
                # Check if we have a new block
                block = True if line[-1] == "{" else False
                # If we have a block
                if block:
                    # Get the vertices
                    vertex_list = [int(num) for num in line[1: line.find(']')].split(",")]
                    # Read the first line in the block
                    block_line = dp_table_file.readline().strip()
                    # Make a list to store each entry in the block
                    values = []
                    # Loop until we reach end of block
                    while block_line != "}":
                        # For each line in the block make a list
                        block_entry = []
                        # Get the count, k_pat_vertices and boundary from that line
                        count, k_pat_vertices, k_pat_boundary = tuple(block_line.split(";"))
                        # Get terms in the boundary
                        terms = []
                        for term in k_pat_boundary.strip()[1:-1].split(","):
                            if term != "":
                                terms.append(term.strip())
                        # Make a dictionary that represents pi
                        pi = {}
                        # Populate pi
                        for term in terms:
                            key_val = term.split(":")
                            pi[int(key_val[0])] = int(key_val[1])
                        # Add the count, k_pat_vertices and pi to our list
                        block_entry.append(int(count))
                        block_entry.append(ast.literal_eval(k_pat_vertices.strip()))
                        block_entry.append(pi)
                        # Add entry to values
                        values.append(block_entry)
                        # Go to the next line
                        block_line = dp_table_file.readline().strip()
                    # Add k_pattern as key and values as value
                    table[tuple(vertex_list)] = values
                # Get the next line
                line = dp_table_file.readline().strip()
        # return the DP table
        return table

    def get_graph_reader(self, ext):
        """
        Identifies, imports, and returns NetworkX reader for graph file format
        :param ext: extension of graph file name, indicates data storage format
        :returns: NetworkX graph reader function for the given extension
        """
        if ext == '.gexf':
            return read_gexf
        elif ext == '.graphml':
            return read_graphml
        elif ext == '.gml':
            return read_gml
        elif ext == '.leda':
            return read_leda
        elif ext == '.txt':
            # Assuming it's an edgelist
            return read_edgelist
        else:
            raise Exception('Unsupported graph file format: {0}'.format(ext))

# The following code is from CONCUSS, https://github.com/theoryinpractice/concuss/,
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
class multidict(object):

    def __init__(self):
        self.d = collections.defaultdict(list)

    def __getitem__(self, key):
        if len(self.d[key]) == 1:
            return self.d[key][0]
        return self.d[key]

    def __setitem__(self, key, value):
        if value is None:
            self.d[key] = []
        else:
            self.d[key].append(value)

    def __iter__(self):
        return iter(self.d)

    def __contains__(self, key):
        return key in self.d

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.d)

    def __str__(self):
        res = "{"
        for key in self:
            if len(self.d[key]) == 1:
                res += "{0}: {1}, ".format(key, self.d[key][0])
            else:
                res += "{0}: {1}, ".format(key, self.d[key])
        if len(self) != 0:
            res = res[:-2]
        res += "}"
        return res

def read_gexf(graph_file):
    from BeautifulSoup import BeautifulSoup as Soup
    soup = Soup(graph_file.read())
    graph = Graph()

    for edge in soup.findAll("edge"):
        source = int(edge['source'])
        target = int(edge['target'])
        graph.add_edge(source, target)
    return graph

def read_graphml(graph_file):
    from BeautifulSoup import BeautifulSoup as Soup
    soup = Soup(graph_file.read())
    graph = Graph()

    for edge in soup.findAll("edge"):
        source = int(edge['source'])
        target = int(edge['target'])
        graph.add_edge(source, target)
    return graph
    
def read_gml(graph_file):
    graph = Graph()

    data = read_gml_data(graph_file)
    for n in data['graph']['node']:
        graph.add_node(int(n['id']))

    for e in data['graph']['edge']:
        graph.add_edge(int(e['source']), int(e['target']))

    return graph
    
def read_leda(graph_file):
    graph = Graph()

    numVertices = 10**10
    lines = graph_file

    # Skip preable
    skip_lines(lines, 4)
    numVertices = int(next(lines))

    # We do not need vertex labels
    skip_lines(lines, numVertices)

    numEdges = int(next(lines))

    for line in lines:
        line = line.strip()
        if line == '' or line[0] == '#':
            continue
        s, t, r, l = line.split(' ')
        graph.add_edge(int(s)-1, int(t)-1)  # LEDA is 1-based.

    return graph
    
def read_edgelist(graph_file):
    graph = Graph()
    for line in graph_file:
        line = line.strip()
        if line[0] == '#':
            continue
        source, target = line.split()
        s = int(source)
        t = int(target)

        graph.add_edge(s, t)

    return graph

def read_gml_data(graph_file):
    stream = []
    for l in graph_file:
        l = l.strip()
        if len(l) == 0:
            continue
        fields = l.split(" ")
        token = lambda: None  # Inline object
        token.name = None
        if len(fields) == 1 or (len(fields) == 2 and fields[1] == '['):
            v = fields[0]
            if v == "[":
                token.type = "BLOCK_START"
            elif v == "]":
                token.type = "BLOCK_END"
            else:
                token.type = "BLOCK_NAME"
                token.name = v
        else:
            token.type = "FIELD"
            token.name = fields[0]
            token.value = "".join(fields[1:])
        stream.append(token)

    data = multidict()
    data[0] = 0
    stack = [data]
    del data.d[0]
    for token in stream:
        current = stack[-1]
        if token.type == "BLOCK_NAME":
            # Start new data block
            block = multidict()
            block[0] = 0
            label = token.name
            current[label] = block
            stack.append(block)
            del block.d[0]
        elif token.type == "BLOCK_START":
            pass
        elif token.type == "BLOCK_END":
            stack.pop()
        elif token.type == "FIELD":
            current[token.name] = token.value
    return data

def skip_lines(fileit, num):
    skipped = 0
    while skipped < num:
        line = next(fileit).strip()
        if line != '' and line[0] != '#':
            skipped += 1
