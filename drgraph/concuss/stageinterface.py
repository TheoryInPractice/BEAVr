import os
import os.path as path

import wx
from numpy import random
import networkx as nx
import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import (
    FigureCanvasWxAgg as FigureCanvas,
    NavigationToolbar2WxAgg as NavigationToolbar
)
from matplotlib.figure import Figure

from drgraph.stageinterface import StageInterface, StageVisualizer

class ColorInterface(StageInterface):
    """GUI elements for CONCUSS coloring stage visualization"""

    name = "Color"

    def __init__(self, parent):
        """Fill the empty GUI elements with coloring-specific widgets"""
        super(ColorInterface, self).__init__(parent)

        # Forward button
        fwd_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR,
                self.tb_size)
        fwd = self.tb.AddLabelTool(wx.ID_FORWARD, "Forward", fwd_bmp)
        self.Bind(wx.EVT_TOOL, self.on_forward, fwd)

        # Backward button
        back_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR,
                self.tb_size)
        back = self.tb.AddLabelTool(wx.ID_BACKWARD, "Backward", back_bmp)
        self.Bind(wx.EVT_TOOL, self.on_backward, back)

        self.tb.AddSeparator()

        # Random Layout buton
        tali_path = path.join(os.getcwd(), 'data', 'icons', 'tali.png')
        rand_bmp = wx.Bitmap(tali_path, wx.BITMAP_TYPE_PNG)
        rand = self.tb.AddLabelTool(wx.NewId(), "Random Layout", rand_bmp)
        self.Bind(wx.EVT_TOOL, self.on_random, rand)

        self.tb.Realize()

        vis = ColorVisualizer(self)
        self.set_visualization(vis)

    def on_forward(self, e):
        """Generate a new random graph layout"""
        if self.vis.coloring_index < len(self.vis.colorings) - 1:
            self.vis.coloring_index += 1
            self.vis.update_graph_display()
            
    def on_backward(self, e):
        """Generate a new random graph layout"""
        if self.vis.coloring_index > 0:
            self.vis.coloring_index -= 1
            self.vis.update_graph_display()

    def on_random(self, e):
        """Generate a new random graph layout"""
        self.vis.graph_layout()
        self.vis.update_graph_display()


class DecomposeInterface(StageInterface):
    """GUI elements for CONCUSS decomposition stage visualization"""

    name = "Decompose"

    def __init__(self, parent):
        """Fill the empty GUI elements with decomposition-specific widgets"""
        super(DecomposeInterface, self).__init__(parent)

        # Forward button
        fwd_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR,
                self.tb_size)
        fwd = self.tb.AddLabelTool(wx.ID_FORWARD, "Forward", fwd_bmp)
        self.Bind(wx.EVT_TOOL, self.on_forward, fwd)

        # Backward button
        back_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR,
                self.tb_size)
        back = self.tb.AddLabelTool(wx.ID_BACKWARD, "Backward", back_bmp)
        self.Bind(wx.EVT_TOOL, self.on_backward, back)

        self.tb.AddSeparator()

        self.tb.Realize()

        vis = DecomposeVisualizer(self)
        self.set_visualization(vis)

    def on_forward(self, e):
        """Generate a new random graph layout"""
        if self.vis.graph_index < len(self.vis.graphs) - 1:
            self.vis.graph_index += 1
            self.vis.update_graph_display()
            
    def on_backward(self, e):
        """Generate a new random graph layout"""
        if self.vis.graph_index > 0:
            self.vis.graph_index -= 1
            self.vis.update_graph_display()


class CountInterface(StageInterface):
    """GUI elements for CONCUSS counting stage visualization"""

    name = "Count"

    def __init__(self, parent):
        """Fill the empty GUI elements with counting-specific widgets"""
        super(CountInterface, self).__init__(parent)


class CombineInterface(StageInterface):
    """GUI elements for CONCUSS combination stage visualization"""

    name = "Combine"

    def __init__(self, parent):
        """Fill the empty GUI elements with combination-specific widgets"""
        super(CombineInterface, self).__init__(parent)


