from PyQt6.QtWidgets import QGraphicsScene, QColorDialog, QFileDialog, QMessageBox, QGraphicsPathItem
from PyQt6.QtGui import QBrush, QColor, QCursor, QImage, QPainter, QTransform, QPainterPath, QPen
from PyQt6.QtCore import Qt, QRectF
from editor.items.node import NodeItem
from editor.items.rectangle import NodeRect
from editor.items.ellipse import NodeEllipse
from editor.items.image import ImageNode
from editor.items.edge import EdgeItem
from editor.items.directed_edge import DirectedEdgeItem
from editor.calculations.dijkstra import shortest_path
from editor.items.triangle import NodeTriangle
from editor.path_utils import get_recent_files_path, get_saves_directory
from editor.ui.components.edge_endpoint_handle import EdgeEndpointHandle
import os
import math

class DiagramScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 3000, 3000)
        self.current_color = QColor(0, 150, 255)
        self.current_color_edge = QColor(0, 0, 0)
        self.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
        self.startnode = None
        self.endnode = None
        self.edge_nodes = [None, None]
        self.controller = None
        self.creating_edge = 0
        self.win = None
        self.directed_edge_mode = False
        self._edge_drag_source = None
        self._edge_dragging = False
        self._edge_drag_start_pos = None
        self._edge_drag_moved = False
        self._edge_preview = None
        self._edge_endpoint_handles = {}
        self._edge_reconnect = None
        self.selectionChanged.connect(self._update_edge_endpoint_handles)

    def clear(self):
        self._clear_edge_endpoint_handles()
        super().clear()
    
    def set_services(self, controller):
        self.controller = controller
        self.controller.set_scene(self)
        self.win = self.views()[0].window()
    
    def export_png(self, path: str, source_rect=None):
        if source_rect is None:
            source_rect = self.sceneRect()
            image_width = 3000
            image_height = 3000
        else:
            source_rect = source_rect.normalized()
            if source_rect.isEmpty():
                raise ValueError("The export region must have a non-zero width and height")
            image_width = max(1, math.ceil(source_rect.width()))
            image_height = max(1, math.ceil(source_rect.height()))

        image = QImage(
            image_width,
            image_height,
            QImage.Format.Format_ARGB32
        )
        image.fill(Qt.GlobalColor.black)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        target_rect = QRectF(0, 0, image_width, image_height)
        visible_handles = [
            handle
            for handles in self._edge_endpoint_handles.values()
            for handle in handles.values()
            if handle.isVisible()
        ]
        for handle in visible_handles:
            handle.hide()
        try:
            self.render(painter, target_rect, source_rect)
        finally:
            painter.end()
            for handle in visible_handles:
                handle.show()

        if not image.save(path):
            raise OSError(f"Could not save PNG export to {path}")
    
    def add_rect(self, x, y):
        rect = NodeRect(
            x, y,
            80, 80,
            self.current_color
        )
        if self.controller:
            self.controller.add_node(self, rect)
    
    def add_ellipse(self, x, y):
        ellp = NodeEllipse(
            x, y,
            80, 80,
            self.current_color
        )
        if self.controller:
            self.controller.add_node(self, ellp)
    
    def add_triangle(self, x, y):
        triangle = NodeTriangle(
            x, y,
            80, 80,
            self.current_color
        )
        if self.controller:
            self.controller.add_node(self, triangle)
    
    def add_image(self, x, y):
        image = ImageNode(
            x, y,
            80, 80,
            self.current_color,
        )
        if self.controller:
            self.controller.add_node(self, image)
    
    def save_file_dialog(self):
        filename, _ = QFileDialog.getSaveFileName(
            self.win,
            "Save Diagram",
            os.path.join(get_saves_directory(), "diagram.diagram"),
            "BunnyNode diagrams (*.diagram)",
        )
        if not filename:
            return

        if not filename.lower().endswith(".diagram"):
            filename += ".diagram"
        try:
            self.save_scene(filename=filename)
        except OSError as error:
            QMessageBox.critical(
                self.win, "Save Failed", f"Could not save the diagram:\n{error}"
            )
            return
        self.update_recent_files(filename)
    
    def load_file_dialog(self):
        folder = get_saves_directory()

        filename, _ = QFileDialog.getOpenFileName(
            None,
            "load",
            folder,                      
            "Diagram-files (*.diagram)"
        )
        if filename:
            self.load_scene(filename=filename)
            self.update_recent_files(filename)
    
    def load_popup(self):
        popup = QMessageBox()
        popup.setWindowTitle("Warning")
        popup.setText("Do you want to load a new diagram? All unsaved changes will be lost.")
        popup.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if popup.exec() == QMessageBox.StandardButton.Yes:
            self.load_file_dialog()
    
    def color_dialog(self, item_type):
        if item_type == 0:
            new_color = QColorDialog.getColor(self.current_color)
            if new_color.isValid():
                self.current_color = new_color
        else:
            new_color = QColorDialog.getColor(self.current_color_edge)
            if new_color.isValid():
                self.current_color_edge = new_color
    
    def edge_create_dialog(self, directed):
        if self.creating_edge == 0:
            self._set_status("Select a node and drag to another node, or click two nodes")
            self.creating_edge = 1
            self.directed_edge_mode = directed

    def _set_status(self, text):
        if self.win:
            self.win.status.setText(text)

    def node_at(self, position):
        for item in self.items(position, Qt.ItemSelectionMode.IntersectsItemShape, Qt.SortOrder.DescendingOrder, QTransform()):
            parent = item
            while parent is not None:
                if isinstance(parent, NodeItem):
                    return parent
                parent = parent.parentItem()
        return None

    def _clear_edge_endpoint_handles(self):
        for handles in self._edge_endpoint_handles.values():
            for handle in handles.values():
                if handle.scene() is self:
                    self.removeItem(handle)
        self._edge_endpoint_handles.clear()

    def _update_edge_endpoint_handles(self):
        self._clear_edge_endpoint_handles()
        selected_edges = [
            item for item in self.selectedItems()
            if isinstance(item, EdgeItem)
        ]
        if len(selected_edges) != 1:
            return

        edge = selected_edges[0]
        handles = {}
        for endpoint in ("start", "end"):
            handle = EdgeEndpointHandle(edge, endpoint)
            handle.setPos(edge.endpoint_handle_position(endpoint))
            self.addItem(handle)
            handles[endpoint] = handle
        self._edge_endpoint_handles[edge] = handles

    def refresh_edge_endpoint_handles(self, edge):
        handles = self._edge_endpoint_handles.get(edge)
        if not handles:
            return
        for endpoint, handle in handles.items():
            handle.setPos(edge.endpoint_handle_position(endpoint))

    def _start_endpoint_reconnect(self, edge, endpoint, position):
        self.creating_edge = 0
        self.edge_nodes = [None, None]
        self._edge_drag_source = None
        self.directed_edge_mode = False
        self._edge_reconnect = (edge, endpoint)
        self._edge_dragging = True
        self._edge_drag_start_pos = position
        self._edge_drag_moved = False
        fixed_node = edge.end_node if endpoint == "start" else edge.start_node
        path = QPainterPath()
        if endpoint == "start":
            path.moveTo(position)
            path.lineTo(fixed_node.sceneBoundingRect().center())
        else:
            path.moveTo(fixed_node.sceneBoundingRect().center())
            path.lineTo(position)
        self._edge_preview = QGraphicsPathItem(path)
        self._edge_preview.setPen(QPen(edge.color, 3, Qt.PenStyle.DashLine))
        self._edge_preview.setZValue(999)
        self._edge_preview.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.addItem(self._edge_preview)

    def _update_endpoint_reconnect(self, position):
        edge, endpoint = self._edge_reconnect
        fixed_node = edge.end_node if endpoint == "start" else edge.start_node
        path = QPainterPath()
        if endpoint == "start":
            path.moveTo(position)
            path.lineTo(fixed_node.sceneBoundingRect().center())
        else:
            path.moveTo(fixed_node.sceneBoundingRect().center())
            path.lineTo(position)
        self._edge_preview.setPath(path)
        delta = position - self._edge_drag_start_pos
        self._edge_drag_moved = self._edge_drag_moved or (
            delta.x() ** 2 + delta.y() ** 2 >= 16
        )

    def _finish_endpoint_reconnect(self, position):
        edge, endpoint = self._edge_reconnect
        target = self.node_at(position)
        self._clear_edge_preview()
        self._edge_reconnect = None
        self._edge_dragging = False
        self._edge_drag_start_pos = None
        moved = self._edge_drag_moved
        self._edge_drag_moved = False

        fixed_node = edge.end_node if endpoint == "start" else edge.start_node
        if moved and target is not None and target is not fixed_node:
            if self.controller:
                self.controller.reconnect_edge(edge, endpoint, target)
            self._set_status(f"Reconnected edge {endpoint}")
        else:
            self._set_status("Edge reconnect cancelled")
        if self.win:
            self.win.inspectordock.update_inspector(self.get_the_selected_item())

    def begin_edge_drag(self, source, directed):
        if source is None or source.scene() is not self:
            return
        self.creating_edge = 0
        self.edge_nodes = [None, None]
        self._edge_drag_source = source
        self._edge_dragging = False
        self.directed_edge_mode = directed
        self._set_status("Drag from source node to target node")

    def _start_edge_drag(self, source, position):
        self._edge_drag_source = source
        self._edge_dragging = True
        self._edge_drag_start_pos = position
        self._edge_drag_moved = False
        preview_path = QPainterPath()
        preview_path.moveTo(source.sceneBoundingRect().center())
        preview_path.lineTo(position)
        self._edge_preview = QGraphicsPathItem(preview_path)
        self._edge_preview.setPen(QPen(self.current_color_edge, 3, Qt.PenStyle.DashLine))
        self._edge_preview.setZValue(-0.5)
        self._edge_preview.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.addItem(self._edge_preview)

    def _update_edge_preview(self, position):
        if self._edge_preview is None or self._edge_drag_source is None:
            return
        path = QPainterPath()
        path.moveTo(self._edge_drag_source.sceneBoundingRect().center())
        path.lineTo(position)
        self._edge_preview.setPath(path)
        if self._edge_drag_start_pos is not None:
            delta = position - self._edge_drag_start_pos
            self._edge_drag_moved = self._edge_drag_moved or (
                delta.x() ** 2 + delta.y() ** 2 >= 16
            )

    def _clear_edge_preview(self):
        if self._edge_preview is not None:
            self.removeItem(self._edge_preview)
            self._edge_preview = None

    def _create_edge(self, source, target):
        if not self.controller:
            return
        if self.directed_edge_mode:
            edge = DirectedEdgeItem(source, target, self.current_color_edge)
        else:
            edge = EdgeItem(source, target, self.current_color_edge)
        self.controller.add_node(self, edge)

    def _finish_edge_drag(self, target):
        source = self._edge_drag_source
        was_shortcut_mode = self.creating_edge != 0
        moved = self._edge_drag_moved
        self._clear_edge_preview()
        self._edge_dragging = False
        self._edge_drag_source = None
        self._edge_drag_start_pos = None
        self._edge_drag_moved = False

        if source is not None and target is not None and target is not source and moved:
            self._create_edge(source, target)
            self.creating_edge = 0
            self.edge_nodes = [None, None]
            self.directed_edge_mode = False
            self._set_status("idle")
        elif was_shortcut_mode and source is not None:
            self.edge_nodes = [source, None]
            self.creating_edge = 2
            self._set_status("Select a different target node")
        else:
            self.creating_edge = 0
            self.edge_nodes = [None, None]
            self.directed_edge_mode = False
            self._set_status("idle")
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_R:
            view = self.views()[0]
            mouse_pos = view.mapFromGlobal(QCursor.pos())
            pos = view.mapToScene(mouse_pos)

            self.add_rect(pos.x(), pos.y())
        elif event.key() == Qt.Key.Key_E:
            view = self.views()[0]
            mouse_pos = view.mapFromGlobal(QCursor.pos())
            pos = view.mapToScene(mouse_pos)

            self.add_ellipse(pos.x(), pos.y())
        # TODO repair triangle
        # elif event.key() == Qt.Key.Key_T:
        #     view = self.views()[0]
        #     mouse_pos = view.mapFromGlobal(QCursor.pos())
        #     pos = view.mapToScene(mouse_pos)

        #     self.add_triangle(pos.x(), pos.y())
        elif event.key() == Qt.Key.Key_1:
            self.color_dialog(0)
            return
        
        elif event.key() == Qt.Key.Key_2:
            self.color_dialog(1)
            return
        
        elif event.key() == Qt.Key.Key_I:
            view = self.views()[0]
            mouse_pos = view.mapFromGlobal(QCursor.pos())
            pos = view.mapToScene(mouse_pos)

            self.add_image(pos.x(), pos.y())
            return
        
        elif event.key() == Qt.Key.Key_L and event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.edge_create_dialog(True)
            return
        
        elif event.key() == Qt.Key.Key_L:
            self.edge_create_dialog(False)
            return
        
        elif event.key() == Qt.Key.Key_Escape:
            self._clear_edge_preview()
            self.creating_edge = 0
            self.edge_nodes = [None, None]
            self._edge_drag_source = None
            self._edge_dragging = False
            self._edge_drag_start_pos = None
            self._edge_drag_moved = False
            self._edge_reconnect = None
            self.directed_edge_mode = False
            self._set_status("idle")
            self.clearSelection()
            return
        
        elif event.key() == Qt.Key.Key_Delete:
            self.delete()
            return
        
        elif event.key() == Qt.Key.Key_S and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.save_file_dialog()
            return
        
        elif event.key() == Qt.Key.Key_O and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.load_popup()
            return
        
        elif event.key() == Qt.Key.Key_C and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.controller.clipboard.copy(self.selectedItems())
            return
        
        elif event.key() == Qt.Key.Key_V and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.controller.paste(self)
            return
        
        elif event.key() == Qt.Key.Key_X and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.controller.clipboard.copy(self.selectedItems())
            self.delete()
            return
        
        elif event.key() == Qt.Key.Key_D and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.controller.clipboard.copy(self.selectedItems())
            self.controller.paste(self)
            return
        super().keyPressEvent(event)
    
    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos(), QTransform())
        if (
            event.button() == Qt.MouseButton.LeftButton
            and isinstance(item, EdgeEndpointHandle)
        ):
            self._start_endpoint_reconnect(
                item.edge,
                item.endpoint,
                event.scenePos(),
            )
            event.accept()
            return

        if self._edge_drag_source is not None:
            if self.node_at(event.scenePos()) is self._edge_drag_source:
                self._start_edge_drag(self._edge_drag_source, event.scenePos())
                event.accept()
                return

        if self.creating_edge == 1:
            source = self.node_at(event.scenePos())
            if source is not None:
                self.edge_nodes[0] = source
                self.creating_edge = 2
                self._start_edge_drag(source, event.scenePos())
                event.accept()
                return

        self.old_pos_list = []
        self.itemlist = []
        for i in self.items():
            if isinstance(i, NodeItem):
                self.old_pos_list.append(i.pos())
                self.itemlist.append(i)
        super().mousePressEvent(event)
        if self.creating_edge == 2:
            target = self.node_at(event.scenePos())
            source = self.edge_nodes[0]
            if target is not None and source is not None and target is not source:
                self._create_edge(source, target)
            self.directed_edge_mode = False
            self.creating_edge = 0
            self.edge_nodes = [None, None]
            self._set_status("idle")

    def mouseMoveEvent(self, event):
        if self._edge_reconnect is not None:
            self._update_endpoint_reconnect(event.scenePos())
            event.accept()
            return
        if self._edge_dragging:
            self._update_edge_preview(event.scenePos())
            event.accept()
            return
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if self._edge_reconnect is not None:
            self._finish_endpoint_reconnect(event.scenePos())
            event.accept()
            return
        if self._edge_dragging:
            self._finish_edge_drag(self.node_at(event.scenePos()))
            event.accept()
            return

        super().mouseReleaseEvent(event)
        new_pos_list = []
        for i in self.items():
            if isinstance(i, NodeItem):
                new_pos_list.append(i.pos())
        if self.items() != []:
            for i in self.old_pos_list:
                if i != new_pos_list[self.old_pos_list.index(i)]:
                    self.controller.move_node(self.itemlist, self.old_pos_list, new_pos_list)
                    break
        self.win.inspectordock.update_inspector(self.get_the_selected_item())
    
    def delete(self):
        itemlist = []
        for item in self.selectedItems():
            if isinstance(item, NodeItem):
                for edge in item.edges[:]:
                    itemlist.append(edge)
                itemlist.append(item)
            elif isinstance(item, EdgeItem):
                itemlist.append(item)
        self.controller.delete_node(self, itemlist)

    def save_scene(self, online=False, filename=""):
        data = {
            "type": "full_state",
            "nodes": [],
            "edges": []
        }
        for item in self.items():
            if isinstance(item, NodeItem):
                data["nodes"].append(item.to_dict())

            elif isinstance(item, EdgeItem):
                data["edges"].append(item.to_dict())
        import json
        if online:
            return data
        else:
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)
    
    def load_scene(self, online=False, filename="", data={}):
        import json
        if not online:
            with open(filename, "r") as f:
                data = json.load(f)

        self.clear()
        id_map = {"nodes": {}, "edges": {}}

        for n in data["nodes"]:
            existing = self.find_node_by_id(n["id"])
            if not existing:
                node = self.create_node_from_data(n)
                id_map["nodes"][node.id] = node
                if self.controller and not online:
                    self.controller.add_node(self, node)
                elif online:
                    self.addItem(node)
            else:
                existing.update_from_data(n)

        for e in data["edges"]:
            existing = self.find_edge_by_id(e["id"])
            if not existing:
                e["start"] = id_map["nodes"][e["start"]]
                e["end"] = id_map["nodes"][e["end"]]
                edge = self.create_edge_from_data(e)
                edge.id = e["id"]
                id_map["edges"][edge.id] = edge
                if self.controller and not online:
                    self.controller.add_node(self, edge)
                elif online:
                    self.addItem(edge)

    def apply_delta(self, changes):
        if not isinstance(changes, dict):
            return
        if changes.get("type") == "nodes_added":
            for node_data in changes.get("nodes", []):
                if self.find_node_by_id(node_data["id"]) == None:
                    node = self.create_node_from_data(node_data)
                    if node:
                        self.addItem(node)
        
        elif changes.get("type") == "nodes_modified":
            for node_update in changes.get("nodes", []):
                node_id = node_update.get("id")
                node = self.find_node_by_id(node_id)
                if node:
                    if 'x' in node_update and 'y' in node_update:
                        node.setPos(node_update['x'], node_update['y'])
                    if 'z_value' in node_update:
                        node.setZValue(node_update['z_value'])
                    if 'color' in node_update:
                        node.apply_color(QColor(node_update['color'][0], node_update['color'][1], node_update['color'][2]))
                    if 'text_color' in node_update:
                        node.apply_text_color(QColor(*node_update['text_color']))
                    if 'text' in node_update and not isinstance(node, ImageNode):
                        node.text = node_update['text']
                        node.label.setPlainText(node_update['text'])
                        node.updateLabelPosition()
                    if 'width' in node_update and 'height' in node_update:
                        node.resize(node_update['height'], node_update['width'])
                    if 'custom_param' in node_update:
                        if isinstance(node, ImageNode):
                            node.load_image(node_update['custom_param'][0])
                    node.update()
        
        elif changes.get("type") == "nodes_and_edges_removed":
            for node_data in changes.get("nodes", []):
                node_id = node_data.get("id") if isinstance(node_data, dict) else node_data
                node = self.find_node_by_id(node_id)
                if node:
                    self.removeItem(node)
            for edge_data in changes.get("edges", []):
                edge_id = edge_data.get("id") if isinstance(edge_data, dict) else edge_data
                edge = self.find_edge_by_id(edge_id)
                if edge:
                    self.removeItem(edge)
        
        elif changes.get("type") == "edges_added":
            for edge_data in changes.get("edges", []):
                if self.find_edge_by_id(edge_data["id"]) == None:
                    edge_data["start"] = self.find_node_by_id(edge_data["start"])
                    edge_data["end"] = self.find_node_by_id(edge_data["end"])
                    if edge_data["start"] and edge_data["end"]:
                        edge = self.create_edge_from_data(edge_data)
                        self.addItem(edge)
        
        elif changes.get("type") == "edges_modified":
            for edge_update in changes.get("edges", []):
                edge_id = edge_update.get("id")
                edge = self.find_edge_by_id(edge_id)
                if edge:
                    if 'start' in edge_update:
                        start_node = self.find_node_by_id(edge_update['start'])
                        if start_node:
                            edge.set_endpoint("start", start_node)
                    if 'end' in edge_update:
                        end_node = self.find_node_by_id(edge_update['end'])
                        if end_node:
                            edge.set_endpoint("end", end_node)
                    if 'color' in edge_update:
                        edge.apply_color(QColor(edge_update['color'][0], edge_update['color'][1], edge_update['color'][2]))
                    if 'text_color' in edge_update:
                        edge.apply_text_color(QColor(*edge_update['text_color']))
                    if 'width' in edge_update:
                        edge.apply_width(edge_update['width'])
                    if 'text' in edge_update:
                        edge.apply_text(edge_update['text'])
                    if 'z_value' in edge_update:
                        edge.setZValue(edge_update['z_value'])
                    edge.update()
        
        elif changes.get("type") == "nodes_and_edges_added":
            for node_data in changes.get("nodes", []):
                if self.find_node_by_id(node_data["id"]) == None:
                    node = self.create_node_from_data(node_data)
                    if node:
                        self.addItem(node)
            for edge_data in changes.get("edges", []):
                if self.find_edge_by_id(edge_data["id"]) == None:
                    edge_data["start"] = self.find_node_by_id(edge_data["start"])
                    edge_data["end"] = self.find_node_by_id(edge_data["end"])
                    if edge_data["start"] and edge_data["end"]:
                        edge = self.create_edge_from_data(edge_data)
                        self.addItem(edge)

    def find_node_by_id(self, node_id):
        for item in self.items():
            if hasattr(item, 'id') and item.id == node_id:
                return item
        return None

    def find_edge_by_id(self, edge_id):
        for item in self.items():
            if isinstance(item, EdgeItem) and item.id == edge_id:
                return item
        return None

    def create_node_from_data(self, data):
        n_type = data.get('type', 'rect')

        if n_type == 'image':
            node = ImageNode(data["x"], data["y"], data["width"], data["height"], QColor(data["color"][0], data["color"][1], data["color"][2]), data.get("text", ""), data.get("custom_param", []))
        elif n_type == 'rect':
            node = NodeRect(data["x"], data["y"], data["width"], data["height"], QColor(data["color"][0], data["color"][1], data["color"][2]), data.get("text", ""), data.get("custom_param", []))
        elif n_type == 'ellipse':
            node = NodeEllipse(data["x"], data["y"], data["width"], data["height"], QColor(data["color"][0], data["color"][1], data["color"][2]), data.get("text", ""), data.get("custom_param", []))
        elif n_type == 'triangle':
            node = NodeTriangle(data["x"], data["y"], data["width"], data["height"], QColor(data["color"][0], data["color"][1], data["color"][2]), data.get("text", ""), data.get("custom_param", []))
        else:
            return None

        node.id = data["id"]
        node.setZValue(data.get('z_value', node.zValue()))
        if 'text_color' in data:
            node.apply_text_color(QColor(*data['text_color']))
        return node

    def create_edge_from_data(self, data):
        if data["directed"]:
            edge = DirectedEdgeItem(data["start"], data["end"], QColor(data["color"][0], data["color"][1], data["color"][2]), data["width"], text=data.get("text", ""))
        else:
            edge = EdgeItem(data["start"], data["end"], QColor(data["color"][0], data["color"][1], data["color"][2]), data["width"], text=data.get("text", ""))

        edge.id = data["id"]
        edge.setZValue(data.get('z_value', edge.zValue()))
        if 'text_color' in data:
            edge.apply_text_color(QColor(*data['text_color']))
        return edge
    
    def update_recent_files(self, filename):
        import json
        recent_files_path = get_recent_files_path()
        
        try:
            with open(recent_files_path, "r") as f:
                recent_files = json.load(f)
        except FileNotFoundError:
            recent_files = []
        
        if filename in recent_files:
            recent_files.remove(filename)
        recent_files.insert(0, filename)
        recent_files = recent_files[:10]

        with open(recent_files_path, "w") as f:
            json.dump(recent_files, f, indent=4)
    
    def get_the_selected_item(self):
        sel_items = []
        for item in self.selectedItems():
            if isinstance(item, NodeItem) or isinstance(item, EdgeItem):
                sel_items.append(item)

        if len(sel_items) == 1:
            return sel_items[0]
        else:
            return None

    def weighted_graph(self):
        g = {}
        for i in self.items():
            if isinstance(i, NodeItem):
                g[i] = []
            elif isinstance(i, EdgeItem):
                dist = i.laenge()
                g[i.start_node].append((i.end_node, dist))
                if not getattr(i, 'directed', False):
                    g[i.end_node].append((i.start_node, dist))
        return g

    def unweighted_graph(self):
        g = {}
        for i in self.items():
            if isinstance(i, NodeItem):
                g[i] = []
            elif isinstance(i, EdgeItem):
                g[i.start_node].append([i.end_node, 1])
                if not getattr(i, 'directed', False):
                    g[i.end_node].append([i.start_node, 1])
        return g
    
    def show_distance(self, text):
        self.win.calcdock.dist_label.setText(text)
    
    def compute_shortest(self, a, b, unweighted):
        if unweighted:
            g = self.unweighted_graph()
        else:
            g = self.weighted_graph()
        d, prev = shortest_path(g, a, b)
        if d is None:
            self.show_distance("No path found")
        else:
            self.show_distance(f"Distance: {round(d,2)}")

    def setup_path_compution(self, unweighted):
        if self.startnode and self.endnode and self.startnode in self.items() and self.endnode in self.items():
            self.compute_shortest(self.startnode, self.endnode, unweighted)
        else:
            self.show_distance("No nodes selected")