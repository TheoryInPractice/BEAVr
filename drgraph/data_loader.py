from abc import ABCMeta, abstractmethod

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
        Load data
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
        from zipfile import ZipFile
        archive = ZipFile(filename, 'r')
        # dir_name is archive name with extension removed
        import os.path
        dir_name = os.path.basename(filename).split('.')[0]
        print dir_name

        # Create config parser.
        import ConfigParser
        parser = ConfigParser.ConfigParser()
        # Parse visinfo.cfg for name of the pipeline the archive came from
        parser.readfp( archive.open( dir_name + '/visinfo.cfg', 'r' ) )
        pipe_name = parser.get('pipeline', 'name')

        # Check if data_loader.py exists in directory for the given pipeline
        # TODO: Change 'drgraph' directory before finalization of project
        if not os.path.exists( './drgraph/' + pipe_name + '/data_loader.py' ):
            from sys import exit
            exit( '/' + pipe_name + '/data_loader.py does not exist.\n' )

        # Import DataLoader class for the given pipeline
        from importlib import import_module
        pipe_data_loader = import_module( pipe_name + '.data_loader' )
        # Create and return DataLoader object for the given pipeline
        return pipe_data_loader.Factory.create( archive )
