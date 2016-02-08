from abc import ABCMeta, abstractmethod
import wx

class MainInterface(wx.Frame):
    """
    Main window of the visualization tool.

    This class defines all the GUI elements in the main window, including
    menus and their event methods, the statusbar, and the space for
    StageInterfaces.
    """

    def __init__(self, parent):
        """Create the main window and all its GUI elements"""
        super(MainInterface, self).__init__(parent)

class StageInterface(wx.Panel):
    """
    Abstract base class for interface of a stage.

    Defines some wxPython GUI elements like a toolbar, but doesn't put anything
    in them.
    """
    __metaclass__ = ABCMeta

    def __init__(self, parent):
        """Create a sizer with a toolbar and a space for the StageVisualizer"""
        super(StageInterface, self).__init__(parent)
