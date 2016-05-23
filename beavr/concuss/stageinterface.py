#
# This file is part of BEAVr, https://github.com/theoryinpractice/beavr/, and is
# Copyright (C) North Carolina State University, 2016. It is licensed under
# the three-clause BSD license; see LICENSE.
#

import math
import os
import os.path as path

import wx
from wx.lib.scrolledpanel import ScrolledPanel
from numpy import random, fromstring, uint8
import networkx as nx
import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from beavr.stageinterface import StageInterface, StageVisualizer, MatplotlibVisualizer
from beavr.concuss.visualizerbackend import DecompositionGenerator, CombineSetGenerator, CountGenerator
from beavr.util import load_palette, map_coloring, map_colorings, choose

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

        self.pattern = pattern

        vis = DecomposeVisualizer(self, len(pattern.nodes()))
        self.set_visualization(vis)
        self.vis.set_graph(graph, coloring)

        # Mapping from button IDs to colors
        self.id_color_mapping = {}
        # The current color set
        self.color_set = set()
        # Add buttons for all our colors
        for color in set(coloring):
            new_id = wx.NewId()
            self.id_color_mapping[new_id] = color
            bmp = self.color_icon(color)
            btn = self.tb.AddCheckLabelTool(new_id, "Color {0}".format(color),
                    bmp)
            self.Bind(wx.EVT_TOOL, self.on_color_tool, btn)

        self.tb.Realize()

    def color_icon(self, color):
        """Create an icon for the given color"""
        # Create the bitmap
        icon = wx.EmptyBitmap(*self.tb_size)
        # Create a DC to draw on the bitmap
        dc = wx.MemoryDC()
        dc.SelectObject(icon)
        dc.Clear()
        # Draw on the bitmap using the DC
        dc.SetPen(wx.Pen(wx.BLACK, 1))
        # Prepare to draw in the right color
        rgb = [int(channel * 255) for channel in
                self.vis.palette[color%len(self.vis.palette)]]
        dc.SetBrush(wx.Brush(wx.Colour(*rgb)))
        # Draw the square
        dc.DrawRectangle(5, 5, self.tb_size[0]-10, self.tb_size[1]-10)
        # Select the null bitmap to flush all changes to icon
        dc.SelectObject(wx.NullBitmap)
        # Make the white parts of the icon transparent
        mask = wx.Mask(icon, wx.WHITE)
        icon.SetMask(mask)
        return icon

    def on_color_tool(self, e):
        """Add or remove the selected color from the current set"""
        # Get the color corresponding to the button that was clicked
        color = self.id_color_mapping[e.GetId()]
        # Add or remove the color from the color set
        self.color_set ^= {color}
        # Update the graph display
        self.vis.update_graph_display(self.color_set)


class CountInterface(StageInterface):
    """GUI elements for CONCUSS counting stage visualization"""

    name = "Count"

    def __init__(self, parent, graph, pattern, tdd, dptable, coloring):
        """Fill the empty GUI elements with counting-specific widgets"""
        super(CountInterface, self).__init__(parent)

        # Random Layout buton
        tali_path = path.join(os.getcwd(), 'data', 'icons', 'tali.png')
        rand_bmp = wx.Bitmap(tali_path, wx.BITMAP_TYPE_PNG)
        rand = self.tb.AddLabelTool(wx.NewId(), "Random Patterns", rand_bmp)
        self.Bind(wx.EVT_TOOL, self.on_random, rand)

        self.tb.Realize()

        vis = CountVisualizer(self, graph, pattern, tdd, dptable, coloring)
        self.set_visualization(vis)

    def on_random(self, e):
        """Choose a new set of patterns for display"""
        self.vis.randomize_patterns()
        self.vis.update_graph_display()


