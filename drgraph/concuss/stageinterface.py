import math
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
from drgraph.concuss.visualizerbackend import DecompositionGenerator
from drgraph.util import load_palette, map_coloring, map_colorings

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
        self.vis.update_graph_display(reset_zoom=True)


class DecomposeInterface(StageInterface):
    """GUI elements for CONCUSS decomposition stage visualization"""

    name = "Decompose"

    def __init__(self, parent, graph, pattern, coloring):
        """Fill the empty GUI elements with decomposition-specific widgets"""
        super(DecomposeInterface, self).__init__(parent)

        vis = DecomposeVisualizer(self)
        self.set_visualization(vis)
        self.vis.set_graph(graph, pattern, coloring)

        # Set one button
        one_bmp = self.color_set_icon(0)
        one = self.tb.AddLabelTool(wx.NewId(), "Color set one", one_bmp)
        self.Bind(wx.EVT_TOOL, self.on_one, one)

        # Set two button
        two_bmp = self.color_set_icon(1)
        two = self.tb.AddLabelTool(wx.NewId(), "Color set two", two_bmp)
        self.Bind(wx.EVT_TOOL, self.on_two, two)

        # Set three button
        three_bmp = self.color_set_icon(2)
        three = self.tb.AddLabelTool(wx.NewId(), "Color set three", three_bmp)
        self.Bind(wx.EVT_TOOL, self.on_three, three)

        # Set four button
        four_bmp = self.color_set_icon(3)
        four = self.tb.AddLabelTool(wx.NewId(), "Color set four", four_bmp)
        self.Bind(wx.EVT_TOOL, self.on_four, four)

        # Not needed until we get something below it
        #self.tb.AddSeparator()

        self.tb.Realize()

    def color_set_icon(self, index):
        """Create an icon for the given color set index"""
        color_set = sorted(self.vis.color_sets[index])
        # Create the bitmap
        icon = wx.EmptyBitmap(*self.tb_size)
        # Create a DC to draw on the bitmap
        dc = wx.MemoryDC()
        dc.SelectObject(icon)
        # Draw on the bitmap using the DC
        dc.Clear()
        dc.SetPen(wx.Pen(wx.BLACK, 1))
        assert self.tb_size[0] == self.tb_size[1], "Assume square icons"
        # Calculate dimensions of the squares and grid
        tb_size = self.tb_size[0]
        grid_len = int(math.ceil(math.sqrt(len(color_set))))
        grid_size = tb_size // grid_len
        # Draw each square
        for color in color_set:
            # Prepare to draw in the right color
            rgb = [int(channel * 255) for channel in
                    self.vis.palette[color%len(self.vis.palette)]]
            dc.SetBrush(wx.Brush(wx.Colour(*rgb)))
            # Calculate where the square should be located
            grid_x = color_set.index(color) % grid_len
            grid_y = color_set.index(color) / grid_len
            # Draw the square
            dc.DrawRectangle(grid_x*grid_size, grid_y*grid_size, grid_size,
                    grid_size)
        # Select the null bitmap to flush all changes to icon
        dc.SelectObject(wx.NullBitmap)
        return icon

    def on_one(self, e):
        """Show the decompositions for color set one"""
        self.vis.graph_index = 0
        self.vis.update_graph_display()
            
    def on_two(self, e):
        """Show the decompositions for color set two"""
        self.vis.graph_index = 1
        self.vis.update_graph_display()

    def on_three(self, e):
        """Show the decompositions for color set three"""
        self.vis.graph_index = 2
        self.vis.update_graph_display()

    def on_four(self, e):
        """Show the decompositions for color set four"""
        self.vis.graph_index = 3
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

        self.canvas.Bind(wx.EVT_PAINT, self.on_paint)

    def on_paint(self, evt):
        """Draw a legend in the top-left corner of the graph display"""
        dc = wx.PaintDC(self.canvas)
        # First, draw the graph with matplotlib
        self.canvas.draw(dc)

        # Calculate the size of the legend
        legend_height = 40  # Should be big enough
        legend_width = 0
        # Text size
        step_label = 'Step {0}'.format(self.coloring_index)
        step_extents = self.GetFullTextExtent(step_label)
        margin = (legend_height - step_extents[1]) / 2
        # Add enough width for the text
        legend_width += 2 * margin + step_extents[0]
        separator_x = legend_width
        legend_width += margin
        # Add enough width for the colors
        color_set = set(self.colorings[self.coloring_index])
        if self.coloring_index > 0:
            previous_color_set = set(self.colorings[self.coloring_index - 1])
        else:
            previous_color_set = set()
        color_delta = len(color_set ^ previous_color_set)
        if len(color_set) < len(previous_color_set):
            color_delta *= -1
        if self.coloring_index > 0 and color_delta > 0:
            color_label = 'Added colors:'
        elif self.coloring_index > 0 and color_delta < 0:
            color_label = 'Removed colors:'
        elif self.coloring_index == 0:
            color_label = 'Initial colors:'
        else:
            color_label = 'No change in colors'
        color_extents = self.GetFullTextExtent(color_label)
        # Add enough room for the color label
        legend_width += color_extents[0] + margin
        # Add enough room for the color boxes
        color_box_size = legend_height - 2 * margin
        color_box_x = legend_width
        color_box_y = margin
        safe_legend_width = legend_width
        legend_width += (color_box_size + margin) * abs(color_delta)
        # The color boxes can be very numerous; wrap if necessary
        try:
            size = dc.GetSize()
        except wx._core.PyAssertionError:
            # This happens on startup before the window is drawn, because it
            # has no size yet.  Set a fake size to make the rest of the code
            # here happy
            size = (1, 1)
        legend_height += (color_box_size + margin) * (legend_width // size[0])
        legend_width = min(legend_width, size[0] - 1)

        # Draw a background for the legend
        dc.SetPen(wx.Pen(wx.BLACK, 2))
        dc.DrawRectangle(1, 1, legend_width, legend_height)

        # Draw contents of the legend
        dc.DrawText(step_label, margin, margin)
        dc.DrawLine(separator_x, 10, separator_x, color_box_size + 2*margin - 10)
        dc.DrawText(color_label, separator_x + margin, margin)
        for color in color_set ^ previous_color_set:
            rgb = [int(channel * 255) for channel in
                    self.palette[color%len(self.palette)]]
            dc.SetBrush(wx.Brush(wx.Colour(rgb[0], rgb[1], rgb[2])))
            dc.DrawRectangle(color_box_x, color_box_y, color_box_size,
                    color_box_size)
            color_box_x += color_box_size + margin
            # If we've gone too wide, wrap
            if color_box_x + color_box_size > size[0]:
                color_box_x = margin
                color_box_y += color_box_size + margin

    def set_graph(self, graph, colorings, palette_name='brewer'):
        """Set the graph to display"""
        self.coloring_index = 0
        self.zoomer = self.zoom_factory(self.axes, base_scale=1.5)

        self.graph = graph
        self.palette = load_palette(palette_name)
        self.colorings = colorings
        self.mapped_colorings = map_colorings(self.palette, self.colorings)
        self.graph_layout(0)

        self.update_graph_display(reset_zoom=True)

    def graph_layout(self, seed=None):
        """Compute a layout of the graph, with an optional seed"""
        if seed is not None:
            random.seed(seed)
        self.layout = nx.spring_layout(self.graph)

    def update_graph_display(self, reset_zoom=False):
        """Compute a layout of the graph, with an optional seed"""
        # Save zoom level, etc.
        if not reset_zoom:
            cur_xlim = self.axes.get_xlim()
            cur_ylim = self.axes.get_ylim()
        self.axes.clear()
        # Restore zoom level, etc.
        if not reset_zoom:
            self.axes.set_xlim(cur_xlim)
            self.axes.set_ylim(cur_ylim)
        self.axes.set_axis_bgcolor((.8,.8,.8))
        nx.draw_networkx(self.graph, self.layout, ax=self.axes,
                         node_color=self.mapped_colorings[self.coloring_index],
                         with_labels=True)
        # Redraw
        self.canvas.Refresh()

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
        self.graphs = []
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

    def set_graph(self, graph, pattern, coloring, palette_name='brewer'):
        """Set the graph to display"""
        self.graph_index = 0
        self.zoomer = self.zoom_factory(self.axes, base_scale=1.5)
        self.pattern = pattern

        self.graph = graph
        self.palette = load_palette(palette_name)
        self.coloring = coloring
        self.mapped_coloring = map_coloring(self.palette, self.coloring)

        self.DG = DecompositionGenerator( self.graph, self.coloring )

        self.components = []
        self.layouts = []
        
        self.color_sets = self.DG.four_color_sets(set(self.coloring), len(pattern))

        for cs in self.color_sets:
            cc_list = self.DG.get_connected_components(cs)
            self.components.append(cc_list)
            # print '\n\nColor set:', cs
            # print 'Mapped color set:', [self.palette[c] for c in cs]
            self.layouts.append(self.DG.get_tree_layouts(cc_list, self.coloring))
            # for cc in cc_list:
            #     print '\nNodes:', cc.nodes()
            #     print 'Edges:', cc.edges()
            #     print 'Coloring:', [self.coloring[node] for node in cc.nodes()]

        self.update_graph_display()

    def update_graph_display(self):
        self.axes.clear()
        self.axes.set_axis_bgcolor((.8,.8,.8))
        for cc, layout in zip(self.components[self.graph_index],
                              self.layouts[self.graph_index]):
            comp_colors = [self.mapped_coloring[node] for node in cc.nodes()]
            nx.draw_networkx(cc, layout, ax=self.axes, node_color=comp_colors,
                             with_labels=True)
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
