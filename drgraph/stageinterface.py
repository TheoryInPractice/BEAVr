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

    name = None

    @abstractmethod
    def __init__(self, parent):
        """Create a sizer with a toolbar and a space for the StageVisualizer"""
        super(StageInterface, self).__init__(parent)

        # Make the sizer
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Make the toolbar, then add it to the sizer
        self.tb = wx.ToolBar(self, style=wx.TB_VERTICAL)
        self.sizer.Add(self.tb, 0, wx.EXPAND)

        # Make the visualizer
        self.set_visualization(StageVisualizer(self))

        # We want to see what's in the sizer
        self.SetSizer(self.sizer)

    def set_visualization(self, vis):
        """Set the panel to be used for visualization"""
        # Destroy the old visualization to avoid leaking memory
        try:
            self.vis.Destroy()
        except AttributeError:
            # Don't crash if there was no old visualization
            pass
        # Set the new visualizer
        self.vis = vis
        # Add it to our sizer
        self.sizer.Add(self.vis, 1, wx.EXPAND)

class DummyStageInterface(StageInterface):
    """
    A blank StageInterface.

    The DummyStageInterface has an open button in its toolbar and a blank white
    visualization.
    """

    name = "No Visualization"

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
