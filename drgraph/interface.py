from abc import ABCMeta, abstractmethod
import webbrowser

import wx

#from drgraph.concuss.interface import ColorInterface

class MainInterface(wx.Frame):
    """
    Main window of the visualization tool.

    This class defines all the GUI elements in the main window, including
    menus and their event methods, the statusbar, and the space for
    StageInterfaces.
    """

    doc_url = 'https://github.ncsu.edu/engr-csc-sdc/2016springTeam09/wiki'

    def __init__(self, parent):
        """Create the main window and all its GUI elements"""
        super(MainInterface, self).__init__(parent, title="Visualization Tool")

        self._make_menubar()
        self.CreateStatusBar()

        self.notebook = wx.Notebook(self, wx.NewId(), style=wx.BK_DEFAULT)

        dummy = DummyStageInterface(self.notebook)
        self.notebook.AddPage(dummy, "No Visualization")

        #color = ColorInterface(self.notebook)
        #self.notebook.AddPage(color, "Color")

        self.Center()

    def _make_menubar(self):
        """Create, populate, and show the menubar"""
        # Menubar setup
        menubar = wx.MenuBar()

        # Load file submenu
        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_OPEN, help='Open execution data')
        fileMenu.Append(wx.NewId(), '&Config', 'Configure Pipeline Data')
        fitem = fileMenu.Append(wx.ID_EXIT, help='Quit application')
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
        doc = helpMenu.Append(wx.ID_HELP_CONTENTS, '&Documentation',
                        'Opens online documentation')
        self.Bind(wx.EVT_MENU, self.OnDoc, doc)
        helpMenu.Append(wx.ID_ABOUT, help='About this application')
        menubar.Append(helpMenu, '&Help')

        self.SetMenuBar(menubar)
    
    def OnQuit(self, e):
        """Quit the application"""
        self.Close()

    def OnDoc(self, e):
        """Open the online documentation"""
        webbrowser.open(self.doc_url, new=2)

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
