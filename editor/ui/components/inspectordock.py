from PyQt6.QtWidgets import (
    QDockWidget, QLabel, QVBoxLayout, QWidget, QGroupBox,
    QGridLayout, QSpinBox, QLineEdit, QPushButton, QDoubleSpinBox,
    QScrollArea, QColorDialog
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QPointF, QTimer
from editor.items.edge import EdgeItem
from editor.items.node import NodeItem

class InspectorDock(QDockWidget):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        self.setWindowTitle("Inspector")
        self.current_item = None
        self.controller = parent.controller
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        panel = QWidget()
        self.main_layout = QVBoxLayout(panel)

        # info group
        self.info_group = QGroupBox("Item Information")
        info_layout = QGridLayout()
        
        info_layout.addWidget(QLabel("Type:"), 0, 0)
        self.type_label = QLabel("None")
        info_layout.addWidget(self.type_label, 0, 1)
        
        info_layout.addWidget(QLabel("ID:"), 1, 0)
        self.id_label = QLabel("-")
        info_layout.addWidget(self.id_label, 1, 1)
        
        self.info_group.setLayout(info_layout)
        self.main_layout.addWidget(self.info_group)

        # pos group
        self.position_group = QGroupBox("Position")
        pos_layout = QGridLayout()
        
        pos_layout.addWidget(QLabel("X:"), 0, 0)
        self.x_spin = QDoubleSpinBox()
        self.x_spin.setRange(0, 3000)
        self.x_spin.editingFinished.connect(self._on_position_changed)
        pos_layout.addWidget(self.x_spin, 0, 1)
        
        pos_layout.addWidget(QLabel("Y:"), 1, 0)
        self.y_spin = QDoubleSpinBox()
        self.y_spin.setRange(0, 3000)
        self.y_spin.editingFinished.connect(self._on_position_changed)
        pos_layout.addWidget(self.y_spin, 1, 1)
        
        self.position_group.setLayout(pos_layout)
        self.main_layout.addWidget(self.position_group)

        # size group
        self.size_group = QGroupBox("Size")
        size_layout = QGridLayout()
        
        size_layout.addWidget(QLabel("Width:"), 0, 0)
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(5, 1000)
        self.width_spin.editingFinished.connect(self._on_size_changed)
        size_layout.addWidget(self.width_spin, 0, 1)
        
        size_layout.addWidget(QLabel("Height:"), 1, 0)
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(5, 1000)
        self.height_spin.editingFinished.connect(self._on_size_changed)
        size_layout.addWidget(self.height_spin, 1, 1)
        
        self.size_group.setLayout(size_layout)
        self.main_layout.addWidget(self.size_group)
        
        # color group
        self.color_group = QGroupBox("Appearance")
        color_layout = QGridLayout()
        
        color_layout.addWidget(QLabel("Color:"), 0, 0)
        self.color_button = QPushButton("Choose Color...")
        self.color_button.clicked.connect(self._on_color_clicked)
        self.color_display = QLabel()
        self.color_display.setFixedSize(30, 30)
        self.color_display.setStyleSheet(
                f"background-color: rgb({255}, {255}, {255}); "
                f"border: 1px solid black;"
            )
        color_layout.addWidget(self.color_display, 0, 1)
        color_layout.addWidget(self.color_button, 0, 2)
        
        self.color_group.setLayout(color_layout)
        self.main_layout.addWidget(self.color_group)
        
        # text group
        self.text_group = QGroupBox("Label")
        text_layout = QGridLayout()
        
        text_layout.addWidget(QLabel("Text:"), 0, 0)
        self.text_input = QLineEdit()
        self.text_input.textChanged.connect(self._on_text_changed)
        text_layout.addWidget(self.text_input, 0, 1)
        
        self.text_group.setLayout(text_layout)
        self.main_layout.addWidget(self.text_group)
        
        # edge group
        self.edge_group = QGroupBox("Edge Properties")
        edge_layout = QGridLayout()
        
        edge_layout.addWidget(QLabel("Start Node:"), 0, 0)
        self.start_node_label = QLabel("-")
        edge_layout.addWidget(self.start_node_label, 0, 1)
        
        edge_layout.addWidget(QLabel("End Node:"), 1, 0)
        self.end_node_label = QLabel("-")
        edge_layout.addWidget(self.end_node_label, 1, 1)
        
        edge_layout.addWidget(QLabel("Width:"), 2, 0)
        self.edge_width_spin = QSpinBox()
        self.edge_width_spin.setRange(1, 50)
        self.edge_width_spin.editingFinished.connect(self._on_edge_width_changed)
        edge_layout.addWidget(self.edge_width_spin, 2, 1)
        
        self.edge_group.setLayout(edge_layout)
        self.main_layout.addWidget(self.edge_group)

        self.main_layout.addStretch()
        scroll.setWidget(panel)
        self.setWidget(scroll)
    
    def update_inspector(self, item):
        self.current_item = item
        
        if not item:
            self._clear_inspector()
            return
        
        self.adapt_to_item(item)
        self._update_common_properties()
        self._update_item_specific_properties()
    
    def adapt_to_item(self, item):
        is_edge = isinstance(item, EdgeItem)
        is_node = isinstance(item, NodeItem)
        
        self.position_group.setVisible(True)
        self.color_group.setVisible(True)
        self.size_group.setVisible(is_node and not is_edge)
        self.text_group.setVisible(is_node and not is_edge)
        self.edge_group.setVisible(is_edge)
    
    def _update_common_properties(self):
        if not self.current_item:
            return
        
        item_type = type(self.current_item).__name__
        self.type_label.setText(item_type)
        
        if hasattr(self.current_item, 'id'):
            self.id_label.setText(str(self.current_item.id))
        else:
            self.id_label.setText("-")
        
        pos = self.current_item.pos()
        self.x_spin.blockSignals(True)
        self.y_spin.blockSignals(True)
        self.x_spin.setValue(pos.x())
        self.y_spin.setValue(pos.y())
        self.x_spin.blockSignals(False)
        self.y_spin.blockSignals(False)
        
        if hasattr(self.current_item, 'color'):
            color = self.current_item.color
            self.color_display.setStyleSheet(
                f"background-color: rgb({color.red()}, {color.green()}, {color.blue()}); "
                f"border: 1px solid black;"
            )
    
    def _update_item_specific_properties(self):
        if isinstance(self.current_item, EdgeItem):
            self._update_edge_properties()
        else:
            self._update_node_properties()
    
    def _update_node_properties(self):
        if not hasattr(self.current_item, 'width'):
            return
        
        self.width_spin.blockSignals(True)
        self.height_spin.blockSignals(True)
        self.text_input.blockSignals(True)
        
        self.width_spin.setValue(self.current_item.width)
        self.height_spin.setValue(self.current_item.height)
        
        if hasattr(self.current_item, 'text'):
            self.text_input.setText(self.current_item.text)
        
        self.width_spin.blockSignals(False)
        self.height_spin.blockSignals(False)
        self.text_input.blockSignals(False)
    
    def _update_edge_properties(self):
        self.start_node_label.setText(f"Node {self.current_item.start_node.id}")
        self.end_node_label.setText(f"Node {self.current_item.end_node.id}")
        
        self.edge_width_spin.blockSignals(True)
        self.edge_width_spin.setValue(self.current_item.p_width)
        self.edge_width_spin.blockSignals(False)
    
    def _on_position_changed(self):
        if not self.current_item:
            return

        self.controller.move_node([self.current_item], [self.current_item.pos()], [QPointF(self.x_spin.value(), self.y_spin.value())])
    
    def _on_size_changed(self):
        if not self.current_item or not hasattr(self.current_item, 'width'):
            return
        
        self.controller.resize_node(self.current_item, self.current_item.width, self.current_item.height, self.width_spin.value(), self.height_spin.value())
    
    def _on_color_clicked(self):
        if not self.current_item:
            return
        
        current_color = self.current_item.color if hasattr(self.current_item, 'color') else QColor(255, 255, 255)
        color = QColorDialog.getColor(current_color, None, "Choose Color")
        
        if color.isValid():
            self.controller.change_color(self.current_item, self.current_item.color, color)
            self._update_common_properties()
    
    def _on_text_changed(self):
        if not self.current_item or not hasattr(self.current_item, 'update_text'):
            return
        
        if not hasattr(self, '_text_timer'):
            self._text_timer = QTimer()
            self._text_timer.setSingleShot(True)
            self._text_timer.timeout.connect(self._apply_text_change)
        
        self._text_timer.stop()
        self._text_timer.start(500)
    
    def _apply_text_change(self):
        if not self.current_item:
            return
        
        new_text = self.text_input.text()
        if hasattr(self.current_item, 'text') and self.current_item.text != new_text:
            self.current_item.update_text(new_text)
    
    def _on_edge_width_changed(self):
        if not self.current_item or not hasattr(self.current_item, 'p_width'):
            return
        
        self.controller.resize_edge(self.current_item, self.current_item.p_width, self.edge_width_spin.value())
    
    def _clear_inspector(self):
        self.type_label.setText("None")
        self.id_label.setText("-")
        self.x_spin.blockSignals(True)
        self.y_spin.blockSignals(True)
        self.width_spin.blockSignals(True)
        self.height_spin.blockSignals(True)
        self.text_input.blockSignals(True)
        self.edge_width_spin.blockSignals(True)
        
        self.x_spin.setValue(0)
        self.y_spin.setValue(0)
        self.width_spin.setValue(5)
        self.height_spin.setValue(5)
        self.text_input.setText("")
        self.edge_width_spin.setValue(1)
        self.color_display.setStyleSheet("background-color: white; border: 1px solid black;")
        
        self.x_spin.blockSignals(False)
        self.y_spin.blockSignals(False)
        self.width_spin.blockSignals(False)
        self.height_spin.blockSignals(False)
        self.text_input.blockSignals(False)
        self.edge_width_spin.blockSignals(False)

        self.position_group.setVisible(True)
        self.color_group.setVisible(True)
        self.size_group.setVisible(True)
        self.edge_group.setVisible(True)
        self.text_group.setVisible(True)