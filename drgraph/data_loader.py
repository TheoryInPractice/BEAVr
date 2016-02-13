from abc import ABCMeta, abstractmethod

class DataLoader(object):
    """ Abstract Data Loader """
    __metaclass__ = ABCMeta

    def __init__(self, config_json):
        """
        Get the json configuration loaded by the DataLoaderFactory
        :param config_json: The loaded json configuration
        """
        self.config_json = config_json

    @abstractmethod
    def load(self):
        """
        Load data
        """

class DataLoaderFactory(object):
    """
    Class that instantiates DataLoader objects
    """

    def data_loader(self, filename):
        """Create the appropriate DataLoader for the given filename"""
