#!/usr/bin/env python2
from numpy import random
from numpy import arange, sin, pi
import matplotlib
matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
import networkx as nx

import wx

class CanvasPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self, -1, self.figure)
        #self.G = nx.house_graph()
        self.G = nx.read_edgelist('karate.txt')

        # Get the same layout every time
        random.seed(0)
        # nx.draw seems to do nx.spring_layout on its own
        #pos = nx.draw_graphviz(self.G, prog='sfdp', args='-Goverlap=prism -Gstart=0')
        #pos = nx.spring_layout(self.G)

        nx.draw(self.G)
        plt.axis('off')

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.sizer.Add(self.toolbar, 0, wx.EXPAND)
        self.SetSizer(self.sizer)
        #self.vbox.Fit(self)
        self.SetSizer(self.sizer)
        self.Fit()
        self.toolbar.pan()

    def draw(self):
        #t = arange(0.0, 3.0, 0.01)
        #s = sin(2 * pi * t)
        #self.axes.draw()
        pass


if __name__ == "__main__":
    app = wx.App(False)
    fr = wx.Frame(None, title='Graph Test')
    panel = CanvasPanel(fr)
    panel.draw()
    fr.Show()
    app.MainLoop()