class ColorVisualizer(StageVisualizer):
    """The visualization for the CONCUSS coloring stage"""

    def __init__(self, parent):
        """Create the CONCUSS coloring visualization"""
        super(ColorVisualizer, self).__init__(parent)

        self.figure = matplotlib.figure.Figure()
        self.axes = self.figure.add_subplot(111)
        self.figure.subplots_adjust(top=1, bottom=0, right=1, left=0)

        self.axes.get_xaxis().set_visible(False)
        self.axes.get_yaxis().set_visible(False)

        self.graph = nx.Graph()
        self.layout = []

        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)

        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.pan()
        self.toolbar.Hide()

        self.Fit()

    def set_graph(self, graph, colorings, palette='brewer'):
        """Set the graph to display"""
        self.coloring_index = 0
        self.zoomer = self.zoom_factory(self.axes, base_scale=1.5)

        self.graph = graph
        self.palette = palette
        self.colorings = colorings
        self.map_colorings()
        self.graph_layout(0)

        self.update_graph_display()

    def map_colorings(self):
        """Load colors from palette, map colorings to palette colors"""
        colors = []
        with open('data/palettes/'+self.palette) as palette_file:
            for line in palette_file:
                line = line.strip()
                if '#' not in line and ',' in line:
                    colors.append([int(c)/255.0 for c in line.split(',')])
        if len(self.colorings) == 1:
            self.mapped_colorings = [colors[self.colorings[0]]]
        else:
            mapped_colorings = []
            for coloring in self.colorings:
                mapped_coloring = []
                for color in coloring:
                    mapped_coloring.append(colors[color%len(colors)])
                mapped_colorings.append(mapped_coloring)
            self.mapped_colorings = mapped_colorings

    def graph_layout(self, seed=None): # done
        """Compute a layout of the graph, with an optional seed"""
        if seed is not None:
            random.seed(seed)
        self.layout = nx.spring_layout(self.graph)

    def update_graph_display(self): # done
        """Compute a layout of the graph, with an optional seed"""
        self.axes.clear()
        self.axes.set_axis_bgcolor((.8,.8,.8))
        nx.draw_networkx(self.graph, self.layout, ax=self.axes,
                         node_color=self.mapped_colorings[self.coloring_index],
                         with_labels=False)
        self.figure.canvas.draw()

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
            self.figure.canvas.draw()

        # Get the figure of interest
        fig = ax.get_figure()
        # Attach the call back
        fig.canvas.mpl_connect('scroll_event', zoom_fun)

        # Return the function
        return zoom_fun


class DecomposeVisualizerSubPlots(StageVisualizer):
    """The visualization for the CONCUSS coloring stage"""

    def __init__(self, parent):
        """Create the CONCUSS coloring visualization"""
        super(DecomposeVisualizer, self).__init__(parent)

        self.figure = matplotlib.figure.Figure()

        self.graph_index = 0
        self.axes = []
        self.graphs = [] 
        self.layouts = []
        self.colorings = []

        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)

        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.pan()
        self.toolbar.Hide()

        self.Fit()

    def set_graph(self, graphs, colorings, palette='brewer'):
        """Set the graph to display"""
        self.graph_index = 0

        #self.zoomer = self.zoom_factory(self.axes, base_scale=1.5)

        self.graphs = graphs
        self.axes = []
        num_graphs = len(self.graphs)
        per_row = (num_graphs + 1) / 2
        for i in range(num_graphs):
            self.axes.append(self.figure.add_subplot(2, per_row, i+1))
        self.palette = palette
        self.colorings = colorings
        self.map_colorings()
        self.graph_layouts(0)

        self.update_graph_display()

    def map_colorings(self):
        """Load colors from palette, map colorings to palette colors"""
        colors = []
        with open('data/palettes/'+self.palette) as palette_file:
            for line in palette_file:
                line = line.strip()
                if '#' not in line and ',' in line:
                    colors.append([int(c)/255.0 for c in line.split(',')])
        if len(self.colorings) == 1:
            self.mapped_colorings = [colors[self.colorings[0]]]
        else:
            mapped_colorings = []
            for coloring in self.colorings:
                mapped_coloring = []
                for color in coloring:
                    mapped_coloring.append(colors[color%len(colors)])
                mapped_colorings.append(mapped_coloring)
            self.mapped_colorings = mapped_colorings

    def graph_layouts(self, seed=None): # done
        """Compute a layout of the graph, with an optional seed"""
        if seed is not None:
            random.seed(seed)
        for i in range(len(self.graphs)):
            self.layouts.append(nx.spring_layout(self.graphs[i]))

    def update_graph_display(self): # done
        """Compute a layout of the graph, with an optional seed"""
        for i in range(len(self.graphs)):
            self.axes[i].clear()
            self.axes[i].set_axis_bgcolor((.8,.8,.8))
            nx.draw_networkx(self.graphs[i], self.layouts[i], ax=self.axes[i],
                             node_color=self.mapped_colorings[self.graph_index],
                             with_labels=False)
        self.figure.canvas.draw()

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
            self.figure.canvas.draw()

        # Get the figure of interest
        fig = ax.get_figure()
        # Attach the call back
        fig.canvas.mpl_connect('scroll_event', zoom_fun)

        # Return the function
        return zoom_fun


