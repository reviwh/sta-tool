from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
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

        self.container = QFrame()
        self.container.setObjectName("welcome_container")
        self.container.setFixedWidth(500)

        self.c_layout = QVBoxLayout(self.container)
        self.c_layout.setContentsMargins(40, 40, 40, 40)
        self.c_layout.setSpacing(20)

        self.title = QLabel("Welcome to STA Translator")
        self.title.setObjectName("welcome_title")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(Theme.FONT)
        self.c_layout.addWidget(self.title)

        self.desc = QLabel(
            "Extract translatable strings from .sta game files \nor open an existing project to continue translating."
        )
        self.desc.setObjectName("welcome_desc")
        self.desc.setFont(Theme.FONT)
        self.desc.setWordWrap(True)
        self.desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.c_layout.addWidget(self.desc)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.btn_extract = QPushButton(" Create New Project")
        self.btn_extract.setObjectName("btn_extract")
        self.btn_extract.setFont(Theme.FONT)
        self.btn_extract.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_extract.setFixedHeight(45)
        self.btn_extract.clicked.connect(self.extract_requested.emit)
        btn_layout.addWidget(self.btn_extract)

        self.btn_load = QPushButton(" Open Existing Project")
        self.btn_load.setObjectName("btn_load")
        self.btn_load.setFont(Theme.FONT)
        self.btn_load.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_load.setFixedHeight(45)
        self.btn_load.clicked.connect(self.load_requested.emit)
        btn_layout.addWidget(self.btn_load)

        self.c_layout.addLayout(btn_layout)

        self.side_footer = QLabel("New Project: Ctrl+N  |  Open Project: Ctrl+O")
        self.side_footer.setObjectName("welcome_footer")
        self.side_footer.setFont(Theme.FONT)
        self.side_footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.c_layout.addWidget(self.side_footer)

        self.layout_target.addWidget(self.container)
        self.apply_theme()

    def apply_theme(self):
        icon_size = QSize(24, 24)
        self.btn_extract.setIcon(Theme.get_primary_icon("file_add"))
        self.btn_extract.setIconSize(icon_size)

        self.btn_load.setIcon(Theme.get_primary_icon("file_open"))
        self.btn_load.setIconSize(icon_size)
