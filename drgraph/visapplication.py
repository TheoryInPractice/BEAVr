import wx

from drgraph.maininterface import MainInterface

class VisApplication(wx.App):
    """The wxPython application class for the visualization tool"""

    def OnInit(self):
        """Start the application"""
        self.config = wx.Config("drgraph")
        wx.ConfigBase.Set(self.config)

        self.frame = MainInterface(None)
        self.SetTopWindow(self.frame)
        self.frame.Show()

        return True
