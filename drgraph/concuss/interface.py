from drgraph.interface import StageInterface

class ColorInterface(StageInterface):
    """GUI elements for CONCUSS coloring stage visualization"""

    def __init__(self):
        """Fill the empty GUI elements with coloring-specific widgets"""
        super(ColorInterface, self).__init__()

class DecomposeInterface(StageInterface):
    """GUI elements for CONCUSS decomposition stage visualization"""

    def __init__(self):
        """Fill the empty GUI elements with decomposition-specific widgets"""
        super(DecomposeInterface, self).__init__()

class CountInterface(StageInterface):
    """GUI elements for CONCUSS counting stage visualization"""

    def __init__(self):
        """Fill the empty GUI elements with counting-specific widgets"""
        super(CountInterface, self).__init__()

class CombineInterface(StageInterface):
    """GUI elements for CONCUSS combination stage visualization"""

    def __init__(self):
        """Fill the empty GUI elements with combination-specific widgets"""
        super(CombineInterface, self).__init__()
