# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module
from __future__ import generator_stop
from __future__ import annotations

from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem, QWidget
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QPainterPath, QPen, QPixmap

from cynodegraph.core import datastructures as ds
from cynodegraph.core import logparams



class GraphicsGUIFeedbackPopup(QGraphicsItem):
    """The graphical representation of the GUIFeedbackPopup tool.

    Attributes:
        text (str): The string to be displayed in the guifeedback by
            default. Default is None.
        parent (QWidget): The parent QWidget of the popup graphic.

    Todo:
        * Make the parameters of the guifeedback(height, width, etc) dynamic.
        * Maybe: Make guifeedback auto-resizing.
    """

    def __init__(self, text: str=None, parent: QWidget=None):
        """Inits the components needed for the guifeedback popup graphic."""
        super().__init__(parent)

        self.__height: int = 240
        self.__width: int = 180
        self.__edge_roundness: float = 10.0
        self.__edge_padding: float = 20.0

        self.__character_max_width: int = 18 # not used for now

        self.__text: str = text
        self.__text_horizontal_padding: float = 4.0
        self.__text_vertical_padding: float = 4.0
        self.__text_item: QGraphicsTextItem = QGraphicsTextItem(self)

        # icons
        self.__icons: QPixmap = QPixmap("icons/status_icons.png")
        self.__icon_offset: float = 0.0

        # TODO: temp solution to guifeedback autosizing
        self.guifeedback_dimensions: ds.Point = ds.Point(180, 50)

        self.hide()
        self.show()

        # create components
        self.__calculate_text_dimensions()
        self.__set_colors()
        self.__set_guifeedback_text_item()


    def __calculate_text_dimensions(self):
        """(Not used yet) Designed to make popup size dynamic based on content.
        """
        # TODO: make dynamic and not static set
        self.__width = self.guifeedback_dimensions.x
        self.__height = self.guifeedback_dimensions.y

    def __set_colors(self):
        """Rather than convolute the __init__, do the brush, pen and
        colors here.
        """
        # text font and color
        self.__text_color = Qt.white
        self.__text_font = QFont("Monospace", 9)
        self.__text_font.setBold(False)

        # color to use for the outline
        self.__color = QColor("#7F000000")

        # outline pens
        self.__pen_default = QPen(self.__color)
        self.__pen_default.setWidthF(1.0)

        # background brushes
        self.__brush_background = QBrush(QColor("#D3212121"))

    def __set_guifeedback_text_item(self):
        """Rather than convolute the __init__, set the popup text here.
        """
        self.__text_item.setDefaultTextColor(self.__text_color)
        self.__text_item.setFont(self.__text_font)
        self.__text_item.setPos(self.__text_horizontal_padding, 0)
        self.__text_item.setTextWidth(
            self.__width - (2 * self.__text_horizontal_padding)
        )
        self.__text_item.setPlainText(self.__text)


    @property
    def text(self):
        """str: The popup's current info text.

        Setter: Sets the new string as the popup's info text.
        """
        return self.__text

    @text.setter
    def text(self, value):
        self.__text = value
        self.__calculate_text_dimensions()
        self.__text_item.setTextWidth(
            self.__width - (2 * self.__text_horizontal_padding)
        )
        self.__text_item.setPlainText(self.__text)

    @property
    def icon_offset(self):
        """float: Returns the selected icons offset value in the sprite
        sheet.

        Setter: Sets an offset for the desired icon in the spritesheet.
        """
        return self.__icon_offset

    @icon_offset.setter
    def icon_offset(self, value):
        self.__icon_offset = value


    # Overloaded Methods
    # ------------------

    # pylint: disable=invalid-name
    # Reasoning: PyQt boundingRect overloaded method requires the
    # camel case.
    def boundingRect(self):
        """Returns the bounding rectangle of the GraphicsGUIFeedbackPopup.

        Returns:
            QRect: The Qt bounding rectangle.
        """
        return QRectF(
            0,
            0,
            self.__width,
            self.__height
        ).normalized()

    # pylint: disable=unused-argument
    # Reasoning: PyQt painter overloaded method requires it.
    # pylint: disable=invalid-name
    # Reasoning: PyQt painter overloaded method requires the camel case.
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        """Overloaded QWidget paint method.

        Draws the GUIFeedbackPopup on the scene.

        Args:
            painter: QWidget painter class.
            QStyleOptionGraphicsItem: ??? (not used).
            widget: The parent widget if there is one(not used).

        Todo:
            * Find out what QStyleOptionGraphicsItem is for.
        """
        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(0, 0, self.__width, self.__height, self.__edge_roundness, self.__edge_roundness)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.__brush_background)
        painter.drawPath(path_content.simplified())

        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.__width, self.__height, self.__edge_roundness, self.__edge_roundness)
        # 9pt = 9px
        # px max of 188 (188 - padding[8] = 180)
        painter.setBrush(Qt.NoBrush)

        painter.setPen(self.__pen_default)
        painter.drawPath(path_outline.simplified())

        # paint icon
        painter.drawPixmap(
            QRectF(-12.5, -12.5, 24.0, 24.0),
            self.__icons,
            QRectF(self.__icon_offset, 0, 24.0, 24.0)
        )
