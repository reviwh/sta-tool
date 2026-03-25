from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont
import os
from ui.theme import Theme


class WelcomePanel(QWidget):
    extract_requested = pyqtSignal()
    load_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.layout_target = QVBoxLayout(self)
        self.layout_target.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_target.setSpacing(20)

        # Container for content
        self.container = QFrame()
        self.container.setFixedWidth(500)

        self.c_layout = QVBoxLayout(self.container)
        self.c_layout.setContentsMargins(40, 40, 40, 40)
        self.c_layout.setSpacing(20)

        # Title
        self.title = QLabel("Welcome to STA Translator")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(Theme.FONT)
        self.c_layout.addWidget(self.title)

        # Description
        self.desc = QLabel(
            "Extract strings from .sta game files or open an \nexisting project to start translating."
        )
        self.desc.setFont(Theme.FONT)
        self.desc.setWordWrap(True)
        self.desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.c_layout.addWidget(self.desc)

        # Buttons Horizontal Layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.btn_extract = QPushButton(" Create New Project")
        self.btn_extract.setFont(Theme.FONT)
        self.btn_extract.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_extract.setFixedHeight(45)
        self.btn_extract.clicked.connect(self.extract_requested.emit)
        btn_layout.addWidget(self.btn_extract)

        self.btn_load = QPushButton(" Open Existing Project")
        self.btn_load.setFont(Theme.FONT)
        self.btn_load.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_load.setFixedHeight(45)
        self.btn_load.clicked.connect(self.load_requested.emit)
        btn_layout.addWidget(self.btn_load)

        self.c_layout.addLayout(btn_layout)

        # Footer info
        self.side_footer = QLabel("Shortcut: Ctrl+N for New, Ctrl+O for Open")
        self.side_footer.setFont(Theme.FONT)
        self.side_footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.c_layout.addWidget(self.side_footer)

        self.layout_target.addWidget(self.container)
        self.apply_theme()

    def apply_theme(self):
        self.container.setStyleSheet(
            f"background-color: {Theme.BG_CONTAINER}; border-radius: 12px; border: 1px solid {Theme.BORDER};"
        )
        self.title.setStyleSheet(
            f"font-size: 18pt; font-weight: 500; color: {Theme.PRIMARY}; border: none; background: transparent;"
        )
        self.desc.setStyleSheet(
            f"color: {Theme.TEXT_MAIN}; border: none; background: transparent;"
        )
        self.side_footer.setStyleSheet(
            f"color: {Theme.TEXT_SECONDARY}; border: none; font-size: 8pt; margin-top: 10px; background: transparent;"
        )

        icon_size = QSize(24, 24)
        button_style = f"""
            QPushButton {{
                color: {Theme.TEXT_MAIN}; 
                border-color: {Theme.TEXT_MAIN};
            }}
            QPushButton:hover {{
                background-color: {Theme.HOVER};
            }}
        """
        self.btn_extract.setIcon(Theme.get_icon("file_add"))
        self.btn_extract.setIconSize(icon_size)
        self.btn_extract.setStyleSheet(button_style)

        self.btn_load.setIcon(Theme.get_icon("file_open"))
        self.btn_load.setIconSize(icon_size)
        self.btn_load.setStyleSheet(button_style)
