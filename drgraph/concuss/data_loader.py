from os.path import basename, splitext

from networkx import graph

from drgraph.data_loader import DataLoader

class Factory:
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
        self.colorings = self.load_colorings()

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

    def load_colorings(self):
        """
        Loads node color data from the data loader's archive
        coloring files must be under color/colorings/
        :returns: list of colorings, where each coloring is list of RBG tuples
        """
        colorings = []
        for f in self.archive.namelist():
            if 'color/colorings/' in f and 'color/colorings/' != f:
                coloring = []
                with self.archive.open(f) as coloring_file:
                    for line in coloring_file:
                        line = line.strip()
                        if ':' not in line:
                            continue
                        node, color = line.split(':')
                        coloring.append(int(color))
                colorings.append(coloring)
        if len(colorings) == 0:
            colorings = [0]
        return colorings

    def get_graph_reader(self, ext):
        """
        Identifies, imports, and returns NetworkX reader for graph file format
        :param ext: extension of graph file name, indicates data storage format
        :returns: NetworkX graph reader function for the given extension
        """
        if ext == '.gexf':
            from networkx import read_gexf
            return read_gexf
        elif ext == '.graphml':
            from networkx import read_graphml
            return read_graphml
        elif ext == '.gml':
            from networkx import read_gml
            return read_gml
        elif ext == '.leda':
            from networkx import read_leda
            return read_leda
        elif ext == '.txt':
            # Assuming it's an edgelist
            from networkx import read_edgelist
            return read_edgelist
        else:
            raise Exception('Unsupported graph file format: {0}'.format(ext))