class CombineInterface(wx.Panel):
    """GUI elements for CONCUSS combination stage visualization"""

    name = "Combine"

    def __init__(self, parent, pattern, colorings, colors, min_size, counts_per_colorset):
        """Fill the empty GUI elements with combination-specific widgets"""
        super(CombineInterface, self).__init__(parent)

        self.pattern = pattern
        self.pattern_size = self.pattern.number_of_nodes()
        self.colorings = colorings
        self.colors = colors
        self.min_size = min_size
        self.counts_per_colorset = counts_per_colorset

        # Make the sizer
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Add the ListBook
        self.listbook = wx.Listbook(self, wx.NewId(), style=wx.BK_TOP)
        self.sizer.Add(self.listbook, 1, wx.EXPAND)
        
        # Add a tab for each coloring
        self.add_tabs()

        # We want to see what's in the sizer
        self.SetSizer(self.sizer)

    def add_tabs(self, palette_name='brewer'):
        """Add a new tab to the Listbook with an appropriate label"""
        self.palette = load_palette(palette_name)
        self.mapped_colorings = map_colorings(self.palette, self.colorings)
        self.pos = None
        icons = [self.get_icon(coloring) for coloring in self.mapped_colorings]
        icons.append(self.get_total_icon())
        il = wx.ImageList(self.w, self.h)
        self.add_image_list(icons)
        # Add coloring tabs
        for i in range(len(icons)-1):
            tab = CombinePage(self, -1, set(self.colorings[i]), self.colors,
                              self.pattern_size, self.min_size)
            self.listbook.AddPage(tab, '', imageId=i)
        # Add total tab
        tab = CombinePage(self, -1, self.colors, self.colors, self.pattern_size,
                          self.min_size, self.counts_per_colorset, is_totals_page=True)
        self.listbook.AddPage(tab, '', imageId=len(icons)-1)

    def add_image_list(self, icons):
        """Take in list of images and assign them to a wx.ImageList"""
        il = wx.ImageList(self.w, self.h)
        for icon in icons:
            il.Add(icon)
        self.listbook.AssignImageList(il)

    def get_icon(self, coloring):
        """Take in NetworkX graph and coloring and create bipmap icon"""
        if self.pos is None:
            self.pos = nx.spring_layout(self.pattern)
        fig = plt.figure(figsize=(1,1))
        axes = plt.Axes(fig, [0,0,1,1])
        axes.set_axis_off()
        fig.add_axes(axes)
        nx.draw(self.pattern, pos=self.pos, ax=axes, node_color=coloring)
        canvas = fig.canvas
        canvas.draw()
        s = canvas.tostring_rgb()

        l,b,w,h = fig.bbox.bounds
        self.w = int(w)
        self.h = int(h)
        X = fromstring(s, uint8)

        icon = wx.BitmapFromBuffer(self.w,self.h,X)
        plt.close()
        return icon

    def get_total_icon(self):
        icon = wx.EmptyBitmap(self.w,self.h)
        dc = wx.MemoryDC()
        dc.SelectObject(icon)
        dc.Clear()
        dc.SetFont(self.GetFont().Scaled(4))
        text= 'Total'
        tw, th = dc.GetTextExtent(text)
        dc.DrawText(text, (self.w-tw)/2, (self.h-th)/2)
        dc.SelectObject(wx.NullBitmap)
        return icon


class ColorVisualizer(MatplotlibVisualizer):
    """The visualization for the CONCUSS coloring stage"""

    def __init__(self, parent):
        """Create the CONCUSS coloring visualization"""
        super(ColorVisualizer, self).__init__(parent)

        self.graph = nx.Graph()
        self.layout = []

        self.canvas.Bind(wx.EVT_PAINT, self.on_paint)

    def on_paint(self, evt):
        """Draw a legend in the top-left corner of the graph display"""
        dc = super(ColorVisualizer, self).on_paint(evt)

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
                         with_labels=False)
        # Redraw
        self.canvas.Refresh()


