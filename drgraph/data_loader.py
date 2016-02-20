from abc import ABCMeta, abstractmethod
from zipfile import ZipFile
import ConfigParser
from os.path import basename, exists
from importlib import import_module

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

        # Create config parser.
        parser = ConfigParser.ConfigParser()
        # Parse visinfo.cfg for name of the pipeline the archive came from
        with archive.open('visinfo.cfg', 'r') as visinfo:
            parser.readfp(visinfo)
        pipe_name = parser.get('pipeline', 'name')

        # Import DataLoader class for the given pipeline
        try:
            pipe_loader = import_module('drgraph.' + pipe_name + '.data_loader')
        except ImportError:
            raise UnknownPipelineError(pipe_name)
            
        # Create and return DataLoader object for the given pipeline
        pipe_factory = pipe_loader.Factory()
        return pipe_factory.create(archive, parser)

class UnknownPipelineError(Exception):
    """
    Exception for visualization files from unknown pipelines
    
    Attributes:
        pipe -- The pipeline name in question
        msg -- Explanation of the error
    """

    def __init__(self, pipe):
        self.pipe = pipe
        self.msg = "Unknown pipeline " + repr(self.pipe)

    def __str__(self):
        return self.msg
