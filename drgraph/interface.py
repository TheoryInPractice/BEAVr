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
        super(MainInterface, self).__init__(parent, title="Visualization Tool")

        # Menubar setup
        menubar = wx.MenuBar()

        # Load file submenu
        fileMenu = wx.Menu()
        fileMenu.Append(wx.NewId(), 'Open', 'Open Execution Data')
        fileMenu.Append(wx.NewId(), 'Config', 'Configure Pipeline Data')
        fitem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)
        menubar.Append(fileMenu, '&File')

        # Load visualization submenu
        visualMenu = wx.Menu()
        preferencesMenu = wx.Menu()
        preferencesMenu.AppendCheckItem(wx.NewId(), "Color-Blind Mode")
        visualMenu.AppendMenu(wx.NewId(), 'Preferences', preferencesMenu)
        menubar.Append(visualMenu, '&Visuals')

        # Load help submenu
        helpMenu = wx.Menu()
        helpMenu.Append(wx.NewId(), 'Documentation', 'Opens documentation')
        helpMenu.Append(wx.NewId(), 'About', 'About this application')
        menubar.Append(helpMenu, '&Help')

        self.SetMenuBar(menubar)

        self.Centre()
        self.Show(True)
    
    def OnQuit(self, e):
        self.Close()

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
