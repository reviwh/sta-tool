from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QWidget,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from ui.theme import Theme


class ShortcutsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("shortcuts_dialog")
        self.setWindowTitle("Keyboard Shortcuts")
        self.setFixedWidth(600)
        self.setMinimumHeight(400)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        scroll.setWidget(content)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(8)

        self._add_shortcuts_section(content_layout, "General Actions", [
            ("Ctrl+N", "Create New Project"),
            ("Ctrl+O", "Open Project"),
            ("Ctrl+S", "Save Project"),
            ("Ctrl+Shift+S", "Save Project As..."),
            ("Ctrl+W", "Close Project"),
            ("Ctrl+I", "Import from CSV"),
            ("Ctrl+E", "Export as CSV"),
            ("F5", "Repack to .sta"),
            ("Ctrl+H", "Replace All"),
            ("Ctrl+P", "Apply Plugin"),
            ("Ctrl+Shift+P", "Remove Plugin"),
            ("F1", "Toggle Keyboard Shortcuts"),
            ("F3", "Focus Filter Field"),
        ])

        self._add_shortcuts_section(content_layout, "Editor & Navigation", [
            ("Ctrl+Enter", "Next String Line"),
            ("Ctrl+Shift+Enter", "Previous String Line"),
            ("Ctrl+Shift+,", "Decrease Font size"),
            ("Ctrl+Shift+.", "Increase Font size"),
        ])

        content_layout.addStretch()
        layout.addWidget(scroll)

        layout.addStretch()

        container = QWidget()
        container.setObjectName("shortcuts_footer")
        btn_layout = QHBoxLayout(container)
        btn_layout.setContentsMargins(8, 8, 8, 8)
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setFont(Theme.FONT)
        close_btn.setIcon(Theme.get_icon("close"))
        close_btn.setIconSize(QSize(16, 16))
        close_btn.setAutoDefault(False)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addWidget(container)

    def _add_shortcuts_section(self, parent_layout, title, shortcuts):
        lbl = QLabel(title)
        lbl.setObjectName("section_label")
        lbl.setFont(Theme.FONT)
        parent_layout.addWidget(lbl)

        grid = QGridLayout()
        grid.setContentsMargins(8, 0, 0, 0)
        grid.setSpacing(4)

        for i, (keys, description) in enumerate(shortcuts):
            col = i % 2
            row = i // 2

            desc_lbl = QLabel(description)
            desc_lbl.setObjectName("shortcut_desc")
            desc_lbl.setFont(Theme.FONT)

            key_lbl = QLabel(keys)
            key_lbl.setObjectName("shortcut_key")
            key_lbl.setFont(Theme.MONO_FONT)

            grid.addWidget(desc_lbl, row, col * 2)
            grid.addWidget(key_lbl, row, col * 2 + 1)

        parent_layout.addLayout(grid)
