import webbrowser

import wx

from drgraph.concuss.stageinterface import ColorInterface
from drgraph.stageinterface import DummyStageInterface

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

        color = ColorInterface(self.notebook)
        self.add_tab(color)

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
        about = helpMenu.Append(wx.ID_ABOUT, help='About this application')
        self.Bind(wx.EVT_MENU, self.OnAbout, about)
        menubar.Append(helpMenu, '&Help')

        self.SetMenuBar(menubar)

    def add_tab(self, interface):
        """Add an interface tab with the correct tab name"""
        self.notebook.AddPage(interface, interface.name)
    
    def OnQuit(self, e):
        """Quit the application"""
        self.Close()

    def OnDoc(self, e):
        """Open the online documentation"""
        webbrowser.open(self.doc_url, new=2)

    def OnAbout(self, e):
        """Show an about box"""
        info = wx.AboutDialogInfo()
        info.Name = "Visualization Tool"
        info.Copyright = "(C) 2016 Team 9"
        info.Description = "A tool for visualizing graph algorithmic pipelines"
        info.WebSite = ("https://github.ncsu.edu/engr-csc-sdc/2016springTeam09",
                        "Website")
        info.Developers = ["Yang Ho", "Clayton G. Hobbs", "Brandon Mork",
                           "Nishant G. Rodrigues"]
        info.License = "BSD"  # TODO: set this as the actual license text

        wx.AboutBox(info)
