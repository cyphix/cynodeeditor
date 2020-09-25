# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module
from __future__ import generator_stop
from __future__ import annotations

from PyQt5.QtWidgets import QLabel, QPushButton, QWidget, QVBoxLayout

from cynodegraph.core import node



class NodeContentWidget(QWidget):
    def __init__(self, node_ref: node.Node, parent: QWidget=None):
        super().__init__(parent)

        self.node: node.Node = node_ref

        self.layout: QVBoxLayout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.widget_label: QLabel = QLabel("Some Title")
        self.layout.addWidget(self.widget_label)
        #self.layout.addWidget(QTextEdit("foo"))

        self.add_input_btn: QPushButton = QPushButton("Add Pin")
        self.add_input_btn.clicked.connect(self.button_state)
        #self.layout.addWidget(self.add_input_btn)



    def button_state(self):
        print("button pressed")