class DecomposeVisualizer(StageVisualizer):
    """The visualization for the CONCUSS coloring stage"""

    def __init__(self, parent):
        """Create the CONCUSS coloring visualization"""
        super(DecomposeVisualizer, self).__init__(parent)

        self.figure = matplotlib.figure.Figure()
        self.axes = self.figure.add_subplot(111)
        self.figure.subplots_adjust(top=1, bottom=0, right=1, left=0)

        self.axes.get_xaxis().set_visible(False)
        self.axes.get_yaxis().set_visible(False)

        self.graph = nx.Graph()
        self.layouts = []
        self.grid = {}

        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)

        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.pan()
        self.toolbar.Hide()

        self.Fit()

    def set_graph(self, graph, colorings, palette='brewer'):
        """Set the graph to display"""
        self.graph_index = 0
        self.zoomer = self.zoom_factory(self.axes, base_scale=1.5)

        self.graph = graph
        self.palette = palette
        self.colorings = colorings
        self.map_colorings()
        self.graph_layout()

        self.update_graph_display()

    def map_colorings(self):
        """Load colors from palette, map colorings to palette colors"""
        colors = []
        with open('data/palettes/'+self.palette) as palette_file:
            for line in palette_file:
                line = line.strip()
                if '#' not in line and ',' in line:
                    colors.append([int(c)/255.0 for c in line.split(',')])
        if len(self.colorings) == 1:
            self.mapped_colorings = [colors[self.colorings[0]]]
        else:
            mapped_colorings = []
            for coloring in self.colorings:
                mapped_coloring = []
                for color in coloring:
                    mapped_coloring.append(colors[color%len(colors)])
                mapped_colorings.append(mapped_coloring)
            self.mapped_colorings = mapped_colorings

    def graph_layout(self): # done
        """Compute a layout of the graph, with an optional seed"""
        # Compute tree layouts for each connected component
        layouts = []
        for sub in nx.connected_component_subgraphs(self.graph):
            layouts.append(nx.circular_layout(sub))
        
        # Calculate offset
        y_offset = 10
        x_offset = 10
        for l in layouts:
            for index in l:
                self.grid[index] = [l[index][0] + x_offset, l[index][1] + y_offset]
            x_offset += 10
            if x_offset > 20:
                x_offset = 10
                y_offset += 10

    def update_graph_display(self): # done
        """Compute a layout of the graph, with an optional seed"""
        self.axes.clear()
        self.axes.set_axis_bgcolor((.8,.8,.8))
        nx.draw_networkx(self.graph, self.grid, ax=self.axes,
                         node_color=self.mapped_colorings[self.graph_index],
                         with_labels=False)
        self.figure.canvas.draw()

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
            self.figure.canvas.draw()

        # Get the figure of interest
        fig = ax.get_figure()
        # Attach the call back
        fig.canvas.mpl_connect('scroll_event', zoom_fun)

        # Return the function
        return zoom_fun
