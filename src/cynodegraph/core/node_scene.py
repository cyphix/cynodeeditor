# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module
from __future__ import generator_stop
from __future__ import annotations

from typing import List

from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtCore import QPointF

from cynodegraph.core import node_edge
from cynodegraph.core import graphics_scene
from cynodegraph.core import node



# TODO: understand 'callback'
class Scene:
    def __init__(self):
        self.nodes: List[node.Node] = []
        self.edges: List[node_edge.Edge] = []

        self.scene_width: int = 64000
        self.scene_height: int = 64000

        self._has_been_modified: bool = False
        self._last_selected_items: List = []

        # initialiaze all listeners
        self._has_been_modified_listeners: List = []
        self._item_selected_listeners: List = []
        self._items_deselected_listeners: List = []

        # here we can store callback for retrieving the class for Nodes
        self.node_class_selector: 'Node Class Instance' = None

        self.graphics_scene: graphics_scene.NodeEditorGraphicsScene = (
            graphics_scene.NodeEditorGraphicsScene(self))
        self.graphics_scene.set_scene(self.scene_width, self.scene_height)

        # slots
        self.graphics_scene.item_selected.connect(self.on_item_selected)
        self.graphics_scene.items_deselected.connect(self.on_items_deselected)


    @property
    def has_been_modified(self) -> bool:
        return self._has_been_modified

    @has_been_modified.setter
    def has_been_modified(self, value: bool):
        if not self._has_been_modified and value:
            # set it now, because we will be reading it soon
            self._has_been_modified = value

            # call all registered listeners
            for callback in self._has_been_modified_listeners: callback()

        self._has_been_modified = value



    def on_item_selected(self):
        current_selected_items = self.get_selected_items()
        if current_selected_items != self._last_selected_items:
            self._last_selected_items = current_selected_items
            for callback in self._item_selected_listeners: callback()

    def on_items_deselected(self):
        self.reset_last_selected_states()
        if self._last_selected_items != []:
            self._last_selected_items = []
            for callback in self._items_deselected_listeners: callback()

    def is_modified(self) -> bool:
        return self.has_been_modified

    def get_selected_items(self) -> list:
        return self.graphics_scene.selectedItems()

    # our helper listener functions
    def addHasBeenModifiedListener(self, callback):
        self._has_been_modified_listeners.append(callback)

    def addItemSelectedListener(self, callback):
        self._item_selected_listeners.append(callback)

    def addItemsDeselectedListener(self, callback):
        self._items_deselected_listeners.append(callback)

    def addDragEnterListener(self, callback):
        self.get_view().addDragEnterListener(callback)

    def addDropListener(self, callback):
        self.get_view().addDropListener(callback)

    # custom flag to detect node or edge has been selected....
    def reset_last_selected_states(self):
        for node in self.nodes:
            node.graphics_node._last_selected_state = False
        for edge in self.edges:
            edge.graphics_edge._last_selected_state = False

    def get_view(self) -> QGraphicsView:
        return self.graphics_scene.views()[0]

    def get_item_at(self, pos: QPointF):
        return self.get_view().itemAt(pos)

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)

    def remove_node(self, node: node.Node):
        if node in self.nodes:
            self.nodes.remove(node)
        else:
            print("!W:", "Scene::remove_node", "want to remove node", node, "from self.nodes but it's not in the list!")

    def remove_edge(self, edge: node_edge.Edge):
        if edge in self.edges:
            self.edges.remove(edge)
        else:
            print("!W:", "Scene::remove_edge", "want to remove edge", edge, "from self.edges but it's not in the list!")

    def clear(self):
        while len(self.nodes) > 0:
            self.nodes[0].remove()

        self.has_been_modified = False



    # TODO: May not need
    def get_node_class_from_data(self, data) -> 'Node Class Instance':
        return (
            Node if self.node_class_selector is None
            else self.node_class_selector(data)
        )
