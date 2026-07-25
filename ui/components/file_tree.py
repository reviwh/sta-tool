from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QTreeView,
    QAbstractItemView,
    QPushButton,
    QHBoxLayout,
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon, QFont, QAction, QColor
from PyQt6.QtCore import pyqtSignal, Qt, QTimer, QModelIndex, QSize
from pathlib import Path
import os
from ui.theme import Theme


class FileTreeComponent(QWidget):
    file_selected = pyqtSignal(int)
    filter_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("file_tree")
        self.setMinimumWidth(100)
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.execute_filter)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # 1. Search & Filter Header
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(Theme.SPACING)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter files...")
        self.search_input.setFont(Theme.FONT)
        self.search_input.textChanged.connect(self._on_search_changed)

        search_icon = QIcon(Theme.get_icon("search"))
        self.search_input.addAction(
            search_icon, QLineEdit.ActionPosition.LeadingPosition
        )

        search_layout.addWidget(self.search_input)

        self.warn_btn = QPushButton()
        self.warn_btn.setIcon(Theme.get_icon("warning"))
        self.warn_btn.setIconSize(QSize(20, 20))
        self.warn_btn.setFixedSize(28, 28)
        self.warn_btn.setCheckable(True)
        self.warn_btn.setToolTip("Show files with empty translations (warnings)")
        self.warn_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.warn_btn.clicked.connect(self.execute_filter)
        self.warn_btn.setStyleSheet(
            f"""
            QPushButton {{ 
                border: 1px solid {Theme.BORDER};
                border-radius: 4px; 
                background: transparent;
            }}
            QPushButton:checked {{ 
                background: {Theme.WARNING}; 
                border: none;
            }}
        """
        )
        search_layout.addWidget(self.warn_btn)

        layout.addLayout(search_layout)

        # 2. Tree View
        self.tree_view = QTreeView()
        self.tree_view.setFont(Theme.FONT)
        self.tree_view.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.model = QStandardItemModel()
        self.tree_view.setModel(self.model)
        layout.addWidget(self.tree_view)

        self.tree_view.clicked.connect(self._handle_click)
        self.tree_view.expanded.connect(self._on_expanded)
        self.tree_view.collapsed.connect(self._on_collapsed)

        self.apply_theme()

    def _on_expanded(self, index):
        item = self.model.itemFromIndex(index)
        if item and item.data(Qt.ItemDataRole.UserRole) == -1:
            item.setIcon(Theme.get_icon("folder_open"))

    def _on_collapsed(self, index):
        item = self.model.itemFromIndex(index)
        if item and item.data(Qt.ItemDataRole.UserRole) == -1:
            item.setIcon(Theme.get_icon("folder"))

    def update_current_file_text(self, file_idx, entries):
        """Update text and background real-time."""
        total = len(entries)
        done = sum(1 for e in entries if len(e.get("translated", "").strip()) > 0)
        percentage = int((done / total) * 100) if total > 0 else 0

        items = self.model.findItems(
            "", Qt.MatchFlag.MatchContains | Qt.MatchFlag.MatchRecursive
        )
        for item in items:
            data_role = item.data(Qt.ItemDataRole.UserRole)
            if data_role == file_idx:
                base_name = item.text().split(" (")[0]
                item.setText(f"{base_name} ({percentage}%)")
                item.setBackground(QColor(Theme.PRIMARY_BG_COLOR))
            elif data_role is not None and data_role != -1:
                item.setBackground(QColor(Theme.TRANSPARENT))

    def get_search_text(self):
        return self.search_input.text()

    def is_warning_filter_active(self):
        return self.warn_btn.isChecked()

    def execute_filter(self):
        self.filter_changed.emit()

    def _on_search_changed(self):
        self.search_timer.start(500)

    def _handle_click(self, index):
        item = self.model.itemFromIndex(index)
        data_idx = item.data(Qt.ItemDataRole.UserRole)

        if data_idx == -1:
            self.tree_view.setExpanded(index, not self.tree_view.isExpanded(index))
        else:
            self.file_selected.emit(data_idx)

    def set_data(self, visible_files, raw_data, active_idx=-1):
        expanded_paths = set()
        self._save_expanded_state(QModelIndex(), expanded_paths)

        v_scroll = self.tree_view.verticalScrollBar().value()
        h_scroll = self.tree_view.horizontalScrollBar().value()

        self.model.clear()
        self.model.setHorizontalHeaderLabels(["Project Files"])
        root_node = self.model.invisibleRootItem()

        folder_icon = Theme.get_icon("folder")
        file_icon = Theme.get_icon("file")
        nodes = {}

        for i, item in enumerate(raw_data):
            f_path = item["file_path"]
            if f_path not in visible_files:
                continue

            parts = Path(f_path).parts
            current_node = root_node

            # skip the root folder (first part of the path)
            display_parts = parts[1:] if len(parts) > 1 else parts
            for j, part in enumerate(display_parts):
                path_key = "/".join(display_parts[: j + 1])
                is_last = j == len(display_parts) - 1

                if path_key not in nodes:
                    display_text = part
                    if is_last:
                        total = len(item["entries"])
                        done = sum(
                            1
                            for e in item["entries"]
                            if len(e.get("translated", "").strip()) > 0
                        )
                        percentage = int((done / total) * 100) if total > 0 else 0
                        display_text = f"{part} ({percentage}%)"

                    new_item = QStandardItem(display_text)
                    new_item.setData(i if is_last else -1, Qt.ItemDataRole.UserRole)
                    new_item.setEditable(False)

                    if part.endswith(".sta"):
                        new_item.setIcon(file_icon)
                        if i == active_idx:
                            new_item.setBackground(QColor(Theme.PRIMARY_BG_COLOR))
                    else:
                        new_item.setIcon(folder_icon)

                    current_node.appendRow(new_item)
                    nodes[path_key] = new_item

                current_node = nodes[path_key]

        self._sort_node(root_node)
        self._restore_expanded_state(QModelIndex(), expanded_paths)

        self.tree_view.verticalScrollBar().setValue(v_scroll)
        self.tree_view.horizontalScrollBar().setValue(h_scroll)

    def _sort_node(self, node):
        items = []
        for i in range(node.rowCount()):
            items.append(node.takeRow(0)[0])

        items.sort(
            key=lambda x: (x.data(Qt.ItemDataRole.UserRole) != -1, x.text().lower())
        )

        for item in items:
            node.appendRow(item)
            self._sort_node(item)

    def _on_search_changed(self):
        self.search_timer.start(500)

    def execute_filter(self):
        # Notify MainWindow via window() access
        parent = self.window()
        if parent and hasattr(parent, "on_filter_changed"):
            parent.on_filter_changed()

    def get_search_text(self):
        return self.search_input.text()

    def is_warning_filter_active(self):
        return self.warn_btn.isChecked()

    def _save_expanded_state(self, index, expanded_set, current_path=""):
        for i in range(self.model.rowCount(index)):
            child = self.model.index(i, 0, index)
            if self.tree_view.isExpanded(child):
                item = self.model.itemFromIndex(child)
                clean_text = item.text().split(" (")[0]
                full_key = (
                    f"{current_path}/{clean_text}" if current_path else clean_text
                )
                expanded_set.add(full_key)
                self._save_expanded_state(child, expanded_set, full_key)

    def _restore_expanded_state(self, index, expanded_set, current_path=""):
        for i in range(self.model.rowCount(index)):
            child = self.model.index(i, 0, index)
            item = self.model.itemFromIndex(child)
            clean_text = item.text().split(" (")[0]
            full_key = f"{current_path}/{clean_text}" if current_path else clean_text

            if full_key in expanded_set:
                self.tree_view.setExpanded(child, True)
                if item.data(Qt.ItemDataRole.UserRole) == -1:
                    item.setIcon(Theme.get_icon("folder_open"))
            self._restore_expanded_state(child, expanded_set, full_key)

    def apply_theme(self):
        search_icon = Theme.get_icon("search")
        for action in self.search_input.actions():
            self.search_input.removeAction(action)
        self.search_input.addAction(
            search_icon, QLineEdit.ActionPosition.LeadingPosition
        )

        self.warn_btn.setIcon(Theme.get_icon("warning"))

        def update_icons(index):
            for i in range(self.model.rowCount(index)):
                child_idx = self.model.index(i, 0, index)
                item = self.model.itemFromIndex(child_idx)
                if item.data(Qt.ItemDataRole.UserRole) == -1:
                    icon_name = (
                        "folder_open"
                        if self.tree_view.isExpanded(child_idx)
                        else "folder"
                    )
                    item.setIcon(Theme.get_icon(icon_name))
                else:
                    item.setIcon(Theme.get_icon("file"))
                update_icons(child_idx)

        update_icons(QModelIndex())
