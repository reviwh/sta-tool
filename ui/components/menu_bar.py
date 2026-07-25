from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, QSize, QObject
from PyQt6.QtGui import QKeySequence, QAction


class MenuBarComponent(QObject):
    def __init__(self, view):
        super().__init__(view)
        self._view = view

        menu_bar = self._view.menuBar()

        file_menu = menu_bar.addMenu("&File")

        self.action_new = QAction("&New Project", view)
        self.action_new.setShortcut(QKeySequence("Ctrl+N"))
        self.action_new.triggered.connect(self._view.extract_requested)
        file_menu.addAction(self.action_new)

        self.action_open = QAction("&Open Project...", view)
        self.action_open.setShortcut(QKeySequence("Ctrl+O"))
        self.action_open.triggered.connect(self._view.load_requested)
        file_menu.addAction(self.action_open)

        file_menu.addSeparator()

        self.action_save = QAction("&Save", view)
        self.action_save.setShortcut(QKeySequence("Ctrl+S"))
        self.action_save.triggered.connect(self._view.save_requested)
        file_menu.addAction(self.action_save)

        self.action_save_as = QAction("Save &As...", view)
        self.action_save_as.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.action_save_as.triggered.connect(self._view.save_as_requested)
        file_menu.addAction(self.action_save_as)

        file_menu.addSeparator()

        self.action_close = QAction("&Close Project", view)
        self.action_close.setShortcut(QKeySequence("Ctrl+W"))
        self.action_close.triggered.connect(self._view.close_project_requested)
        file_menu.addAction(self.action_close)

        self.action_repack = QAction("&Repack", view)
        self.action_repack.setShortcut(QKeySequence("F5"))
        self.action_repack.triggered.connect(self._view.repack_requested)
        file_menu.addAction(self.action_repack)

        file_menu.addSeparator()

        self.action_import_csv = QAction("&Import CSV...", view)
        self.action_import_csv.setShortcut(QKeySequence("Ctrl+I"))
        self.action_import_csv.triggered.connect(
            self._view.import_csv_requested
        )
        file_menu.addAction(self.action_import_csv)

        self.action_export_csv = QAction("&Export CSV...", view)
        self.action_export_csv.setShortcut(QKeySequence("Ctrl+E"))
        self.action_export_csv.triggered.connect(
            self._view.export_csv_requested
        )
        file_menu.addAction(self.action_export_csv)

        self.action_replace_all = QAction("&Replace All...", view)
        self.action_replace_all.setShortcut(QKeySequence("Ctrl+Shift+F"))
        self.action_replace_all.triggered.connect(
            self._view.replace_all_requested
        )
        file_menu.addAction(self.action_replace_all)

        plugin_menu = menu_bar.addMenu("&Plugin")

        self.action_apply_plugin = QAction("&Apply Plugin...", view)
        self.action_apply_plugin.setShortcut(QKeySequence("Ctrl+P"))
        self.action_apply_plugin.triggered.connect(
            self._view.apply_plugin_requested
        )
        plugin_menu.addAction(self.action_apply_plugin)

        self.action_remove_plugin = QAction("&Remove Plugin", view)
        self.action_remove_plugin.setShortcut(QKeySequence("Ctrl+Shift+R"))
        self.action_remove_plugin.triggered.connect(
            self._view.remove_plugin_requested
        )
        plugin_menu.addAction(self.action_remove_plugin)

        help_menu = menu_bar.addMenu("&Help")

        self.action_shortcuts = QAction("&Shortcuts", view)
        self.action_shortcuts.setShortcut(QKeySequence("Ctrl+H"))
        self.action_shortcuts.triggered.connect(
            self._view.shortcuts_requested
        )
        help_menu.addAction(self.action_shortcuts)

        self.menu_theme_btn = QPushButton()
        self.menu_theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.menu_theme_btn.clicked.connect(self._view.theme_changed)
        menu_bar.setCornerWidget(self.menu_theme_btn, Qt.Corner.TopRightCorner)

        self.update_file_menu_state(False)

    def update_file_menu_state(self, is_active, has_plugin=False):
        self.action_new.setEnabled(not is_active)
        self.action_open.setEnabled(not is_active)
        self.action_save.setEnabled(is_active)
        self.action_save_as.setEnabled(is_active)
        self.action_close.setEnabled(is_active)
        self.action_repack.setEnabled(is_active)
        self.action_import_csv.setEnabled(is_active)
        self.action_export_csv.setEnabled(is_active)
        self.action_replace_all.setEnabled(is_active)
        self.action_apply_plugin.setEnabled(is_active)
        self.action_remove_plugin.setEnabled(is_active and has_plugin)
