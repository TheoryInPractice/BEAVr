def load_palette(palette_filename):
    """Load colors from palette, map colorings to palette colors"""
    palette = []
    with open('data/palettes/'+palette_filename) as palette_file:
        for line in palette_file:
            line = line.strip()
            if '#' not in line and ',' in line:
                palette.append([int(c)/255.0 for c in line.split(',')])
    return palette

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