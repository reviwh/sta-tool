from pathlib import Path
from ui.theme import Theme
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QPushButton,
)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QColor
import os


class StringListComponent(QWidget):
    string_selected = pyqtSignal(int)
    request_focus_editor = pyqtSignal()
    import_txt_requested = pyqtSignal()
    replace_all_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(640)
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.path_label = QLabel("Select a file...")
        self.path_label.setObjectName("path_label")
        self.path_label.setFont(Theme.FONT)
        self.path_label.setVisible(False)

        icon_size = QSize(16, 16)

        self.btn_import_txt = QPushButton(" Import TXT")
        self.btn_import_txt.setIcon(Theme.get_icon("txt_import"))
        self.btn_import_txt.setIconSize(icon_size)
        self.btn_import_txt.setToolTip(
            "Import translations from a line-separated .txt file"
        )
        self.btn_import_txt.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_import_txt.clicked.connect(self.import_txt_requested.emit)

        self.btn_replace_all = QPushButton(" Replace All")
        self.btn_replace_all.setIcon(Theme.get_icon("find_replace"))
        self.btn_replace_all.setIconSize(icon_size)
        self.btn_replace_all.setToolTip(
            "Search and replace text across all entries (in current file)"
        )
        self.btn_replace_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_replace_all.clicked.connect(self.replace_all_requested.emit)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(8, 8, 8, 8)
        header_layout.setSpacing(8)
        header_layout.addWidget(self.path_label)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_import_txt)
        header_layout.addWidget(self.btn_replace_all)
        layout.addLayout(header_layout)

        self.list_widget = QListWidget()
        self.list_widget.setFont(Theme.FONT)
        self.list_widget.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.list_widget)

        self.list_widget.currentRowChanged.connect(self._on_row_changed)
        self.list_widget.itemDoubleClicked.connect(
            lambda: self.request_focus_editor.emit()
        )

    def _truncated_text(self, text):
        return (text[:50] + "...") if len(text) > 50 else text

    def update_item_color(self, row_idx, text):
        item = self.list_widget.item(row_idx)
        if not item:
            return
        if len(text.strip()) > 0:
            item.setBackground(QColor(Theme.SUCCESS_BG_COLOR))
        elif len(text) > 0 and len(text.strip()) == 0:
            item.setBackground(QColor(Theme.WARNING_BG_COLOR))
        else:
            item.setBackground(QColor(Theme.TRANSPARENT))

    def set_strings(self, filtered_items):
        self.list_widget.clear()
        for real_idx, entry in filtered_items:
            trans = entry.get("translated", "")
            has_strip = len(trans.strip()) > 0
            has_raw = len(trans) > 0

            trans = trans if has_strip else entry["original"]
            txt = trans.replace("\\n", " ")
            display = self._truncated_text(txt)

            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, real_idx)
            item.setData(Qt.ItemDataRole.UserRole + 1, entry["original"])
            if "\\n" in trans or len(trans) > 50:
                item.setToolTip(trans.replace("\\n", "\n"))

            if has_strip:
                item.setData(
                    Qt.ItemDataRole.BackgroundRole, QColor(Theme.SUCCESS_BG_COLOR)
                )
            elif has_raw:
                item.setData(
                    Qt.ItemDataRole.BackgroundRole, QColor(Theme.WARNING_BG_COLOR)
                )

            self.list_widget.addItem(item)

    def update_item_text(self, row, text):
        item = self.list_widget.item(row)
        if not item:
            return
        if not text.strip():
            orig = item.data(Qt.ItemDataRole.UserRole + 1)
            txt = orig.replace("\\n", " ")
        else:
            txt = text.replace("\\n", " ")
        display = self._truncated_text(txt)
        item.setText(display)

    def _on_row_changed(self, row_idx):
        if row_idx < 0:
            return
        item = self.list_widget.item(row_idx)
        real_idx = item.data(Qt.ItemDataRole.UserRole)
        self.string_selected.emit(real_idx)

    def apply_font(self, font_name, font_size=10):
        font = QFont(font_name, font_size)
        self.list_widget.setFont(font)
        self.path_label.setFont(font)
        self.btn_import_txt.setFont(font)
        self.btn_replace_all.setFont(font)

    def set_file_path(self, path):
        parts = Path(path).parts
        if len(parts) > 1:
            display_path = "/".join(parts[1:])
        else:
            display_path = path
        self.path_label.setText(display_path)
        is_placeholder = path == "Select a file..." or not path
        self.path_label.setVisible(not is_placeholder)

    def apply_theme(self):
        self.btn_import_txt.setIcon(Theme.get_icon("txt_import"))
        self.btn_replace_all.setIcon(Theme.get_icon("find_replace"))
