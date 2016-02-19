from drgraph.data_loader import DataLoader
from networkx import graph

class Factory:
    """ Wrapper allowing DataLoaderFactory to create a ConcussDataLoader """

    def create(self, archive):
        """ Creates ConcussDataLoader with given ZipFile archive object """
        return ConcussDataLoader(archive)


class ConcussDataLoader(DataLoader):
    """ Loads data provided by the CONCUSS pipeline """

    def load(self):
        """
        Load data from self.archive
        :returns: graph 
        """

        return self.load_graph()


    def load_graph(self):
        """
        Load the data
        :returns: graph 
        """
        
        # Locate graph's filename in archive
        graphs = [fn for fn in self.archive.namelist() if '/graph.' in fn]
        if len(graphs) == 0:
            raise Exception('Cannot find graph file in archive.')
        elif len(graphs) > 1:
            raise Exception('Archive contains multiple graph files.')
        from os.path import basename
        graph_name = basename(graphs[0])

        # Get extension of graph file, which indicates storage format
        graph_ext = graph_name.split('.')[1]
        # Get correct reader for graph's format, based on file extension
        graph_reader = self.get_graph_reader(graph_ext)
        # Get name of archive's main directory, includes '/'
        dir_name =  self.archive.namelist()[0]

        # Open graph as file object
        graph_file = self.archive.open(dir_name + graph_name, 'r')
        # Use correct reader to get and return NetworkX graph from graph file
        return graph_reader(graph_file)


    def get_graph_reader(self, ext):
        """
        Identifies, imports, and returns NetworkX reader for graph file format
        :param ext: extension of graph file name, indicates data storage format
        :returns: NetworkX graph reader function for the given extension
        """

        if ext == 'gexf':
            from networkx import read_gexf
            return read_gexf
        elif ext == "graphml":
            from networkx import read_graphml
            return read_graphml
        elif ext == "gml":
            from networkx import read_gml
            return read_gml
        elif ext == "leda":
            from networkx import read_leda
            return read_leda
        elif ext == "txt":
            # Assuming it's an edgelist
            from networkx import read_edgelist
            return read_edgelist
        else:
            raise Exception('Unsupported graph file format: {0}'.format(ext))
