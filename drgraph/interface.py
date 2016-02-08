import wx

class StageInterface(wx.Panel):
    """
    Abstract base class for interface of a stage.

    Defines some wxPython GUI elements like a toolbar, but doesn't put anything
    in them.
    """

    def __init__(self, parent):
        """Create a sizer with a toolbar and a space for the StageVisualizer"""
        super(StageInterface, self).__init__(parent)
