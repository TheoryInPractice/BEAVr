from drgraph.data_loader import DataLoader

class Factory:
    """
    Generically named wrapper for creating ConcussDataLoader via
    data_loader.DataLoaderFactory
    """
    
    def create():
        return ConcussDataLoader()


class ConcussDataLoader(DataLoader):
    """ Loads data provided by the CONCUSS pipeline """

    def load(self):
        """
        Load the data
        :return:
        """