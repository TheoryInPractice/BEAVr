from drgraph.interface import StageInterface

class ColorInterface(StageInterface):
    """GUI elements for CONCUSS coloring stage visualization"""

    def __init__(self, parent):
        """Fill the empty GUI elements with coloring-specific widgets"""
        super(ColorInterface, self).__init__(parent)

class DecomposeInterface(StageInterface):
    """GUI elements for CONCUSS decomposition stage visualization"""

    def __init__(self, parent):
        """Fill the empty GUI elements with decomposition-specific widgets"""
        super(DecomposeInterface, self).__init__(parent)

class CountInterface(StageInterface):
    """GUI elements for CONCUSS counting stage visualization"""

    def __init__(self, parent):
        """Fill the empty GUI elements with counting-specific widgets"""
        super(CountInterface, self).__init__(parent)

class CombineInterface(StageInterface):
    """GUI elements for CONCUSS combination stage visualization"""

    def __init__(self, parent):
        """Fill the empty GUI elements with combination-specific widgets"""
        super(CombineInterface, self).__init__(parent)
