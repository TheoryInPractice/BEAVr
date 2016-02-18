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

        return load_graph()


    def load_graph(self):
        """
        Load the data
        :returns: graph 
        """

        # dir_name is archive filename with extension removed
        from os.path import basename
        dir_name = basename(filename).split('.')[0]

        # Locate graph file in archive
        # TODO: self.archive.namelist() 
        # TODO: graph_file_name =  

        # Get extension of graph file, which indicates storage format
        graph_file_ext = graph_file_name.split('.')[1]
        # Get correct reader for graph's format, based on file extension
        graph_reader = get_graph_reader(graph_file_ext)

        # Open graph as file object
        graph_file = self.archive.open(dir_name + '/' + graph_file_name, 'rb')
        # Use correct reader to get and return NetworkX graph from graph file
        return graph_reader(graph_file)


    def get_graph_loader(ext):
        """
        Identifies, imports, and returns NetworkX reader for graph file format
        :param ext: extension of graph file name, indicates data storage format
        :returns: NetworkX graph reader function for the given extension
        """

        if ext == '.gexf':
            from networkx import read_gexf
            return read_gexf
        elif ext == ".graphml":
            from networkx import read_graphml
            return read_graphml
        elif ext == ".gml":
            from networkx import read_gml
            return read_gml
        elif ext == ".leda":
            from networkx import read_leda
            return read_leda
        elif ext == ".txt":
            # Assuming it's an edgelist
            from networkx import read_edgelist
            return read_edgelist
        else:
            raise Exception('Unsupported graph file format: {0}'.format(ext))
