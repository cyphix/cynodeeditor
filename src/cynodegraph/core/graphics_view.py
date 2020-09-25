# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module
from __future__ import generator_stop
from __future__ import annotations

from typing import List

from PyQt5.QtWidgets import QGraphicsView, QApplication
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPainter

from cynodegraph.core import graphics_cutline
from cynodegraph.core import graphics_edge
from cynodegraph.core import graphics_socket
from cynodegraph.core import logparams
from cynodegraph.core import node_edge
from cynodegraph.core import guifeedback



MODE_NOOP = 1           #: Mode representing ready state
MODE_EDGE_DRAG = 2      #: Mode representing when we drag edge state
MODE_EDGE_CUT = 3       #: Mode representing when we draw a cutting edge

#: Distance when click on socket to enable `Drag Edge`
EDGE_DRAG_START_THRESHOLD = 10



# TODO: Clean and document
class NodeEditorGraphicsView(QGraphicsView):
    scene_pos_changed = pyqtSignal(int, int)

    def __init__(self, graphics_scene_ref: graphics_scene.GraphicsScene, parent: QWidget=None):
        super().__init__(parent)

        self.graphics_scene = graphics_scene_ref

        self.__clean_draw_init()
        self.setScene(self.graphics_scene)

        self.mode: int = MODE_NOOP
        self.editing_flag: bool = False
        self.rubber_band_dragging_rectangle: bool = False

        self.zoom_in_factor: float = 1.25
        self.zoom_clamp: bool = True
        self.zoom: float = 10.0
        self.zoom_step: float = 1.0
        self.zoom_range: List[float, float] = [0.0, 10.0]

        # cutline
        self.cutline: graphics_cutline.CutLine = graphics_cutline.CutLine()
        self.graphics_scene.addItem(self.cutline)

        # listeners
        self._drag_enter_listeners: List = []
        self._drop_listeners: List = []

        # flags
        self.last_hovered_item: QWidget = None


    def __clean_draw_init(self):
        # clean up drawing ugliness
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        # enable dropping
        self.setAcceptDrops(True)

    def __get_item_at_click(self, event) -> QGraphicsItem:
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj

    # guifeedback popups
    def __socket_connection_warnings(self, event):
        # get item which we hover
        item = self.__get_item_at_click(event)

        # if the hover item is a new one, check if a guifeedback is needed
        if(self.last_hovered_item != item):
            # since its a new item, reset the guifeedback
            self.graphics_scene.guifeedback.reset()

            # process if the item a GraphicsSocket
            if(type(item) == graphics_socket.GraphicsSocket):
                if(item.socket.node == self.drag_start_socket.node):
                    if(item.socket != self.drag_start_socket):
                        self.graphics_scene.guifeedback.set(f"SOCKET ERROR: Same Node", guifeedback.ICON_TYPES['bad'])
                elif(item.socket.is_input == self.drag_start_socket.is_input or item.socket.is_output == self.drag_start_socket.is_output):
                    self.graphics_scene.guifeedback.set(f"SOCKET ERROR: Outputs Must Go To Inputs", guifeedback.ICON_TYPES['bad'])
                elif(item.socket.socket_type != self.drag_start_socket.socket_type):
                    self.graphics_scene.guifeedback.set(f"SOCKET ERROR: Different Socket Types", guifeedback.ICON_TYPES['bad'])

        self.last_hovered_item = item


    # TODO: snake case
    def addDragEnterListener(self, callback):
        self._drag_enter_listeners.append(callback)

    # TODO: snake case
    def addDropListener(self, callback):
        self._drop_listeners.append(callback)

    def cut_intersecting_edges(self):
        for ix in range(len(self.cutline.line_points) - 1):
            p1 = self.cutline.line_points[ix]
            p2 = self.cutline.line_points[ix + 1]

            for edge in self.graphics_scene.scene.edges:
                if edge.graphics_edge.intersects_with(p1, p2):
                    edge.remove()

    def delete_selected(self):
        for item in self.graphics_scene.selectedItems():
            if isinstance(item, graphics_edge.GraphicsEdge):
                item.edge.remove()
            elif hasattr(item, 'node'):
                item.node.remove()

    def debug_modifiers(self, event) -> str:
        out = "MODS: "
        if event.modifiers() & Qt.ShiftModifier: out += "SHIFT "
        if event.modifiers() & Qt.ControlModifier: out += "CTRL "
        if event.modifiers() & Qt.AltModifier: out += "ALT "
        return out

    def get_item_at_click(self, event) -> QWidget:
        pos = event.pos()
        obj = self.item_at(pos)
        return obj

    def edge_drag_start(self, item: QWidget):
        try:
            logparams.logging.info("Start dragging edge")
            logparams.logging.debug(" - assign Start Socket to: {item.socket}")
            self.drag_start_socket = item.socket
            self.drag_edge = node_edge.Edge(self.graphics_scene.scene, item.socket, None, node_edge.EDGE_TYPE_BEZIER)
            logparams.logging.debug(" - drag_edge: {self.drag_edge}")
        except Exception as e:
            logparams.logging.exception("Exception occurred")

    def edge_drag_end(self, item: QWidget) -> bool:
        self.mode = MODE_NOOP

        logparams.logging.info("End dragging edge")
        self.drag_edge.remove()
        self.drag_edge = None

        try:
            if type(item) is graphics_socket.GraphicsSocket:
                # if we released dragging on a socket (other then the beginning socket)
                # also check and only allow if sockets of the same kind
                # and make sure they are not both inputs or outputs
                # and that they are not from the same node
                if item.socket != self.drag_start_socket and item.socket.socket_type == self.drag_start_socket.socket_type and item.socket.is_input != self.drag_start_socket.is_input and item.socket.is_output != self.drag_start_socket.is_output and item.socket.node != self.drag_start_socket.node:
                    # we wanna keep all the edges comming from target socket
                    if not item.socket.is_multi_edges:
                        item.socket.remove_all_edges()

                    # we wanna keep all the edges comming from start socket
                    if not self.drag_start_socket.is_multi_edges:
                        self.drag_start_socket.remove_all_edges()

                    new_edge = node_edge.Edge(self.graphics_scene.scene, self.drag_start_socket, item.socket, edge_type=node_edge.EDGE_TYPE_BEZIER)
                    logparams.logging.debug(f" - created new edge:{new_edge}connecting{new_edge.start_socket}<-->{new_edge.end_socket}")

                    for socket in [self.drag_start_socket, item.socket]:
                        socket.node.on_edge_connection_changed(new_edge)
                        if socket.is_input: socket.node.on_input_changed(new_edge)

                    logparams.logging.debug(" - everything done.")
                    return True
        except Exception as e:
            logparams.logging.exception("Exception occurred")


        logparams.logging.debug(" - FAIL: edge not attached. Return False")
        return False

    def distance_between_click_and_release_is_off(self, event) -> bool:
        new_lmb_release_scene_pos = self.mapToScene(event.pos())
        dist_scene = new_lmb_release_scene_pos - self.last_lmb_click_scene_pos
        edge_drag_threshold_sq = EDGE_DRAG_START_THRESHOLD*EDGE_DRAG_START_THRESHOLD
        return (
            (
                dist_scene.x()*dist_scene.x() +
                dist_scene.y()*dist_scene.y()
            ) > edge_drag_threshold_sq
        )


    # Overloaded Methods
    # ------------------

    def dragEnterEvent(self, event):
        for callback in self._drag_enter_listeners: callback(event)

    def dropEvent(self, event):
        for callback in self._drop_listeners: callback(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def middleMouseButtonPress(self, event):
        item = self.__get_item_at_click(event)

        # debug print out
        if DEBUG:
            if isinstance(item, QDMGraphicsEdge): print('RMB DEBUG:', item.edge, ' connecting sockets:',
                                                        item.edge.start_socket, '<-->', item.edge.end_socket)
            if type(item) is QDMGraphicsSocket: print('RMB DEBUG:', item.socket, 'has edges:', item.socket.edges)

            if item is None:
                print('SCENE:')
                print('  Nodes:')
                for node in self.grScene.scene.nodes: print('    ', node)
                print('  Edges:')
                for edge in self.grScene.scene.edges: print('    ', edge)

        # faking events for enable MMB dragging the scene
        release_event = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(release_event)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fake_event = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fake_event)

    def middleMouseButtonRelease(self, event):
        fake_event = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() & ~Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fake_event)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def leftMouseButtonPress(self, event):
        # get item which we clicked on
        item = self.__get_item_at_click(event)

        # we store the position of last LMB click
        self.last_lmb_click_scene_pos = self.mapToScene(event.pos())

        # logic
        if hasattr(item, "node") or isinstance(item, graphics_edge.GraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fake_event = QMouseEvent(QEvent.MouseButtonPress, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, event.buttons() | Qt.LeftButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mousePressEvent(fake_event)
                return


        if type(item) is graphics_socket.GraphicsSocket:
            if self.mode == MODE_NOOP:
                self.mode = MODE_EDGE_DRAG
                self.edge_drag_start(item)
                return

        if self.mode == MODE_EDGE_DRAG:
            res = self.edge_drag_end(item)
            if res:
                return

        if item is None:
            if event.modifiers() & Qt.ControlModifier:
                self.mode = MODE_EDGE_CUT
                fake_event = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton, event.modifiers())
                super().mouseReleaseEvent(fake_event)
                QApplication.setOverrideCursor(Qt.CrossCursor)
                return
            else:
                self.rubber_band_dragging_rectangle = True

        super().mousePressEvent(event)

    def leftMouseButtonRelease(self, event):
        # get item which we release mouse button on
        item = self.__get_item_at_click(event)

        # logic
        if hasattr(item, "node") or isinstance(item, graphics_edge.GraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fake_event = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mouseReleaseEvent(fake_event)
                return

        if self.mode == MODE_EDGE_DRAG:
            if self.distance_between_click_and_release_is_off(event):
                res = self.edge_drag_end(item)
                if res: return

        if self.mode == MODE_EDGE_CUT:
            self.cut_intersecting_edges()
            self.cutline.line_points = []
            self.cutline.update()
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.mode = MODE_NOOP
            return


        if self.rubber_band_dragging_rectangle:
            self.rubber_band_dragging_rectangle = False
            current_selected_items = self.graphics_scene.selectedItems()

            if current_selected_items != self.graphics_scene.scene._last_selected_items:
                if current_selected_items == []:
                    self.graphics_scene.items_deselected.emit()
                else:
                    self.graphics_scene.item_selected.emit()
                self.graphics_scene.scene._last_selected_items = current_selected_items

            return

        # otherwise deselect everything
        if item is None:
            self.graphics_scene.items_deselected.emit()

        super().mouseReleaseEvent(event)

    def rightMouseButtonPress(self, event):
        super().mousePressEvent(event)

    def rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        # TODO: check if there is a more efficient method
        # partially done with changing it to only process if the hovered item is a new one
        if self.mode == MODE_EDGE_DRAG:
            pos = self.mapToScene(event.pos())
            self.drag_edge.graphics_edge.set_destination(pos.x(), pos.y())
            self.drag_edge.graphics_edge.update()

            # socket connection warning popups
            self.__socket_connection_warnings(event)
        elif self.mode == MODE_EDGE_CUT:
            pos = self.mapToScene(event.pos())
            self.cutline.line_points.append(pos)
            self.cutline.update()
        else:
            # reset the guifeedback if no current operations use it
            self.graphics_scene.guifeedback.reset()

        self.last_scene_mouse_position = self.mapToScene(event.pos())

        self.scene_pos_changed.emit(
            int(self.last_scene_mouse_position.x()), int(self.last_scene_mouse_position.y())
        )

        try:
            # make sure that the guifeedback is always drawn at the mouse
            self.graphics_scene.guifeedback.set_position(self.last_scene_mouse_position.x()+20,self.last_scene_mouse_position.y())
        except Exception as e:
            logparams.logging.exception("Exception occurred")

        # allow call to parent mouse events
        super().mouseMoveEvent(event)

    def keyPressEvent(self, event):
        # Use this code below if you wanna have shortcuts in this widget.
        # You want to use this, when you don't have a window which handles these shortcuts for you

        if event.key() == Qt.Key_Delete:
            if not self.editing_flag:
                self.delete_selected()
            else:
                super().keyPressEvent(event)
        elif event.key() == Qt.Key_S and event.modifiers() & Qt.ControlModifier:
            pass
        elif event.key() == Qt.Key_L and event.modifiers() & Qt.ControlModifier:
            pass
        elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier and not event.modifiers() & Qt.ShiftModifier:
            pass
        elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier and event.modifiers() & Qt.ShiftModifier:
            pass
        elif event.key() == Qt.Key_H:
            pass
        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event):
        # calculate our zoom Factor
        zoom_out_factor = 1 / self.zoom_in_factor

        # calculate zoom
        if(event.angleDelta().y() > 0):
            zoom_factor = self.zoom_in_factor
            self.zoom += self.zoom_step
        else:
            zoom_factor = zoom_out_factor
            self.zoom -= self.zoom_step

        clamped = False
        if(self.zoom < self.zoom_range[0]):
            self.zoom, clamped = self.zoom_range[0], True
        if(self.zoom > self.zoom_range[1]):
            self.zoom, clamped = self.zoom_range[1], True

        # set scene scale
        if not clamped or self.zoom_clamp is False:
            self.scale(zoom_factor, zoom_factor)
