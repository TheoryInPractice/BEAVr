from abc import ABCMeta, abstractmethod

import wx

class StageInterface(wx.Panel):
    """
    Abstract base class for interface of a stage.

    Defines wxPython GUI elements common to all StageInterfaces: a toolbar and
    a StageVisualizer inside a sizer.  They are left empty by default, so a
    child class must add all the specific elements it needs.
    """
    __metaclass__ = ABCMeta

    tb_size = (24, 24)

    @abstractmethod
    def __init__(self, parent):
        """Create a sizer with a toolbar and a space for the StageVisualizer"""
        super(StageInterface, self).__init__(parent)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tb = wx.ToolBar(self, style=wx.TB_VERTICAL)

        self.vis = StageVisualizer(self)

        sizer.Add(self.tb, 0, wx.EXPAND)
        sizer.Add(self.vis, 1, wx.EXPAND)

        self.SetSizer(sizer)

    def set_visualization(self, vis):
        """Set the panel to be used for visualization"""
        self.vis = vis

class DummyStageInterface(StageInterface):
    """
    A blank StageInterface.

    The DummyStageInterface has an open button in its toolbar and a blank white
    visualization.
    """

    def __init__(self, parent):
        """Create a StageInterface with nothing special added"""
        super(DummyStageInterface, self).__init__(parent)

        open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR,
                self.tb_size)
        self.tb.AddLabelTool(wx.ID_OPEN, "Open", open_bmp)

        self.tb.Realize()

class StageVisualizer(wx.Panel):
    """Base class for visualizing a particular stage of a pipeline"""

    def __init__(self, parent):
        """Create an empty StageVisualizer"""
        super(StageVisualizer, self).__init__(parent)

        self.SetBackgroundColour(wx.WHITE)
