# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module
from __future__ import generator_stop
from __future__ import annotations

import math

from PyQt5.QtWidgets import QGraphicsItem, QGraphicsPathItem, QWidget
from PyQt5.QtCore import QPointF, QRect, Qt
from PyQt5.QtGui import QColor, QPainterPath, QPen

from cynodegraph.core import datastructures as ds
from cynodegraph.core import logparams
from cynodegraph.core import node_edge
from cynodegraph.core import node_socket



EDGE_TYPE_DIRECT: int = 1
EDGE_TYPE_BEZIER: int = 2
EDGE_CP_ROUNDNESS: int = 100     # bezier controll point distance on the line



class GraphicsEdge(QGraphicsPathItem):
    """The edge's graphical component that actually is drawn on the Scene.

    Args:
        edge (node_edge.Edge): The Edge that this GraphicsEdge belongs to.
        edge_type (int): A value determining the type of line the Edge is.
            EDGE_TYPE_DIRECT or EDGE_TYPE_BEZIER.
        parent (QWidget): The parent QWidget of the cutline graphic.

    Attributes:
        edge (node_edge.Edge): The Edge that this GraphicsEdge belongs to.
        hovered (bool): The current state if the edge is hovered or not.
        pos_source (datastructures.Point): Holds the starting point of the
            edge.
        pos_destination (datastructures.Point): Holds the ending point of
            the edge.
        line_width (float): The default thickness of the drawn line.

    Todo:
        * Re-write of calc_path() severely needed.
        * Maybe: Rename the pos_ variables to pos_start and pos_end. Or
            change the Edge variables to be consistant.
        * Find out what QStyleOptionGraphicsItem is for.
    """

    # pylint: disable=too-many-instance-attributes
    # Reasoning: All the attributes are needed and used.
    def __init__(self, edge: node_edge.Edge, edge_type: int=EDGE_TYPE_BEZIER, parent: QWidget=None):
        """Inits the components needed for the Edge graphic."""
        super().__init__(parent)

        self.edge: node_edge.Edge = edge
        self.__edge_type: int = edge_type

        # flag variables
        self._last_selected_state: bool = False # holds the last state of the edge being selected
        self.hovered: bool = False

        self.pos_source: ds.Point = ds.Point(0, 0)
        self.pos_destination: ds.Point = ds.Point(200, 100)

        self.line_width: float = 2.0
        self.__set_colors()

        # set flags and z-value
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setZValue(-1)


    def __set_colors(self):
        """Rather than convolute the __init__, do the brush, pen and
        colors here.
        """
        self._color = QColor("#adadad")
        self._color_selected = QColor("#00ff00")
        self._color_hovered = QColor("#adadad")
        self._pen = QPen(self._color)
        self._pen_selected = QPen(self._color_selected)
        self._pen_dragging = QPen(self._color)
        self._pen_hovered = QPen(self._color_hovered)
        self._pen_dragging.setStyle(Qt.DashLine)
        self._pen.setWidthF(self.line_width)
        self._pen_selected.setWidthF(self.line_width + 2.0)
        self._pen_dragging.setWidthF(self.line_width + 2.0)
        self._pen_hovered.setWidthF(self.line_width + 4.0)


    def on_selected(self):
        """When selected emit an event to the GraphicsScene."""
        self.edge.scene.graphics_scene.item_selected.emit()

    def do_select(self, new_state: bool=True):
        """Set the GraphicsEdge's state to selected

        Args:
            new_state (bool):
        """
        self.set_selected(new_state)
        self._last_selected_state = new_state
        if new_state:
            self.on_selected()

    def set_source(self, x_pos: int, y_pos: int):
        """Set the source Socket position.

        Args:
            x_pos (int): The x coordinate position.
            y_pos (int): The y coordinate position.
        """
        self.pos_source.point = (x_pos, y_pos)

    def set_destination(self, x_pos: int, y_pos: int):
        """Set the destination Socket position.

        Args:
            x_pos (int): The x coordinate position.
            y_pos (int): The y coordinate position.
        """
        self.pos_destination.point = (x_pos, y_pos)

    def shape(self) -> QPainterPath:
        """Returns the GraphicsEdge's QPainterPath.

        Returns:
            QPainterPath: The edge's line path object.
        """
        return self.calc_path()

    # pylint: disable=no-else-return
    # Reasoning: If the method hits the else case its raises an Exception.
    def calc_path(self) -> QPainterPath:
        """Calculates the line path for the GraphicsEdge based on the line
        type.

        Returns:
            QPainterPath: The edge's line path object.

        Todo:
            * Make more readable. Get rid of s & d shit.
            * More elegant way to check the type of line?
        """
        if self.__edge_type == EDGE_TYPE_DIRECT:
            path = QPainterPath(QPointF(self.pos_source.x, self.pos_source.y))
            path.lineTo(self.pos_destination.x, self.pos_destination.y)
            return path
        elif self.__edge_type == EDGE_TYPE_BEZIER:
            s = self.pos_source
            d = self.pos_destination
            dist = (d.x - s.x) * 0.5

            cpx_s = +dist
            cpx_d = -dist
            cpy_s = 0
            cpy_d = 0

            if self.edge.start_socket is not None:
                sspos = self.edge.start_socket.position

                if (s.x > d.x and sspos in (
                    node_socket.RIGHT_TOP, node_socket.RIGHT_BOTTOM
                    )) or (s.x < d.x and sspos in (
                    node_socket.LEFT_BOTTOM, node_socket.LEFT_TOP
                    )
                ):
                    cpx_d *= -1
                    cpx_s *= -1

                    cpy_d = (
                        (s.y - d.y) / math.fabs(
                            (s.y - d.y) if (s.y - d.y) != 0 else 0.00001
                        )
                    ) * EDGE_CP_ROUNDNESS
                    cpy_s = (
                        (d.y - s.y) / math.fabs(
                            (d.y - s.y) if (d.y - s.y) != 0 else 0.00001
                        )
                    ) * EDGE_CP_ROUNDNESS


            path = QPainterPath(QPointF(self.pos_source.x, self.pos_source.y))
            path.cubicTo( s.x + cpx_s, s.y + cpy_s, d.x + cpx_d, d.y +
                cpy_d, self.pos_destination.x, self.pos_destination.y
            )

            return path
        else:
            logparams.logging.debug(f"Edge type is not correct: {self.__edge_type}")
            raise Exception

        return None

    def intersects_with(self, point1: QPointF, point2: QPointF) -> bool:
        """Determines if the GraphicsEdge intersects with the cutline.

        Args:
            point1 (QPointF): The starting cutline point.
            point2 (QPointF): The ending cutline point.

        Returns:
            bool: True if the cutline intersects, False otherwise.
        """
        cutpath = QPainterPath(point1)
        cutpath.lineTo(point2)
        path = self.calc_path()
        return cutpath.intersects(path)


    # Overloaded Methods
    # ------------------

    # pylint: disable=invalid-name
    # Reasoning: PyQt boundingRect overloaded method requires the
    # camel case.
    def boundingRect(self) -> QRect:
        """Returns the bounding rectangle of the GraphicsEdge.

        Returns:
            QRect: The QGraphicsPathItem's bounding rectangle.
        """
        return self.shape().boundingRect()

    # pylint: disable=unused-argument
    # Reasoning: PyQt painter overloaded method requires it.
    # pylint: disable=invalid-name
    # Reasoning: PyQt painter overloaded method requires the camel case.
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        """Overloaded QWidget paint method.

        Draws the line on the GraphicsScene. It also draws the hovered and
        selected indicators.

        Args:
            painter: QWidget painter class.
            QStyleOptionGraphicsItem: ??? (not used).
            widget: The parent widget if there is one(not used).

        Todo:
            * Find out what QStyleOptionGraphicsItem is for.
        """
        self.setPath(self.calc_path())

        painter.setBrush(Qt.NoBrush)

        if self.hovered and self.edge.end_socket is not None:
            painter.setPen(self._pen_hovered)
            painter.drawPath(self.path())

        if self.edge.end_socket is None:
            painter.setPen(self._pen_dragging)
        else:
            painter.setPen(self._pen if not self.isSelected() else self._pen_selected)

        painter.drawPath(self.path())

    # pylint: disable=invalid-name
    # Reasoning: PyQt overloaded method is camel case.
    def mouseReleaseEvent(self, event):
        """Overloaded method for the mouse release event.

        If the previously selected object is not this edge then set
        selected.

        Args:
            event: Contains the event data.
        """
        super().mouseReleaseEvent(event)
        if self._last_selected_state != self.isSelected():
            self.edge.scene.reset_last_selected_states()
            self._last_selected_state = self.isSelected()
            self.on_selected()

    # pylint: disable=invalid-name
    # Reasoning: PyQt overloaded method is camel case.
    # pylint: disable=unused-argument
    # Reasoning: PyQt event overloaded method requires it.
    def hoverEnterEvent(self, event):
        """Overloaded method for the hover entered event.

        Sets the GraphicsEdge to hovered and updates.

        Args:
            event: Contains the event data.
        """
        self.hovered = True
        self.update()

    # pylint: disable=invalid-name
    # Reasoning: PyQt overloaded method is camel case.
    # pylint: disable=unused-argument
    # Reasoning: PyQt event overloaded method requires it.
    def hoverLeaveEvent(self, event):
        """Overloaded method for the hover leave event.

        Sets the GraphicsEdge to not hovered and updates.

        Args:
            event: Contains the event data.
        """
        self.hovered = False
        self.update()
