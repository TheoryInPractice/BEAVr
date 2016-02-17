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
    """
    Class that instantiates DataLoader objects
    """

    def data_loader(self, filename):
        """Create the appropriate DataLoader for the given filename"""

        # Open zip archive as ZipFile object
        archive = ZipFile( filename, 'r' )
        # dir_name is filename without extension
        dir_name = filename.split('.')[0]

        # Create config parser.
        parser = ConfigParser.ConfigParser()
        # Parse visinfo.cfg for pipeline name
        parser.readfp( myzip.open( dir_name + '/visinfo.cfg', 'r' ) )
        pipeline_name = parser.get( 'pipeline','name' )

        # Check if data_loader.py exists in directory for the given pipeline
        if not os.path.exists( './' + pipeline_name + '/data_loader.py' ):
            sys.exit( './' + pipeline_name + '/data_loader.py missing.\n' )

        # Create and return data_loader object for pipeline
        ## TODO
        ## from importlib import import_module
        ## pipe_data_loader = import_module( pipeline_name + '/data_loader.py' )
