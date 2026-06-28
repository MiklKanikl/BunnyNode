from PyQt6.QtWidgets import QDockWidget, QLabel, QVBoxLayout, QWidget

class CalcDock(QDockWidget):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        panel = QWidget()
        layout = QVBoxLayout(panel)

        # distance label
        self.dist_label = QLabel("Waiting for Computation...")
        layout.addWidget(self.dist_label)

        layout.addStretch()
        self.setWidget(panel)