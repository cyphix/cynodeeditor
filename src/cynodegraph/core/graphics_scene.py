# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module
from __future__ import generator_stop
from __future__ import annotations

import math

from PyQt5.QtWidgets import QGraphicsScene, QWidget
from PyQt5.QtCore import pyqtSignal, QLine
from PyQt5.QtGui import QColor, QPen

from cynodegraph.core import node_scene
from cynodegraph.core import guifeedback



class NodeEditorGraphicsScene(QGraphicsScene):
    """The graphical scene object on which to draw the node graph and
    components.

    Args:
        scene (Scene): Reference to Scene object that this is the child of.
        parent (QWidget): The parent QWidget of the scene graphic.

    Attributes:
        scene (Scene): Reference to Scene object that this is the child of.
        grid_size (int): The graphical size of a grid square in pixels.
        grid_squares (int): The width/height of grid squares that make up
            a bigger grid square.
        guifeedback (GUIFeedbackPopup): The persistant GUIFeedbackPopup
            object for the scene.
    """

    # pyqtSignal emitted when some item is selected in the `Scene`
    item_selected = pyqtSignal()
    # pyqtSignal emitted when items are deselected in the `Scene`
    items_deselected = pyqtSignal()

    # pylint: disable=too-many-instance-attributes
    # Reasoning: All the attributes are needed and used.
    def __init__(self, scene: node_scene.Scene, parent: QWidget=None):
        """Inits the components needed for the scene graphic."""
        super().__init__(parent)

        self.scene: node_scene.Scene = scene

        # settings
        self.grid_size: int = 20
        self.grid_squares: int = 5

        # create guifeedback item
        self.guifeedback: guifeedback.GUIFeedbackPopup = guifeedback.GUIFeedbackPopup(self)

        self.__set_colors()


    def __set_colors(self):
        """Rather than convolute the __init__, do the brush, pen and
        colors here.
        """
        # create pens and brushes
        self._color_background: QColor = QColor("#393939")
        self._color_light: QColor = QColor("#2f2f2f")
        self._color_dark: QColor = QColor("#292929")

        self._pen_light: QPen = QPen(self._color_light)
        self._pen_light.setWidth(1)
        self._pen_dark: QPen = QPen(self._color_dark)
        self._pen_dark.setWidth(2)
        self.setBackgroundBrush(self._color_background)


    def set_scene(self, width: int, height: int):
        """Set the scene's size.

        Args:
            width (int): The scene's width in pixels.
            height (int): The scene's height in pixels.
        """
        self.setSceneRect(-width//2, -height//2, width, height)


    # Overloaded Methods
    # ------------------

    # pylint: disable=invalid-name
    # Reasoning: PyQt mouseReleaseEvent overloaded method requires the
    # camel case.
    def dragMoveEvent(self, event):
        """The drag events won't be allowed until dragMoveEvent is overriden. Otherwise unused.

        Todo:
            * Find out if there is a more elegant way to do this.
        """
        pass

    # pylint: disable=unused-argument
    # Reasoning: PyQt drawBackground overloaded method requires it.
    # pylint: disable=invalid-name
    # Reasoning: PyQt drawBackground overloaded method requires the camel case.
    def drawBackground(self, painter, rect):
        """Overloaded QGraphicsScene draw method.

        Draws the grid lines and background color of the scene.

        Args:
            painter: QWidget painter class.
            rect: The rectagle which contains the positions for the scene.
        """
        super().drawBackground(painter, rect)

        # create grid
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.grid_size)
        first_top = top - (top % self.grid_size)

        # compute the lines to be drawn
        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.grid_size):
            if x % (self.grid_size*self.grid_squares) != 0:
                lines_light.append(QLine(x, top, x, bottom))
            else:
                lines_dark.append(QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.grid_size):
            if y % (self.grid_size*self.grid_squares) != 0:
                lines_light.append(QLine(left, y, right, y))
            else:
                lines_dark.append(QLine(left, y, right, y))


        # draw the lines
        painter.setPen(self._pen_light)
        painter.drawLines(*lines_light)

        painter.setPen(self._pen_dark)
        painter.drawLines(*lines_dark)
