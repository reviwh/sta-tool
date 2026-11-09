from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize

from ui.theme import Theme


class RecentProjectRow(QFrame):
    """Clickable row that opens a recently used project."""

    clicked = pyqtSignal(str)

    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path
        self.setObjectName("recent_project_row")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setToolTip(path)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        self.icon_label = QLabel()
        self.icon_label.setObjectName("recent_icon")
        self.icon_label.setFixedSize(20, 20)
        layout.addWidget(self.icon_label)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(0)

        self.name_label = QLabel(Path(path).name)
        self.name_label.setObjectName("recent_name")
        self.name_label.setFont(Theme.FONT)
        text_layout.addWidget(self.name_label)

        self.path_label = QLabel(self._short_parent(path))
        self.path_label.setObjectName("recent_path")
        self.path_label.setFont(Theme.FONT)
        self.path_label.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
        )
        text_layout.addWidget(self.path_label)
        layout.addLayout(text_layout, 1)

        self.arrow_label = QLabel()
        self.arrow_label.setObjectName("recent_arrow")
        self.arrow_label.setFixedSize(16, 16)
        layout.addWidget(self.arrow_label)

        self.apply_theme()

    @staticmethod
    def _short_parent(path):
        parent = Path(path).parent
        parts = parent.parts
        if len(parts) > 2:
            return "…/" + "/".join(parts[-2:])
        return str(parent)

    def apply_theme(self):
        self.icon_label.setPixmap(Theme.get_icon("file").pixmap(QSize(20, 20)))
        self.arrow_label.setPixmap(
            Theme.get_icon("arrow_right").pixmap(QSize(16, 16))
        )
        self.name_label.setFont(Theme.FONT)
        self.path_label.setFont(Theme.FONT)

    def mouseReleaseEvent(self, event):
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.rect().contains(event.position().toPoint())
        ):
            self.clicked.emit(self.path)
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter,
            Qt.Key.Key_Space,
        ):
            self.clicked.emit(self.path)
            event.accept()
            return
        super().keyPressEvent(event)


class WelcomePanel(QWidget):
    extract_requested = pyqtSignal()
    load_requested = pyqtSignal()
    recent_project_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._recent_rows = []
        self.init_ui()

    def init_ui(self):
        self.layout_target = QVBoxLayout(self)
        self.layout_target.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_target.setSpacing(0)

        self.container = QFrame()
        self.container.setObjectName("welcome_container")
        self.container.setFixedWidth(560)

        self.c_layout = QVBoxLayout(self.container)
        self.c_layout.setContentsMargins(36, 32, 36, 28)
        self.c_layout.setSpacing(14)

        self.title = QLabel("Welcome to STA Translator")
        self.title.setObjectName("welcome_title")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(Theme.FONT)
        self.c_layout.addWidget(self.title)

        self.desc = QLabel(
            "Extract translatable strings from .sta game files\n"
            "or open an existing project to continue translating."
        )
        self.desc.setObjectName("welcome_desc")
        self.desc.setFont(Theme.FONT)
        self.desc.setWordWrap(True)
        self.desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.c_layout.addWidget(self.desc)

        self.c_layout.addSpacing(4)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.btn_extract = QPushButton(" Create New Project")
        self.btn_extract.setObjectName("btn_extract")
        self.btn_extract.setFont(Theme.FONT)
        self.btn_extract.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_extract.setFixedHeight(44)
        self.btn_extract.setDefault(True)
        self.btn_extract.clicked.connect(self.extract_requested.emit)
        btn_layout.addWidget(self.btn_extract)

        self.btn_load = QPushButton(" Open Existing Project")
        self.btn_load.setObjectName("btn_load")
        self.btn_load.setFont(Theme.FONT)
        self.btn_load.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_load.setFixedHeight(44)
        self.btn_load.clicked.connect(self.load_requested.emit)
        btn_layout.addWidget(self.btn_load)

        self.c_layout.addLayout(btn_layout)

        self.recent_section = QWidget()
        self.recent_section.setObjectName("recent_section")
        recent_layout = QVBoxLayout(self.recent_section)
        recent_layout.setContentsMargins(0, 6, 0, 0)
        recent_layout.setSpacing(4)

        self.recent_label = QLabel("RECENT PROJECTS")
        self.recent_label.setObjectName("welcome_section")
        self.recent_label.setFont(Theme.FONT)
        recent_layout.addWidget(self.recent_label)

        self.recent_rows_layout = QVBoxLayout()
        self.recent_rows_layout.setContentsMargins(0, 0, 0, 0)
        self.recent_rows_layout.setSpacing(2)
        recent_layout.addLayout(self.recent_rows_layout)

        self.c_layout.addWidget(self.recent_section)
        self.recent_section.setVisible(False)

        self.side_footer = QLabel(
            "Ctrl+N  New Project     Ctrl+O  Open Project     F1  Shortcuts"
        )
        self.side_footer.setObjectName("welcome_footer")
        self.side_footer.setFont(Theme.FONT)
        self.side_footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.c_layout.addWidget(self.side_footer)

        self.layout_target.addWidget(self.container)
        self.apply_theme()

    def set_recent_projects(self, paths):
        """Rebuild the recent projects list (hidden when it is empty)."""
        while self.recent_rows_layout.count():
            item = self.recent_rows_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self._recent_rows = []
        for path in paths:
            row = RecentProjectRow(path)
            row.clicked.connect(self.recent_project_requested.emit)
            self.recent_rows_layout.addWidget(row)
            self._recent_rows.append(row)

        self.recent_section.setVisible(bool(paths))

    def apply_theme(self):
        icon_size = QSize(20, 20)
        self.btn_extract.setIcon(Theme.get_primary_icon("file_add"))
        self.btn_extract.setIconSize(icon_size)
        self.btn_load.setIcon(Theme.get_icon("file_open"))
        self.btn_load.setIconSize(icon_size)

        for row in self._recent_rows:
            row.apply_theme()
