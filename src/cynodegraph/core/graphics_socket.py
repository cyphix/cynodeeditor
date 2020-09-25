# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module
from __future__ import generator_stop
from __future__ import annotations

from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import QBrush, QColor, QPen, QPolygonF

from cynodegraph.core import node_scene
from cynodegraph.core import node_socket



# socket type CONST
SOCKET_BOOL = 0
SOCKET_INTEGER = 1
SOCKET_FLOAT = 2
SOCKET_STRING = 3



class GraphicsSocket(QGraphicsItem):
    """The graphical representation of the Socket.

    Args:
        socket (Socket): Reference to the parent Socket of this.
        scene (Scene): Reference to Scene object that the Socket is drawn on(child of).
        socket_type (int): An integer value representing the type of Socket.

    Attributes:
        socket (Socket): Reference to the parent Socket of this.
        scene (Scene): Reference to Scene object that the Socket is drawn on(child of).
        socket_type (int): An integer value representing the type of Socket.
        outline_width (float): The thickness of the GraphicsSocket's outline.
        radius (float): The radius of the GraphicsSocket.
        hovered (bool): Flag for if the GraphicsSocket is hovered over currently.

    Todo:
        * Maybe make SOCKET_ consts into a dictionary.
        * Potentially add a way to make the socket types/colors dynamic.
        * Find out what QStyleOptionGraphicsItem is for.
    """

    # pylint: disable=too-many-instance-attributes
    # Reasoning: All the attributes are needed and used.
    def __init__(self, socket: node_socket.Socket, scene: node_scene.Scene,
        socket_type: int=1
    ):
        """Inits the components needed for the socket graphic."""
        super().__init__(socket.node.graphics_node)

        self.__alpha_color: QColor = QColor("#00000000")
        self.__point_length: float = 4.0
        self.__poly_outline_width: float = 1.0

        self.scene: node_scene.Scene = scene

        self.outline_width: float = 1.5
        self.radius: float = 4.0
        self.socket: float = socket
        self.socket_type: float = socket_type
        self.hovered: float = False

        self.__set_colors()

        # set object flags
        self.setAcceptHoverEvents(True)


    def __set_colors(self):
        """Rather than convolute the __init__, do the brush, pen and
        colors here.

        The colors are meant to be dependent on the socket type.

        Todo:
            * Potentially add a way to make the socket types/colors dynamic.
        """

        # color scheme from:
        # https://docs.unrealengine.com/en-US/Engine/Blueprints/UserGuide/Nodes/index.html
        self.__color_dict = {
            SOCKET_BOOL : QColor("#FF8f0700"),
            SOCKET_INTEGER : QColor("#FF21e2ab"),
            SOCKET_FLOAT : QColor("#FF9dff3f"),
            SOCKET_STRING : QColor("#FFf604cc"),
        }
        self.__color_background: QColor = self.__color_dict[self.socket_type]
        self.__color_outline: QColor = self.__color_dict[self.socket_type]

        self.__brush: QBrush = QBrush(self.__color_background)
        self.__pen: QPen = QPen(self.__color_outline)
        self.__pen.setWidthF(self.outline_width)
        self.__poly_pen: QPen = QPen(self.__color_outline)
        self.__poly_pen.setWidthF(self.__poly_outline_width)


    # Overloaded Methods
    # ------------------

    # pylint: disable=invalid-name
    # Reasoning: PyQt boundingRect overloaded method requires the
    # camel case.
    def boundingRect(self) -> QRectF:
        """Returns the bounding rectangle of the GraphicsSocket.

        Returns:
            QRect: The Qt bounding rectangle.
        """
        return QRectF(
            - self.radius - self.outline_width,
            - self.radius - self.outline_width,
            2 * (self.radius + self.outline_width),
            2 * (self.radius + self.outline_width),
        )

    # pylint: disable=unused-argument
    # Reasoning: PyQt painter overloaded method requires it.
    # pylint: disable=invalid-name
    # Reasoning: PyQt painter overloaded method requires the camel case.
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        """Overloaded QWidget paint method.

        Draws the Socket with it's directional indicator. The Socket changes
        from a hollow circle when the Socket has no connection to a filled
        circle when the Socket is connected.

        Args:
            painter: QWidget painter class.
            QStyleOptionGraphicsItem: ??? (not used).
            widget: The parent widget if there is one(not used).

        Todo:
            * Find out what QStyleOptionGraphicsItem is for.
        """
        painter.setBrush(self.__brush)
        painter.setPen(self.__pen)

        # draws the direction arrow
        polygon = QPolygonF()
        polygon.append(QPointF(self.radius + (self.radius/4 * 1.5), -(self.radius/4 * 2.5)))
        polygon.append(QPointF(self.radius + self.__point_length, 0.0))
        polygon.append(QPointF(self.radius + (self.radius/4 * 1.5), (self.radius/4 * 2.5)))

        # draws either a hollow circle or filled depending on if active
        if len(self.socket.edges) > 0:
            painter.drawEllipse(-self.radius, -self.radius, self.radius * 2, self.radius * 2)
        else:
            painter.setBrush(self.__alpha_color)
            painter.drawEllipse(-self.radius, -self.radius, self.radius * 2, self.radius * 2)

        painter.setBrush(self.__brush)
        painter.setPen(self.__poly_pen)

        painter.drawPolygon(polygon)
