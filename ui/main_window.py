from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QSplitter,
    QStatusBar,
    QLabel,
    QProgressBar,
    QStackedWidget,
)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QFontDatabase, QFont, QIcon

from core.utils import resource_path
from ui.theme import Theme
from ui.components.file_tree import FileTreeComponent
from ui.components.string_list import StringListComponent
from ui.components.editor_panel import EditorPanelComponent
from ui.components.welcome_panel import WelcomePanel
from ui.components.menu_bar import MenuBarComponent


class StaTranslator(QMainWindow):
    extract_requested = pyqtSignal()
    load_requested = pyqtSignal()
    save_requested = pyqtSignal()
    save_as_requested = pyqtSignal()
    close_project_requested = pyqtSignal()
    repack_requested = pyqtSignal()
    apply_plugin_requested = pyqtSignal()
    remove_plugin_requested = pyqtSignal()
    theme_changed = pyqtSignal()
    export_csv_requested = pyqtSignal()
    import_csv_requested = pyqtSignal()
    shortcuts_requested = pyqtSignal()
    replace_all_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("STA Translator Tool")
        self.setWindowIcon(QIcon(resource_path("assets/icon.svg")))
        self.resize(1024, 640)

        self.close_handler = None
        self.font_family = "Noto Sans JP"

        self._load_fonts()
        self._detect_theme()
        self.setFont(QFont(self.font_family, 10))
        self.init_ui()
        self.menu_bar = MenuBarComponent(self)
        self.apply_theme()

    def _load_fonts(self):
        font_path = resource_path("assets/fonts/NotoSansJP-Regular.ttf")
        font_mono_path = resource_path("assets/fonts/JetBrainsMono.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        QFontDatabase.addApplicationFont(font_mono_path)
        if font_id != -1:
            self.font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

    def _detect_theme(self):
        initial_mode = Theme.detect_system_theme()
        Theme.set_mode(initial_mode)

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.content_stack = QWidget()
        self.content_layout = QVBoxLayout(self.content_stack)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        self.v_splitter = QSplitter(Qt.Orientation.Vertical)
        self.h_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.file_section = FileTreeComponent()
        self.h_splitter.addWidget(self.file_section)

        self.string_section = StringListComponent()
        self.h_splitter.addWidget(self.string_section)

        self.h_splitter.setStretchFactor(0, 1)
        self.h_splitter.setStretchFactor(1, 2)
        self.v_splitter.addWidget(self.h_splitter)

        self.editor_section = EditorPanelComponent()
        self.v_splitter.addWidget(self.editor_section)

        self.v_splitter.setStretchFactor(0, 1)
        self.v_splitter.setStretchFactor(1, 1)
        self.content_layout.addWidget(self.v_splitter)

        self.welcome_panel = WelcomePanel()
        self.stack = QStackedWidget()
        self.stack.addWidget(self.welcome_panel)
        self.stack.addWidget(self.content_stack)
        layout.addWidget(self.stack)

        self.global_progress = QProgressBar()
        self.global_progress.setFont(Theme.FONT)
        self.global_progress.setFixedHeight(16)
        self.global_progress.setVisible(False)
        layout.addWidget(self.global_progress)

        self.status_bar = QStatusBar()
        self.status_bar.setFont(Theme.FONT)
        self.status_bar.setSizeGripEnabled(False)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self.status_plugin_label = QLabel("")
        self.status_plugin_label.setObjectName("status_plugin_label")
        self.status_plugin_label.setFont(Theme.FONT)
        self.status_bar.addPermanentWidget(self.status_plugin_label)

        self.footer = QLabel("© 2024 Revi Wardana Putra.")
        self.footer.setObjectName("footer")
        self.footer.setFont(Theme.FONT)
        self.status_bar.addPermanentWidget(self.footer)

    def update_file_menu_state(self, is_active, has_plugin=False):
        self.menu_bar.update_file_menu_state(is_active, has_plugin=has_plugin)

    def update_global_progress(self, all_content):
        total_entries = 0
        done_entries = 0
        for file_data in all_content:
            entries = file_data.get("entries", [])
            total_entries += len(entries)
            for e in entries:
                trans_text = e.get("translated", "")
                if len(trans_text.strip()) > 0:
                    done_entries += 1
        if total_entries > 0:
            percentage = int((done_entries / total_entries) * 100)
            self.global_progress.setValue(percentage)
        else:
            self.global_progress.setValue(0)

    def apply_global_styles(self):
        editor_family = self.editor_section.font_combo.currentText()
        editor_size = self.editor_section.font_size_spin.value()

        app_font = QFont(self.font_family)
        app_font.setPixelSize(Theme.FONT_SIZE)
        self.setFont(app_font)
        self.string_section.apply_font(self.font_family)

        self.editor_section.apply_fonts(editor_family, editor_size)

    def apply_theme(self):
        Theme.apply_qss()

        self.file_section.apply_theme()
        self.string_section.apply_theme()
        self.editor_section.apply_theme()
        self.welcome_panel.apply_theme()

        theme_icon = (
            "light_mode" if Theme.current_mode == Theme.MODE_DARK else "dark_mode"
        )
        btn = self.menu_bar.menu_theme_btn
        btn.setIcon(Theme.get_icon(theme_icon))
        btn.setIconSize(QSize(16, 16))
        btn.setToolTip(
            f"Switch to {'Light' if Theme.current_mode == Theme.MODE_DARK else 'Dark'} Mode"
        )
        btn.setFont(Theme.FONT)

        self.apply_global_styles()

    def closeEvent(self, event):
        if self.close_handler:
            self.close_handler(event)
        else:
            event.accept()
