import drgraph.data_loader

class Factory:
    """ Wrapper allowing DataLoaderFactory to create a ConcussDataLoader """

    def create(archive):
        """ Creates ConcussDataLoader with given ZipFile archive object """
        return ConcussDataLoader(archive)


class ConcussDataLoader(DataLoader):
    """ Loads data provided by the CONCUSS pipeline """

    def load(self):
        """
        Load the data
        :returns:
        """