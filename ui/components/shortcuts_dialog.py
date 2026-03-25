import os
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QWidget,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QKeySequence, QIcon
from ui.theme import Theme
from core.utils import resource_path


class ShortcutsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Application Shortcuts")
        self.setFixedWidth(450)
        self.setMinimumHeight(400)

        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Scroll Area for shortcuts
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        scroll.setWidget(content)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(4)

        # Section: General
        self._add_section(content_layout, "General Actions")
        self._add_shortcut(content_layout, "Ctrl+N", "Create New Project")
        self._add_shortcut(content_layout, "Ctrl+O", "Open Project")
        self._add_shortcut(content_layout, "Ctrl+S", "Save Project")
        self._add_shortcut(content_layout, "Ctrl+Shift+S", "Save Project As...")
        self._add_shortcut(content_layout, "Ctrl+W", "Close Project")
        self._add_shortcut(content_layout, "F5", "Repack to .sta")
        self._add_shortcut(content_layout, "Ctrl+P", "Plugin Management")
        self._add_shortcut(content_layout, "Ctrl+H", "Toggle Help / Shortcuts")

        content_layout.addSpacing(8)

        # Section: Editor
        self._add_section(content_layout, "Editor & Navigation")
        self._add_shortcut(content_layout, "Ctrl+Enter", "Next String Line")
        self._add_shortcut(content_layout, "Ctrl+Shift+Enter", "Previous String Line")
        self._add_shortcut(content_layout, "Ctrl+Shift+,", "Decrease Font size")
        self._add_shortcut(content_layout, "Ctrl+Shift+.", "Increase Font size")

        content_layout.addStretch()
        layout.addWidget(scroll)

        layout.addStretch()

        # Close Button
        container = QWidget()
        container.setStyleSheet(
            f"background-color: {Theme.BG_CONTAINER}; border-top: 1px solid {Theme.BORDER}"
        )
        btn_layout = QHBoxLayout(container)
        btn_layout.setContentsMargins(8, 8, 8, 8)
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setFont(Theme.FONT)
        close_btn.setIcon(QIcon(resource_path("assets/icons/white/close.svg")))
        close_btn.setIconSize(QSize(16, 16))
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(Theme.DEFAULT_BUTTON_STYLE)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addWidget(container)

    def apply_theme(self):
        self.setStyleSheet(
            f"QDialog {{ background-color: {Theme.BG_APP}; color: {Theme.TEXT_MAIN};}}"
        )
        # Apply to children specifically if needed, but setStyleSheet on self should propagate mostly
        self.apply_global_styles()

    def apply_global_styles(self):
        # Apply Scrollbar style to possible scroll areas
        for scroll in self.findChildren(QScrollArea):
            scroll.verticalScrollBar().setStyleSheet(Theme.SCROLLBAR_STYLE)
            scroll.horizontalScrollBar().setStyleSheet(Theme.SCROLLBAR_STYLE)
            scroll.setStyleSheet(
                "QScrollArea { border: none; background-color: transparent; }"
            )

    def _add_section(self, layout, title):
        lbl = QLabel(title)
        lbl.setFont(Theme.FONT)
        lbl.setStyleSheet(
            f"QLabel {{ color: {Theme.PRIMARY}; font-weight: 500; font-size: 11pt; background-color: transparent; }}"
        )
        layout.addWidget(lbl)

    def _add_shortcut(self, layout, keys, description):
        row = QHBoxLayout()
        row.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        row.addSpacing(8)

        key_lbl = QLabel(keys)
        key_lbl.setFont(Theme.MONO_FONT)
        key_lbl.setStyleSheet(
            f"""
            border: 1px solid {Theme.BORDER};
            background-color: {Theme.SECONDARY_BG_COLOR};
            color: {Theme.TEXT_MAIN};
            border-radius: 4px;
            padding: 2px 6px;
            font-weight: bold;
            """
        )

        desc_lbl = QLabel(description)
        desc_lbl.setFont(Theme.FONT)
        desc_lbl.setStyleSheet(
            f"color: {Theme.TEXT_MAIN}; background-color: transparent;"
        )

        row.addWidget(desc_lbl, 1)
        row.addWidget(key_lbl)
        layout.addLayout(row)
