from abc import ABCMeta, abstractmethod

import wx
import matplotlib
from matplotlib.backends.backend_wxagg import (
    FigureCanvasWxAgg as FigureCanvas,
    NavigationToolbar2WxAgg as NavigationToolbar
)

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
            self.sizer.Remove(self.vis)
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

class MatplotlibVisualizer(StageVisualizer):
    """"Subclass of StageVisualizer that utilizes matplotlib"""

    def __init__(self, parent):
        """Create a StageVisualizer with matplotlib essentials"""
        super(StageVisualizer, self).__init__(parent)

        self.figure = matplotlib.figure.Figure()
        self.axes = self.figure.add_subplot(111)
        self.figure.subplots_adjust(top=1, bottom=0, right=1, left=0)

        self.axes.get_xaxis().set_visible(False)
        self.axes.get_yaxis().set_visible(False)

        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)

        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.pan()
        self.toolbar.Hide()

        self.Fit()

        self.zoomer = self.zoom_factory(self.axes, base_scale=1.5)

        self.canvas.Bind(wx.EVT_PAINT, self.on_paint)

    def on_paint(self, evt):
        """
        Redraws the canvas so we can see real time zooming
        :param evt: For binding wx.EVT_PAINT to this function
        :return: wx.PaintDC object so subclasses can call super.on_paint(evt)
                 instead of copy/pasting the contents of this function
        """
        dc = wx.PaintDC(self.canvas)
        # First, draw the graph with matplotlib
        self.canvas.draw(dc)
        return dc

    def zoom_factory(self, ax, base_scale=2.):
        """
        Handle zooming using the scroll wheel.

        Original source: https://gist.github.com/tacaswell/3144287
        """
        def zoom_fun(event):
            # Get the current x and y limits
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()
            cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
            cur_yrange = (cur_ylim[1] - cur_ylim[0])*.5
            # Get event location
            xdata = event.xdata
            ydata = event.ydata
            if event.button == 'up':
                # Deal with zoom in
                scale_factor = 1/base_scale
            elif event.button == 'down':
                # Deal with zoom out
                scale_factor = base_scale
            else:
                # Deal with something that should never happen
                scale_factor = 1
                print event.button
            # Set new limits - improved from original
            ax.set_xlim([xdata - (xdata - cur_xlim[0])*scale_factor,
                         xdata + (cur_xlim[1] - xdata)*scale_factor])
            ax.set_ylim([ydata - (ydata - cur_ylim[0])*scale_factor,
                         ydata + (cur_ylim[1] - ydata)*scale_factor])
            # Force redraw
            self.canvas.Refresh()

        # Get the figure of interest
        fig = ax.get_figure()
        # Attach the call back
        fig.canvas.mpl_connect('scroll_event', zoom_fun)

        # Return the function
        return zoom_fun