class DecomposeVisualizer(MatplotlibVisualizer):
    """The visualization for the CONCUSS decompose stage"""

    def __init__(self, parent, p):
        """Create the CONCUSS decompose visualization"""
        super(DecomposeVisualizer, self).__init__(parent)

        self.parent = parent
        self.graph = nx.Graph()
        self.p = p

        self.canvas.Bind(wx.EVT_PAINT, self.on_paint)

    def on_paint(self, evt):
        """Draw a legend in the top-left corner of the graph display"""
        dc = super(DecomposeVisualizer, self).on_paint(evt)

        # Calculate the size of the legend
        legend_height = 40  # Should be big enough
        legend_width = 0
        # Text size
        cs_label = 'Color set:'
        cs_extents = self.GetFullTextExtent(cs_label)
        margin = (legend_height - cs_extents[1]) / 2
        # Add enough width for the text
        legend_width += 2 * margin + cs_extents[0]
        # Add enough width for the colors
        color_set = set(self.parent.color_set)
        # Add enough room for the color boxes
        color_box_size = legend_height - 2 * margin
        color_box_x = legend_width
        color_box_y = margin
        safe_legend_width = legend_width
        legend_width += (color_box_size + margin) * len(color_set)
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
        # Pink if we have too many colors
        if len(self.parent.color_set) > self.p:
            bgcolor = '#ffcccc'
        # White if we don't have too many
        else:
            bgcolor = '#ffffff'
        dc.SetBrush(wx.Brush(bgcolor, wx.SOLID))
        # Now that we're done setting things up, draw it
        dc.DrawRectangle(1, 1, legend_width, legend_height)

        # Draw contents of the legend
        dc.DrawText(cs_label, margin, margin)
        for color in color_set:
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

    def set_graph(self, graph, coloring, palette_name='brewer'):
        """Set the graph to display"""

        self.graph = graph
        self.palette = load_palette(palette_name)
        self.coloring = coloring
        self.mapped_coloring = map_coloring(self.palette, self.coloring)

        self.DG = DecompositionGenerator(self.graph, self.coloring)

        self.update_graph_display(set())

    def update_graph_display(self, color_set):
        """Update the displayed graph"""
        # Compute what we need for the current color set
        cc_list = self.DG.get_connected_components(color_set)
        layouts = self.DG.get_tree_layouts(cc_list
            , self.coloring)
        # Draw the graph
        self.axes.clear()
        self.axes.set_axis_bgcolor((.8,.8,.8))
        for cc, layout in zip(cc_list, layouts):
            comp_colors = [self.mapped_coloring[node] for node in cc.nodes()]
            if cc.occ == 1:
                nx.draw_networkx(cc, layout, ax=self.axes, node_color=comp_colors,
                                 with_labels=False)
            else:
                nx.draw_networkx(cc, layout, ax=self.axes, node_color=comp_colors,
                                 labels={cc.nodes()[0]:cc.occ})
        self.canvas.Refresh()


class CountVisualizer(MatplotlibVisualizer):
    """The visualization for the CONCUSS count stage"""

    def __init__(self, parent, graph, pattern, tdd, dptable, coloring,
            palette_name='brewer'):
        """Create the CONCUSS count visualization"""
        super(CountVisualizer, self).__init__(parent)

        self.parent = parent
        self.coloring = coloring
        self.graph = graph
        self.pattern = pattern
        self.tdd = tdd
        self.dptable = dptable

        self.colorset = [self.coloring[node] for node in self.tdd.nodes()]
        self.CG = CountGenerator(self.graph, self.pattern, self.tdd,
                self.dptable, self.coloring, palette_name)
        self.canvas.Bind(wx.EVT_PAINT, self.on_paint)
        self.update_graph_display()

    def randomize_patterns(self):
        """Select a new, random set of patterns to display"""
        self.CG.get_patterns()

    def update_graph_display(self):
        self.axes.clear()
        self.axes.set_axis_bgcolor((.8,.8,.8))

        graph_attributes = self.CG.get_attributes()
        for attributes in graph_attributes:
            nx.draw_networkx(self.pattern, ax=self.axes, **attributes[0])
            for attribute in attributes[1:]:
                nx.draw_networkx(self.graph, ax=self.axes, **attribute)

        self.canvas.Refresh()

    def on_paint(self, evt):
        """Draw a legend in the top-left corner of the graph display"""
        dc = super(CountVisualizer, self).on_paint(evt)

        # Calculate the size of the legend
        legend_height = 40  # Should be big enough
        legend_width = 0
        # Text size
        cs_label = 'Color set:'
        cs_extents = self.GetFullTextExtent(cs_label)
        margin = (legend_height - cs_extents[1]) / 2
        # Add enough width for the text
        legend_width += 2 * margin + cs_extents[0]
        # Add enough width for the colors
        color_set = set(self.colorset)
        # Add enough room for the color boxes
        color_box_size = legend_height - 2 * margin
        color_box_x = legend_width
        color_box_y = margin
        safe_legend_width = legend_width
        legend_width += (color_box_size + margin) * len(color_set)
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
        dc.SetBrush(wx.Brush('#ffffff', wx.SOLID))
        # Now that we're done setting things up, draw it
        dc.DrawRectangle(1, 1, legend_width, legend_height)

        # Draw contents of the legend
        dc.DrawText(cs_label, margin, margin)
        for color in color_set:
            rgb = [int(channel * 255) for channel in
                    self.CG.palette[color%len(self.CG.palette)]]
            dc.SetBrush(wx.Brush(wx.Colour(rgb[0], rgb[1], rgb[2])))
            dc.DrawRectangle(color_box_x, color_box_y, color_box_size,
                    color_box_size)
            color_box_x += color_box_size + margin
            # If we've gone too wide, wrap
            if color_box_x + color_box_size > size[0]:
                color_box_x = margin
                color_box_y += color_box_size + margin


