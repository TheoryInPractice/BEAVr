#
# This file is part of BEAVr, https://github.com/theoryinpractice/beavr/, and is
# Copyright (C) North Carolina State University, 2016. It is licensed under
# the three-clause BSD license; see LICENSE.
#

import argparse

import wx

from beavr.maininterface import MainInterface

class VisApplication(wx.App):
    """The wxPython application class for the visualization tool"""

    def OnInit(self):
        """Start the application"""
        # Parse command line arguments
        parser = argparse.ArgumentParser()

        parser.add_argument('data',
                            help='filename of the pipeline execution data',
                            type=str, nargs='?', default=None)

        args = parser.parse_args()

        # Set up the configuration file
        self.config = wx.Config("beavr")
        wx.ConfigBase.Set(self.config)

        # Create and show the main window
        self.frame = MainInterface(None, filename=args.data)
        self.SetTopWindow(self.frame)
        self.frame.Show()

        return True


def run():
    """Run BEAVr"""
    app = VisApplication()
    app.MainLoop()
