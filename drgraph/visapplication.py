import wx

import drgraph.interface

class VisApplication(wx.App):
    """The wxPython application class for the visualization tool"""

    def OnInit(self):
        """Set and show the application's main window"""
        self.frame = drgraph.interface.MainInterface(None)
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True
