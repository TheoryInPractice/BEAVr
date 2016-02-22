from abc import ABCMeta, abstractmethod
from zipfile import ZipFile
import ConfigParser
from os.path import basename, exists
from importlib import import_module

class DataLoader(object):
    """ Abstract Data Loader """
    __metaclass__ = ABCMeta

    def __init__(self, archive, parser):
        """
        Get the json configuration loaded by the DataLoaderFactory
        :param config_json: The loaded json configuration
        """
        self.archive = archive
        self.parser = parser

    @abstractmethod
    def load(self):
        """
        Load data from self.archive
        """

class DataLoaderFactory(object):
    """ Class that instantiates DataLoader objects """

    def load_data(self, filename):
        """
        Load data from the appropriate DataLoader for given archive filename
        :param filename: name of zip archive file containing execution data
        :returns: data returned by pipeline.DataLoader.load_data()
        """
        # Open zip archive as ZipFile object
        with ZipFile(filename, 'r') as archive:
            dl = self.data_loader(archive)
            return dl.load()


    def data_loader(self, archive):
        """
        Create the appropriate DataLoader for the given ZipFile archive
        :param archive: ZipFile object for archive containing execution data
        :returns: DataLoader for the pipeline that the execution data came from
        """
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
