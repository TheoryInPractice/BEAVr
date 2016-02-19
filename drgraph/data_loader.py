from abc import ABCMeta, abstractmethod
from zipfile import ZipFile
import ConfigParser

class DataLoader(object):
    """ Abstract Data Loader """
    __metaclass__ = ABCMeta

    def __init__(self, archive):
        """
        Get the json configuration loaded by the DataLoaderFactory
        :param config_json: The loaded json configuration
        """
        self.archive = archive

    @abstractmethod
    def load(self):
        """
        Load data from self.archive
        """

class DataLoaderFactory(object):
    """ Class that instantiates DataLoader objects """

    def data_loader(self, filename):
        """
        Create the appropriate DataLoader for the given zip archive filename
        :param filename: Name of zip archive file containing execution data
        :returns: DataLoader for the pipeline that the execution data came from
        """
        
        # Open zip archive as ZipFile object
        archive = ZipFile(filename, 'r')
        # dir_name is archive filename with extension removed
        from os.path import basename, exists
        dir_name = basename(filename).split('.')[0]

        # Create config parser.
        parser = ConfigParser.ConfigParser()
        # Parse visinfo.cfg for name of the pipeline the archive came from
        parser.readfp( archive.open( dir_name + '/visinfo.cfg', 'r' ) )
        pipe_name = parser.get('pipeline', 'name')

        # Check if data_loader.py exists in directory for the given pipeline
        # TODO: Change 'drgraph' directory before finalization of project
        if not exists( './drgraph/' + pipe_name + '/data_loader.py' ):
            from sys import exit
            exit( '/' + pipe_name + '/data_loader.py does not exist.\n' )

        # Import DataLoader class for the given pipeline
        from importlib import import_module
        pipe_loader = import_module( 'drgraph.' + pipe_name + '.data_loader' )
        # Create and return DataLoader object for the given pipeline
        pipe_factory = pipe_loader.Factory()
        return pipe_factory.create( archive )
