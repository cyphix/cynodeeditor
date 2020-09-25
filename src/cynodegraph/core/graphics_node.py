# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module
from __future__ import generator_stop
from __future__ import annotations

from PyQt5.QtWidgets import QGraphicsItem, QGraphicsProxyWidget, QGraphicsTextItem, QWidget
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainterPath, QPen

from cynodegraph.core import node
from cynodegraph.core import node_content_widget



class GraphicsNode(QGraphicsItem):
    """The graphical representation of the Node.

    Args:
        node_ref (Node): Reference to the parent Node of this.
        parent (QWidget): The parent QWidget of the node graphic.

    Attributes:
        node (Node): Reference to the parent Node of this.
        content (NodeContentWidget): Reference to the Node's content object.
        hovered (bool): Flag for if the GraphicsNode is hovered over currently.
        width (int): The width of the Node in pixels.
        height (int): The height of the Node in pixels.
        edge_roundness (float): Value to determine the intensity of the
            Node's edge roundness.
        edge_padding (float): Value for the padding between the Node's
            edge and it's content.
        title_height (float): Value for the Node's title height.
        title_horizontal_padding (float): Value for the horizontal padding
            between the Node's edge and title .
        title_vertical_padding (float): Value for the vertical padding
            between the Node's edge and title .
        graphics_content (QGraphicsProxyWidget): Reference to the content's
            QGraphicsProxyWidget.

    Todo:
        * Find out what QStyleOptionGraphicsItem is for.
    """

    # pylint: disable=too-many-instance-attributes
    # Reasoning: All the attributes are needed and used.
    def __init__(self, node_ref: node.Node, parent: QWidget=None):
        """Inits the components needed for the Node graphic."""
        super().__init__(parent)

        self.node: node.Node = node_ref
        self.content: node_content_widget.NodeContentWidget = self.node.content

        self._title: str = self.node.title

        # flag variables
        self.hovered: bool = False
        self._was_moved: bool = False
        self._last_selected_state: bool = False

        # settings
        self.width: int = 180
        self.height: int = 240
        self.edge_roundness: float = 10.0
        self.edge_padding: float = 20.0
        self.title_height: float = 24.0
        self.title_horizontal_padding: float = 4.0
        self.title_vertical_padding: float = 4.0

        # create components
        self.__set_colors()
        self.__set_title_item()

        # content
        self.graphics_content: QGraphicsProxyWidget = QGraphicsProxyWidget(self)
        self.content.setGeometry(
            self.edge_padding, self.title_height + self.edge_padding,
            self.width - 2 * self.edge_padding,
            self.height - 2 * self.edge_padding - self.title_height
        )
        self.graphics_content.setWidget(self.content)

        # set object flags
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setAcceptHoverEvents(True)



    def __set_colors(self):
        """Rather than convolute the __init__, do the brush, pen and
        colors here.
        """
        # title text font and color
        self._title_color: QColor = Qt.white
        self._title_font: QFont = QFont("Helvetica", 9)
        self._title_font.setBold(True)

        # colors to use for the outlines
        self._color: QColor = QColor("#7F000000")
        self._color_selected: QColor = QColor("#FFFFA637")
        self._color_hovered: QColor = QColor("#FF37A6FF")

        # outline pens
        self._pen_default: QPen = QPen(self._color)
        self._pen_default.setWidthF(1.0)
        self._pen_selected: QPen = QPen(self._color_selected)
        self._pen_selected.setWidthF(3.0)
        self._pen_hovered: QPen = QPen(self._color_hovered)
        self._pen_hovered.setWidthF(3.0)

        # background brushes
        self._brush_title: QBrush = QBrush(QColor("#FF313131"))
        self._brush_background: QBrush = QBrush(QColor("#D3212121"))

        # create gradient brush for title
        hor_gradient: QLinearGradient = QLinearGradient(
            0, 0, (self.width*0.8), self.title_height
        )
        ver_gradient: QLinearGradient = QLinearGradient(0, 0, 0, 20)
        gradient = hor_gradient
        gradient.setColorAt(0.0, QColor("#e0098be0"))
        gradient.setColorAt(1.0, QColor("#FF313131"))
        self._brush_title_grad: QBrush = QBrush(gradient)

    def __set_title_item(self):
        """Rather than convolute the __init__, set the Node title here.
        """
        self.title_item: QGraphicsTextItem = QGraphicsTextItem(self)
        self.title_item.node = self.node
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self.title_horizontal_padding, 0)
        self.title_item.setTextWidth(
            self.width - (2 * self.title_horizontal_padding)
        )
        self.title_item.setPlainText(self._title)



    @property
    def title(self) -> str:
        """str: Reference to the Node's title.

        Setter: Change the Node's title value and the then update the drawn
        text.
        """
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value
        self.title_item.setPlainText(self._title)



    def on_selected(self):
        """When selected emit an event to the GraphicsScene."""
        self.node.scene.graphics_scene.item_selected.emit()

    def do_select(self, new_state=True):
        """Set the GraphicsNode's state to selected

        Args:
            new_state (bool):
        """
        self.set_selected(new_state)
        self._last_selected_state = new_state
        if new_state:
            self.on_selected()


    # Overloaded Methods
    # ------------------

    # pylint: disable=invalid-name
    # Reasoning: PyQt boundingRect overloaded method requires the
    # camel case.
    def boundingRect(self):
        """Returns the bounding rectangle of the GraphicsNode.

        Returns:
            QRect: The Qt bounding rectangle.
        """
        return QRectF(
            0,
            0,
            self.width,
            self.height
        ).normalized()

    # pylint: disable=unused-argument
    # Reasoning: PyQt hoverEnterEvent overloaded method requires it.
    # pylint: disable=invalid-name
    # Reasoning: PyQt hoverEnterEvent overloaded method requires the
    # camel case.
    def hoverEnterEvent(self, event):
        """When the mouse hover enter event triggers, set the Node to
        hovered and then refresh the GraphicsNode.
        """
        self.hovered = True
        self.update()

    # pylint: disable=unused-argument
    # Reasoning: PyQt hoverLeaveEvent overloaded method requires it.
    # pylint: disable=invalid-name
    # Reasoning: PyQt hoverLeaveEvent overloaded method requires the
    # camel case.
    def hoverLeaveEvent(self, event):
        """When the mouse hover leave event triggers, set the Node to
        hovered and then refresh the GraphicsNode.
        """
        self.hovered = False
        self.update()

    # pylint: disable=invalid-name
    # Reasoning: PyQt mouseMoveEvent overloaded method requires the
    # camel case.
    def mouseMoveEvent(self, event):
        """When the mouse move event triggers, trigger the proper graphical
        updates.
        """
        super().mouseMoveEvent(event)

        # TODO: optimize me! just update the selected nodes
        for node_instance in self.scene().scene.nodes:
            if node_instance.graphics_node.isSelected():
                node_instance.update_connected_edges()
        self._was_moved = True

    # pylint: disable=invalid-name
    # Reasoning: PyQt mouseReleaseEvent overloaded method requires the
    # camel case.
    def mouseReleaseEvent(self, event):
        """When the mouse release event triggers, trigger the proper
        graphical updates.
        """
        super().mouseReleaseEvent(event)

        # handle when GraphicsNode moved
        if self._was_moved:
            self._was_moved = False

            self.node.scene.reset_last_selected_states()
            self._last_selected_state = True

            # we need to store the last selected state, because moving does also select the nodes
            self.node.scene._last_selected_items = self.node.scene.get_selected_items()

            # now we want to skip storing selection
            return

        # handle when grNode was clicked on
        if(self._last_selected_state != self.isSelected() or
            self.node.scene._last_selected_items != self.node.scene.get_selected_items()
        ):
            self.node.scene.reset_last_selected_states()
            self._last_selected_state = self.isSelected()
            self.on_selected()

    # pylint: disable=unused-argument
    # Reasoning: PyQt painter overloaded method requires it.
    # pylint: disable=invalid-name
    # Reasoning: PyQt painter overloaded method requires the camel case.
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        """Overloaded QWidget paint method.

        Draws the Node starting with the title, then content, background,
        corner fixes, and outline.

        Args:
            painter: QWidget painter class.
            QStyleOptionGraphicsItem: ??? (not used).
            widget: The parent widget if there is one(not used).

        Todo:
            * Find out what QStyleOptionGraphicsItem is for.
        """
        # title
        path_title = QPainterPath()
        path_title.setFillRule(Qt.WindingFill)
        path_title.addRoundedRect(0, 0, self.width, self.title_height,
            self.edge_roundness, self.edge_roundness
        )
        path_title.addRect(0, self.title_height - self.edge_roundness,
            self.edge_roundness, self.edge_roundness
        )
        path_title.addRect(
            self.width - self.edge_roundness,
            self.title_height - self.edge_roundness, self.edge_roundness,
            self.edge_roundness
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_title_grad)
        painter.drawPath(path_title.simplified())

        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        # add the rectange for the content area background with rounded edges
        path_content.addRoundedRect(
            0, self.title_height, self.width,
            self.height - self.title_height, self.edge_roundness,
            self.edge_roundness
        )
        # next 2 addRects are to create 2 small squares below the title
        # since the are rounded(which we do not want)
        path_content.addRect(0, self.title_height, self.edge_roundness,
            self.edge_roundness
        )
        path_content.addRect(self.width - self.edge_roundness,
            self.title_height, self.edge_roundness, self.edge_roundness
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())

        # selected outline
        if self.isSelected():
            path_outline = QPainterPath()
            path_outline.addRoundedRect(-2, -2, self.width+4,
                self.height+4, self.edge_roundness, self.edge_roundness)
            painter.setBrush(Qt.NoBrush)
            painter.setPen(self._pen_selected)
            painter.drawPath(path_outline.simplified())

        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height,
            self.edge_roundness, self.edge_roundness)
        painter.setBrush(Qt.NoBrush)
        if self.hovered:
            #painter.setPen(self._pen_hovered)
            #painter.drawPath(path_outline.simplified())
            painter.setPen(self._pen_default)
            painter.drawPath(path_outline.simplified())
        else:
            painter.setPen(self._pen_default)
            painter.drawPath(path_outline.simplified())
