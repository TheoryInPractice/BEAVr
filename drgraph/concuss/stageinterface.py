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
        self.vis.update_graph_display(reset_zoom=True)


class DecomposeInterface(StageInterface):
    """GUI elements for CONCUSS decomposition stage visualization"""

    name = "Decompose"

    def __init__(self, parent):
        """Fill the empty GUI elements with decomposition-specific widgets"""
        super(DecomposeInterface, self).__init__(parent)

        # Set one button
        one_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR,
                self.tb_size)
        one = self.tb.AddLabelTool(wx.NewId(), "Forward", one_bmp)
        self.Bind(wx.EVT_TOOL, self.on_one, one)

        # Set two button
        two_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR,
                self.tb_size)
        two = self.tb.AddLabelTool(wx.NewId(), "Backward", two_bmp)
        self.Bind(wx.EVT_TOOL, self.on_two, two)

        # Set three button
        three_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR,
                self.tb_size)
        three = self.tb.AddLabelTool(wx.NewId(), "Backward", three_bmp)
        self.Bind(wx.EVT_TOOL, self.on_three, three)

        # Set four button
        four_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR,
                self.tb_size)
        four = self.tb.AddLabelTool(wx.NewId(), "Backward", four_bmp)
        self.Bind(wx.EVT_TOOL, self.on_four, four)

        self.tb.AddSeparator()

        self.tb.Realize()

        vis = DecomposeVisualizer(self)
        self.set_visualization(vis)

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
                    self.color_palette[color%len(self.color_palette)]]
            dc.SetBrush(wx.Brush(wx.Colour(rgb[0], rgb[1], rgb[2])))
            dc.DrawRectangle(color_box_x, color_box_y, color_box_size,
                    color_box_size)
            color_box_x += color_box_size + margin
            # If we've gone too wide, wrap
            if color_box_x + color_box_size > size[0]:
                color_box_x = margin
                color_box_y += color_box_size + margin

    def set_graph(self, graph, colorings, palette='brewer'):
        """Set the graph to display"""
        self.coloring_index = 0
        self.zoomer = self.zoom_factory(self.axes, base_scale=1.5)

        self.graph = graph
        self.palette = palette
        self.colorings = colorings
        self.map_colorings()
        self.graph_layout(0)

        self.update_graph_display(reset_zoom=True)

    def map_colorings(self):
        """Load colors from palette, map colorings to palette colors"""
        self.color_palette = []
        with open('data/palettes/'+self.palette) as palette_file:
            for line in palette_file:
                line = line.strip()
                if '#' not in line and ',' in line:
                    self.color_palette.append(
                            [int(c)/255.0 for c in line.split(',')])
        if len(self.colorings) == 1:
            self.mapped_colorings = [self.color_palette[self.colorings[0]]]
        else:
            mapped_colorings = []
            for coloring in self.colorings:
                mapped_coloring = []
                for color in coloring:
                    mapped_coloring.append(self.color_palette[color%len(self.color_palette)])
                mapped_colorings.append(mapped_coloring)
            self.mapped_colorings = mapped_colorings

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
                         with_labels=False)
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

    def set_graph(self, graph, pattern, graphs, colorings, palette='brewer'):
        """Set the graph to display"""
        self.graph_index = 0
        self.zoomer = self.zoom_factory(self.axes, base_scale=1.5)
        self.pattern = pattern

        self.graph = graph
        self.graphs = graphs
        self.palette = palette
        self.colorings = colorings
        self.map_colorings()
        self.graph_layout()

        self.update_graph_display()

    def map_colorings(self):
        """Load colors from palette, map colorings to palette colors"""
        self.color_palette = []
        with open('data/palettes/'+self.palette) as palette_file:
            for line in palette_file:
                line = line.strip()
                if '#' not in line and ',' in line:
                    self.color_palette.append(
                            [int(c)/255.0 for c in line.split(',')])
        if len(self.colorings) == 1:
            self.mapped_colorings = [self.color_palette[self.colorings[0]]]
        else:
            mapped_colorings = []
            for coloring in self.colorings:
                mapped_coloring = []
                for color in coloring:
                    mapped_coloring.append(self.color_palette[color%len(self.color_palette)])
                mapped_colorings.append(mapped_coloring)
            self.mapped_colorings = mapped_colorings

    def graph_layout(self):
        """Compute a layout of the graph, with an optional seed"""
        # Compute tree layouts for each connected component
        layouts = []
        for sub in nx.connected_component_subgraphs(self.graphs[self.graph_index]):
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

    def update_graph_display(self):
        """Compute a layout of the graph, with an optional seed"""
        self.axes.clear()
        self.axes.set_axis_bgcolor((.8,.8,.8))
        nx.draw_networkx(self.graphs[self.graph_index], self.grid, ax=self.axes,
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

    def get_connected_components(self, color_set):
        """
        A generator for connected components given a specific color set

        :param color_set: The color set
        :return: A generator for connected components (subgraphs) induced by
                 color_set
        """

        # Make an empty set to store vertices
        vertices = set()

        # Find vertices that are colored with colors in color_set
        for index, color in enumerate(self.colorings[-1]):
            if color in color_set:
                vertices.add(index)

        # # While we have more vertices to look at
        # while vertices:
        #     # Pop a vertex at random and make a set containing that vertex
        #     comp = {vertices.pop()}
        #     # Find its neighbors that are also in 'vertices'
        #     exp = self.neighbors_set(comp) & vertices
        #     # While we have more neighbors
        #     while exp:
        #         # Add those vertices to our component
        #         comp.update(exp)
        #         # Compute new neighbors
        #         exp = self.neighbors_set(comp) & vertices
        #     # We found a component, delete those vertices from original
        #     # set of vertices
        #     vertices = vertices - comp
        #     # Yield the component
        #     yield self.graph.subgraph(comp)

        return nx.connected_component_subgraphs(self.graph.subgraph(vertices))

    def neighbors_set(self, centers):
        """
        Returns all neighbors given a set of vertices

        :param centers: The vertices whose neighbors are sought
        :return: A set containing the neighbors
        """

        res = reduce(lambda x, y: x | self.graph.neighbors(y), centers, set())
        return res - centers

    def get_tree_layouts( self, connected_components, coloring ):
        layouts = []
        for connected_component in connected_components:
            tree = self.get_underlying_tree( connected_component, coloring )
            try:
                # Nice circular layout if you have graphviz
                from networkx import graphviz_layout
                layouts.append( nx.graphviz_layout(tree,prog='twopi',args='') )
            except ImportError:
                # Spring layout if you do not have grahpviz
                layouts.append( nx.spring_layout(tree) )
        return layouts

    def get_underlying_tree( self, connected_component, coloring ):
        # Find the root (color with only one occurrence)
        root = None
        colors = [coloring[node] for node in connected_component.nodes()]
        for index, color in enumerate(colors):
            colors[index] = 'Not a color'
            if color not in colors:
                root = connected_component.nodes()[index]
                break
            colors[index] = color

        # If we can't find a root, something's wrong!
        if root == None:
            print 'WARNING: Coloring this has no root', colors
            return connected_component

        # Create a new NetworkX graph to represent the tree
        tree = nx.Graph()
        tree.add_node( root )

        # Remove the root from the connected component
        connected_component.remove_node( root )

        # Every new connected component is a subtree
        for sub_cc in nx.connected_component_subgraphs( connected_component ):
            subtree = get_underlying_tree( sub_cc, coloring )
            tree = nx.compose( tree, subtree )
            tree.add_edge( root, subtree.root )

        # Root field for use in recursive case to connect tree and subtree
        tree.root = root
        return tree





