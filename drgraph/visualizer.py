import wx

class StageVisualizer(wx.Panel):
    """
    Abstract class that handles visualization for a particular step.
    """

    def __init__(self, parent):
        """Creates a window to display the visuals in"""
        super(StageVisualizer, self).__init__(parent) 
