# pylint: disable=missing-docstring
# pylint: disable=no-name-in-module
from __future__ import generator_stop
from __future__ import annotations

from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from cynodegraph.core import logparams # pylint: disable=import-error

from testwindow import NodeEditorWindow



if __name__ == "__main__":
    logparams.logging_config()

    import sys
    app = QApplication(sys.argv)
    main_window = NodeEditorWindow()

    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)

    sys.exit(app.exec_())
