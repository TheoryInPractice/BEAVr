from abc import ABCMeta, abstractmethod
from zipfile import ZipFile
import ConfigParser
import os.path

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
    """ Class that instantiates DataLoader objects """

    def data_loader(self, filename):
        """ Create the appropriate DataLoader for the given filename """

        # Open zip archive as ZipFile object
        archive = ZipFile( filename, 'r' )
        # dir_name is filename without extension
        dir_name = filename.split('.')[0]

        # Create config parser.
        parser = ConfigParser.ConfigParser()
        # Parse visinfo.cfg for name of the pipeline the archive came from
        parser.readfp( myzip.open( dir_name + '/visinfo.cfg', 'r' ) )
        pipe_name = parser.get( 'pipeline','name' )

        # Check if data_loader.py exists in directory for the given pipeline
        if not os.path.exists( './' + pipe_name + '/data_loader.py' ):
            sys.exit( './' + pipe_name + '/data_loader.py missing.\n' )

        # Import DataLoader class for the given pipeline
        from importlib import import_module
        pipe_data_loader = import_module( pipe_name + '/data_loader.py' )
        # Create and return DataLoader object for the given pipeline
        return pipe_data_loader.Factory.create()
