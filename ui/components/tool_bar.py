from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
)
from PyQt6.QtCore import pyqtSignal, QSize, Qt
from PyQt6.QtGui import QIcon, QPixmap, QFont
import os
from ui.theme import Theme


class ToolBarComponent(QWidget):
    remove_plugin_requested = pyqtSignal()
    theme_changed = pyqtSignal()
    export_csv_requested = pyqtSignal()
    import_csv_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Active Project Info
        self.status_container = QWidget()
        self.status_layout = QHBoxLayout(self.status_container)
        self.status_layout.setSpacing(Theme.SPACING)

        # Baris Tombol
        self.nav_layout = QHBoxLayout()
        self.nav_layout.setContentsMargins(8, 8, 8, 8)
        self.nav_layout.setSpacing(Theme.SPACING)

        self.btn_save = QPushButton(" Save")
        self.btn_save.setToolTip("Save current project")
        self.btn_save_as = QPushButton(" Save As")
        self.btn_save_as.setToolTip("Save current project as a new project")
        self.btn_close = QPushButton(" Close Project")
        self.btn_close.setToolTip("Close current project")
        self.btn_repack = QPushButton(" Repack")
        self.btn_repack.setToolTip("Repack current project")
        self.btn_apply_plugin = QPushButton(" Apply Plugin")
        self.btn_apply_plugin.setToolTip("Apply plugin to current project")
        self.btn_close_plugin = QPushButton(" Close Plugin")
        self.btn_close_plugin.setToolTip("Close plugin from current project")
        self.btn_shortcuts = QPushButton(" Shortcuts")
        self.btn_shortcuts.setToolTip("Open shortcuts dialog")

        self.btn_export_csv = QPushButton(" Export CSV")
        self.btn_export_csv.setToolTip("Export all entries to CSV file")

        self.btn_import_csv = QPushButton(" Import CSV")
        self.btn_import_csv.setToolTip("Import translations from CSV file")

        # Theme Toggle Button
        self.btn_theme_toggle = QPushButton()
        self.btn_theme_toggle.setFont(Theme.FONT)
        self.btn_theme_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme_toggle.setToolTip(
            f"Switch to {'Light' if Theme.current_mode == Theme.MODE_DARK else 'Dark'} Mode"
        )
        self.btn_theme_toggle.clicked.connect(self.theme_changed.emit)

        self.btn_close_plugin.clicked.connect(self.remove_plugin_requested.emit)

        for btn in [
            self.btn_save,
            self.btn_save_as,
            self.btn_close,
            self.btn_repack,
            self.btn_apply_plugin,
            self.btn_close_plugin,
        ]:
            btn.setFont(Theme.FONT)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.nav_layout.addWidget(btn)

        self.btn_export_csv.setFont(Theme.FONT)
        self.btn_export_csv.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export_csv.clicked.connect(self.export_csv_requested.emit)
        self.nav_layout.addWidget(self.btn_export_csv)

        self.btn_import_csv.setFont(Theme.FONT)
        self.btn_import_csv.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_import_csv.clicked.connect(self.import_csv_requested.emit)
        self.nav_layout.addWidget(self.btn_import_csv)

        self.nav_layout.addStretch()

        for btn in [
            self.btn_theme_toggle,
            self.btn_shortcuts,
        ]:
            btn.setFont(Theme.FONT)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.nav_layout.addWidget(btn)

        layout.addLayout(self.nav_layout)

        self.line = QFrame()
        self.line.setFixedHeight(1)
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setStyleSheet(f"color: {Theme.BORDER};")
        layout.addWidget(self.line)

        self.apply_theme()

    def update_state(
        self, active, project_name="", project_path="", has_plugin=False, is_dirty=False
    ):
        title_suffix = " *" if is_dirty else ""
        self.setWindowTitle(f"STA Tools - {project_name}{title_suffix}")

        self.btn_save.setVisible(active)
        self.btn_save_as.setVisible(active)
        self.btn_close.setVisible(active)
        self.btn_repack.setVisible(active)
        self.btn_apply_plugin.setVisible(active)
        self.btn_close_plugin.setVisible(active and has_plugin)
        self.btn_export_csv.setVisible(active)
        self.btn_import_csv.setVisible(active)
        self.btn_shortcuts.setVisible(True)
        self.apply_theme(has_plugin)

        if has_plugin:
            self.btn_apply_plugin.setText(" Change Plugin")
            self.btn_apply_plugin.setIcon(Theme.get_icon("attach_file_replace"))
            self.btn_apply_plugin.setToolTip("Change plugin from current project")
        else:
            self.btn_apply_plugin.setText(" Apply Plugin")
            self.btn_apply_plugin.setIcon(Theme.get_icon("attach_file_add"))
            self.btn_apply_plugin.setToolTip("Apply plugin to current project")

    def apply_theme(self, has_plugin=False):
        icon_size = QSize(16, 16)

        self.btn_save.setIcon(Theme.get_icon("save"))
        self.btn_save.setIconSize(icon_size)

        self.btn_save_as.setIcon(Theme.get_icon("save_as"))
        self.btn_save_as.setIconSize(icon_size)

        self.btn_close.setIcon(Theme.get_icon("file_close"))
        self.btn_close.setIconSize(icon_size)

        self.btn_repack.setIcon(Theme.get_icon("archive"))
        self.btn_repack.setIconSize(icon_size)

        if has_plugin:
            self.btn_apply_plugin.setIcon(Theme.get_icon("attach_file_replace"))
        else:
            self.btn_apply_plugin.setIcon(Theme.get_icon("attach_file_add"))
        self.btn_apply_plugin.setIconSize(icon_size)

        self.btn_close_plugin.setIcon(Theme.get_icon("attach_file_close"))
        self.btn_close_plugin.setIconSize(icon_size)

        self.btn_shortcuts.setIcon(Theme.get_icon("keyboard_command_key"))
        self.btn_shortcuts.setIconSize(icon_size)

        self.btn_export_csv.setIcon(Theme.get_icon("csv_export"))
        self.btn_export_csv.setIconSize(icon_size)

        self.btn_import_csv.setIcon(Theme.get_icon("csv_import"))
        self.btn_import_csv.setIconSize(icon_size)

        theme_icon = (
            "light_mode" if Theme.current_mode == Theme.MODE_DARK else "dark_mode"
        )
        self.btn_theme_toggle.setText(
            " Light Mode" if Theme.current_mode == Theme.MODE_DARK else " Dark Mode"
        )
        self.btn_theme_toggle.setIcon(Theme.get_icon(theme_icon))
        self.btn_theme_toggle.setIconSize(QSize(icon_size))
        self.btn_theme_toggle.setToolTip(
            f"Switch to {'Light' if Theme.current_mode == Theme.MODE_DARK else 'Dark'} Mode"
        )

        self.line.setStyleSheet(f"color: {Theme.BORDER};")

        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {Theme.BG_APP};
                color: {Theme.TEXT_MAIN};
            }}
            {Theme.TOOLTIP_STYLE}
            {Theme.BUTTON_STYLE}
        """
        )
