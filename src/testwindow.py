# pylint: disable=missing-docstring
# pylint: disable=no-name-in-module
from __future__ import generator_stop
from __future__ import annotations

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import QFile

from cynodegraph.core.graphics_view import NodeEditorGraphicsView # pylint: disable=import-error
from cynodegraph.core.node import Node # pylint: disable=import-error
from cynodegraph.core.node_edge import Edge # pylint: disable=import-error
from cynodegraph.core.node_scene import Scene # pylint: disable=import-error



class NodeEditorWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.stylesheet_filename = "qss/nodestyle.qss"
        self._load_sytlesheet(self.stylesheet_filename)

        # set window dimensions
        # 2000, 50 sets it on middle screen(linux)
        self.setGeometry(2000, 50, 1000, 800)

        # set the layout to a verticle layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # create the graphics scene
        self.scene = Scene()
        self.graphics_scene = self.scene.graphics_scene

        # inputs build bottom up, outputs top down
        node1 = Node(self.scene, "Test Node 1", inputs=[0, 1, 2], outputs=[1])
        node2 = Node(self.scene, "Test Node 2", inputs=[1, 2, 3], outputs=[1])
        node3 = Node(self.scene, "Test Node 3", inputs=[1, 2, 3], outputs=[0, 1, 2])

        node1.set_pos(-350, -250)
        node2.set_pos(-75, 0)
        node3.set_pos(200, -250)

        edge1 = Edge(self.scene, node1.outputs[0], node2.inputs[0], edge_type=2)
        edge2 = Edge(self.scene, node2.outputs[0], node3.inputs[0], edge_type=2)



        # create the graphics view
        self.graphics_view = NodeEditorGraphicsView(self.graphics_scene, self)
        self.layout.addWidget(self.graphics_view)

        # display the window
        self.setWindowTitle("Node Editor")
        self.show()

    def _load_sytlesheet(self, filename):
        file = QFile(filename)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf-8'))
