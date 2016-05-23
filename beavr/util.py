#
# This file is part of BEAVr, https://github.com/theoryinpractice/beavr/, and is
# Copyright (C) North Carolina State University, 2016. It is licensed under
# the three-clause BSD license; see LICENSE.
#

import pkg_resources

def load_palette(palette_filename):
    """Load colors from palette, map colorings to palette colors"""
    palette = []
    with pkg_resources.resource_stream(__name__,
            'data/palettes/'+palette_filename) as palette_file:
        for line in palette_file:
            line = line.strip()
            if '#' not in line and ',' in line:
                palette.append([int(c)/255.0 for c in line.split(',')])
    return palette


def resource_filename(name):
    """Return a filename of a resource from the beavr package"""
    return pkg_resources.resource_filename(__name__, name)


def map_colorings(palette, colorings):
    """Map list of colorings to palette RGB colors"""
    mapped_colorings = []
    for coloring in colorings:
        mapped_colorings.append(map_coloring(palette, coloring))
    return mapped_colorings


def map_coloring(palette, coloring):
    """Map coloring to palette RGB colors"""
    mapped_coloring = []
    for color in coloring:
        mapped_coloring.append(palette[color%len(palette)])
    return mapped_coloring


def choose(n, m):
    """ Choose m elements from n elements """
    assert n >= m, "Cannot choose {0} elements from {1}".format(m, n)
    result = 1
    for n_i, m_i in zip(range(n, m, -1), range(1, m+1)):
        result *= n_i
        result /= m_i
    return result