class CombinePage(wx.Panel):
    """
    A single page of the CombineInterface's Listbook

    It is very important that this is a wx.Panel with a sizer which contains
    the ScrolledPanel.  Otherwise, the ScrolledPanel will not have a scroll
    bar, though it is still possible to scroll using the scroll wheel.
    """

    def __init__(self, parent, id, color_set, colors, pattern_size, min_size, counts_per_colorset=None,
                 is_totals_page=False):
        super(CombinePage, self).__init__(parent, id)

        outersizer = wx.BoxSizer(wx.VERTICAL)
        self.scrolledpanel = ScrolledPanel(self, -1, style=wx.TAB_TRAVERSAL)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Display a max of 100 color sets for each set size
        max_sets_coef = 100/math.log(pattern_size)
        count_by_size = {}

        # compute inclusion exclusion coefficients
        in_ex = []
        for n_colors in range(pattern_size, -1, -1):
            # For inclusion/exclusion principle, we either need to add or
            # subtract the count for a specific set of colors in order to avoid
            # double counting. We count the number of times a color combination
            # of size numColors was counted in the color combinations of size
            # greater than numColors and adjust our count accordingly.
            discrepancy = pattern_size - n_colors
            remaining_colors = len(colors) - n_colors
            in_ex_modifier = 1 - sum([choose(remaining_colors, discrepancy-i) *
                                      mod for i, mod in enumerate(in_ex)])
            in_ex.append(in_ex_modifier)

        # If this is the totals page
        if is_totals_page:
            c_sets_by_size = []
            # Add up counts for each size of color sets
            for c_set, count in counts_per_colorset.iteritems():
                len_c_set = len(c_set)
                if len_c_set in count_by_size:
                    count_by_size[len_c_set] += count
                else:
                    count_by_size[len_c_set] = count
            # Add color sets from CONCUSS's output instead of generating them again
            for i in range(pattern_size, min_size - 1, -1):
                c_sets_by_size.append([set(colorset) for colorset in counts_per_colorset.keys() if len(colorset) == i])

        else:
            self.CSG = CombineSetGenerator(color_set, colors, pattern_size, min_size)
            c_sets_by_size = self.CSG.get_color_sets()

        total = 0
        add = len(c_sets_by_size) % 2 == 1
        for c_sets in c_sets_by_size:
            max_sets = int(max_sets_coef*math.log(len(c_sets[0])))
            inexterm = InExTermWidget(self.scrolledpanel, c_sets, in_ex,
                                      colors, pattern_size, add, max_sets, count_by_size, totals_term=is_totals_page)
            self.sizer.Add(inexterm, 0, wx.EXPAND|wx.BOTTOM, 12)
            total += inexterm.total
            add = not add

        text = wx.StaticText(self.scrolledpanel, -1, 'Final total: ' + str(total))
        modified_font=text.GetFont()
        modified_font.SetPixelSize((20,20))
        modified_font.SetWeight(wx.FONTWEIGHT_BOLD)
        text.SetFont(modified_font)
        self.sizer.Add(text, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_RIGHT, 12)

        self.scrolledpanel.SetSizer(self.sizer)
        self.scrolledpanel.SetAutoLayout(1)
        self.scrolledpanel.SetupScrolling(scroll_x=False)

        outersizer.Add(self.scrolledpanel, 1, wx.EXPAND)
        self.SetSizer(outersizer)


