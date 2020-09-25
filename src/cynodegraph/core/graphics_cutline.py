# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module
from __future__ import generator_stop
from __future__ import annotations

from typing import List

from PyQt5.QtWidgets import QGraphicsItem, QWidget
from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QPainter, QPainterPath, QPen, QPolygonF



class CutLine(QGraphicsItem):
    """The graphical representation of the Edge cut-line tool.

    Args:
        parent (QWidget): The parent QWidget of the cutline graphic.

    Attributes:
        line_points (List[QPointF]): The list of the cut-line's connecting
            points.

    Todo:
        * Find out what QStyleOptionGraphicsItem is for.
    """

    def __init__(self, parent: QWidget=None):
        """Inits the components needed for the cut-line graphic."""
        super().__init__(parent)

        self.line_points: List[QPointF] = []

        self.__pen: QPen = QPen(Qt.white)
        self.__pen.setWidthF(2.0)
        self.__pen.setDashPattern([3, 3])

        self.setZValue(2)

    def shape(self) -> QPainterPath:
        """Returns the cut-line's QPainterPath.

        Returns:
            QPainterPath: The edge's line path object.
        """
        if len(self.line_points) > 1:
            path = QPainterPath(self.line_points[0])
            for point in self.line_points[1:]:
                path.lineTo(point)
        else:
            path = QPainterPath(QPointF(0,0))
            path.lineTo(QPointF(1,1))

        return path


    # Overloaded Methods
    # ------------------

    # pylint: disable=invalid-name
    # Reasoning: PyQt boundingRect overloaded method requires the
    # camel case.
    def boundingRect(self) -> QRectF:
        """Returns the bounding rectangle of the cut-line.

        Returns:
            QRect: The QGraphicsItem's bounding rectangle.
        """
        return self.shape().boundingRect()

    # pylint: disable=unused-argument
    # Reasoning: PyQt painter overloaded method requires it.
    # pylint: disable=invalid-name
    # Reasoning: PyQt painter overloaded method requires the camel case.
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        """Overloaded QWidget paint method.

        Draws the cut-line on the GraphicsScene.

        Args:
            painter: QWidget painter class.
            QStyleOptionGraphicsItem: ??? (not used).
            widget: The parent widget if there is one(not used).

        Todo:
            * Find out what QStyleOptionGraphicsItem is for.
        """
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self.__pen)

        poly = QPolygonF(self.line_points)
        painter.drawPolyline(poly)
