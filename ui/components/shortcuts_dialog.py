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
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QGuiApplication
from ui.theme import Theme


KEY_ICON_MAP = {
    "Ctrl": "keyboard_command_key",
    "Shift": "keyboard_shift",
    "Enter": "keyboard_return",
}


def _make_key_icon(icon_name, size=15):
    """Return a crisp icon label for a modifier key."""
    label = QLabel()
    label.setObjectName("shortcut_key_part")

    icon = Theme.get_icon(icon_name)
    screen = QGuiApplication.primaryScreen()
    ratio = screen.devicePixelRatio() if screen else 1.0
    pixmap = icon.pixmap(QSize(size, size), ratio)
    pixmap.setDevicePixelRatio(ratio)
    label.setPixmap(pixmap)
    label.setFixedSize(size, size)

    return label


class KeyBadge(QFrame):
    """Keycap-style badge rendering modifiers as icons."""

    def __init__(self, keys, parent=None):
        super().__init__(parent)
        self.setObjectName("shortcut_key")
        self.setToolTip(keys)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for i, part in enumerate(keys.split("+")):
            if i:
                sep = QLabel("+")
                sep.setObjectName("shortcut_key_part")
                sep.setFont(Theme.MONO_FONT)
                layout.addWidget(sep)

            icon_name = KEY_ICON_MAP.get(part)
            if icon_name:
                layout.addWidget(_make_key_icon(icon_name))
            else:
                part_lbl = QLabel(part)
                part_lbl.setObjectName("shortcut_key_part")
                part_lbl.setFont(Theme.MONO_FONT)
                layout.addWidget(part_lbl)


class ShortcutRow(QWidget):
    """One shortcut entry: key badge followed by its description."""

    def __init__(self, keys, description, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.key_badge = KeyBadge(keys)
        layout.addWidget(self.key_badge)

        desc_lbl = QLabel(description)
        desc_lbl.setObjectName("shortcut_desc")
        desc_lbl.setFont(Theme.FONT)
        desc_lbl.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        layout.addWidget(desc_lbl, 1)


class ShortcutsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("shortcuts_dialog")
        self.setWindowTitle("Keyboard Shortcuts")
        self.setFixedWidth(640)
        self.setMinimumHeight(460)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        scroll.setWidget(content)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(12)

        self._add_shortcuts_section(content_layout, "Project & File Commands", [
            ("Ctrl+N", "Create New Project"),
            ("Ctrl+O", "Open Project"),
            ("Ctrl+S", "Save Project"),
            ("Ctrl+Shift+S", "Save Project As..."),
            ("Ctrl+W", "Close Project"),
            ("Ctrl+I", "Import from CSV"),
            ("Ctrl+E", "Export as CSV"),
            ("F5", "Repack to .sta"),
            ("Ctrl+H", "Replace All"),
            ("Ctrl+Shift+H", "Replace All in Project"),
            ("Ctrl+P", "Apply Plugin"),
            ("Ctrl+Shift+P", "Remove Plugin"),
            ("F1", "Toggle Keyboard Shortcuts"),
            ("F3", "Focus Filter Field"),
        ])

        self._add_shortcuts_section(content_layout, "Undo & Redo", [
            ("Ctrl+Z", "Undo"),
            ("Ctrl+Y", "Redo"),
        ])

        self._add_shortcuts_section(content_layout, "Pane Focus & Switching", [
            ("Ctrl+1", "Focus File Tree"),
            ("Ctrl+2", "Focus String List"),
            ("Ctrl+3", "Focus Editor"),
            ("F6", "Next Pane"),
            ("Shift+F6", "Previous Pane"),
            ("Enter", "Edit Selected String"),
            ("Esc", "Leave Editor / String List"),
        ])

        self._add_shortcuts_section(content_layout, "Text Editing & Font", [
            ("Ctrl+Enter", "Next String Line"),
            ("Ctrl+Shift+Enter", "Previous String Line"),
            ("Ctrl+Shift+,", "Decrease Font size"),
            ("Ctrl+Shift+.", "Increase Font size"),
        ])

        content_layout.addStretch()
        layout.addWidget(scroll, 1)

        self._normalize_key_widths()

        container = QWidget()
        container.setObjectName("shortcuts_footer")
        btn_layout = QHBoxLayout(container)
        btn_layout.setContentsMargins(16, 12, 16, 12)
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

    def _normalize_key_widths(self):
        """Give every key badge the width of the widest shortcut."""
        badges = self.findChildren(KeyBadge)
        if not badges:
            return
        for badge in badges:
            badge.ensurePolished()
        width = max(badge.sizeHint().width() for badge in badges)
        for badge in badges:
            badge.setFixedWidth(width)

    def _add_shortcuts_section(self, parent_layout, title, shortcuts):
        section = QFrame()
        section.setObjectName("shortcuts_section")

        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(16, 12, 16, 14)
        section_layout.setSpacing(10)

        lbl = QLabel(title)
        lbl.setObjectName("section_label")
        lbl.setFont(Theme.FONT)
        section_layout.addWidget(lbl)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(28)
        grid.setVerticalSpacing(6)

        for i, (keys, description) in enumerate(shortcuts):
            row = ShortcutRow(keys, description)
            grid.addWidget(row, i // 2, i % 2)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        section_layout.addLayout(grid)

        parent_layout.addWidget(section)