class InExTermWidget(wx.Panel):
    """A GUI widget one term of the inclusion-exclusion equation"""

    def __init__(self, parent, color_sets, in_ex_coefficients, colors, pattern_size,\
                 add, max_sets, counts_per_colorset_size, totals_term=True):
        super(InExTermWidget, self).__init__(parent, -1)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        if not totals_term:
            # Calculate inclusion/exclusion coefficient
            coef = 1
            remaining_colors = len(colors) - len(color_sets[0])
            for i in range(pattern_size-len(color_sets[0]), 0, -1):
                coef += math.factorial(remaining_colors)/ \
                        (math.factorial(i)*math.factorial(remaining_colors-i))
            if not add:
                coef *= -1
        else:
            # Use coefficient from inclusion exclusion table
            coef = in_ex_coefficients[pattern_size - len(color_sets[0])]

        # Add the first text
        coef_str = str(coef)
        if coef >= 0:
            coef_str = '+' + coef_str
        text = wx.StaticText(self, -1, coef_str)
        modified_font = text.GetFont()
        modified_font.SetPixelSize((20,20))
        modified_font.SetWeight(wx.FONTWEIGHT_BOLD)
        text.SetFont(modified_font)
        if coef >= 0:
            text.SetForegroundColour((0, 0, 200))
        else:
            text.SetForegroundColour((200, 0, 0))
        self.sizer.Add(text, 0, wx.LEFT, 12)

        # Now add the count for this size
        if counts_per_colorset_size:
            text_str = u' \u00d7 ' + str(counts_per_colorset_size[len(color_sets[0])])
        else:
            text_str = u' \u00d7 ' + str(len(color_sets))
        text = wx.StaticText(self, -1, text_str, size=(110,20))
        text.SetFont(modified_font)
        self.sizer.Add(text, 0, wx.EXPAND|wx.RIGHT, 12)

        # Add the color set widgets
        self.color_set_sizer = wx.WrapSizer(wx.HORIZONTAL)
        for i in range(min(len(color_sets),max_sets)):
            self.color_set_sizer.Add(ColorSetWidget(self, color_sets[i]), 1,
                    wx.BOTTOM|wx.RIGHT, 12)

        # Add ellipsis if we aren't displaying all of the color sets
        if len(color_sets) > max_sets:
            text = wx.StaticText(self, -1, "...")
            text.SetFont(modified_font)
            self.color_set_sizer.Add(text, 1, wx.BOTTOM|wx.RIGHT, 12)

        self.sizer.Add(self.color_set_sizer, 1, wx.EXPAND)

        # Add the second text
        self.coef = coef

        if totals_term:
            self.total = counts_per_colorset_size[len(color_sets[0])] * coef
        else:
            self.total = len(color_sets)*coef
        text2 = wx.StaticText(self, -1, "= "+str(self.total), size=(70,20))
        text2.SetFont(modified_font)
        self.sizer.Add(text2, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 12)

        # Set the sizer
        self.SetSizer(self.sizer)


class ColorSetWidget(wx.Panel):
    """A GUI widget for one set of colors"""

    def __init__(self, parent, color_set):
        super(ColorSetWidget, self).__init__(parent, style=wx.SIMPLE_BORDER)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.color_set = color_set

        self.palette = load_palette("brewer")
        self.mapped_coloring = map_coloring(self.palette, color_set)

        self.sizer.Add(self.get_color_set_panel())
        self.SetSizer(self.sizer)
        #self.SetBackgroundColour(wx.Colour(0, 255, 0))

    def get_color_set_panel(self):
        set_sizer = wx.BoxSizer(wx.HORIZONTAL)
        for color, bg in zip(self.color_set, self.mapped_coloring):
            color_panel = wx.Panel(self, -1, size=(20,20))
            color_panel.SetBackgroundColour([255 * i for i in bg])
            set_sizer.Add(color_panel)

        return set_sizer
