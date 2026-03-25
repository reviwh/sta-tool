import os
import json
import re
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QMessageBox,
    QLabel,
    QDialog,
    QSplitter,
    QStatusBar,
    QStackedWidget,
)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QShortcut, QKeySequence, QFontDatabase, QFont, QIcon

from core.project_manager import ProjectManager

# Import New Components
from ui.theme import Theme
from ui.components.tool_bar import ToolBarComponent
from ui.components.file_tree import FileTreeComponent
from ui.components.string_list import StringListComponent
from ui.components.editor_panel import EditorPanelComponent
from ui.components.toast import ToastNotification
from ui.components.replace_dialog import ReplaceDialog
from ui.components.shortcuts_dialog import ShortcutsDialog
from ui.components.welcome_panel import WelcomePanel


class StaTranslator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STA Translator Tool")
        self.setWindowIcon(QIcon("assets/icon.svg"))
        self.resize(1024, 640)

        self.manager = ProjectManager()

        self.current_file_idx = -1
        self.current_string_idx = -1

        self.toast = None  # Lazy init in show_toast
        self.font_family = "Noto Sans JP"

        font_path = "assets/fonts/NotoSansJP-Regular.ttf"
        font_mono_path = "assets/fonts/JetBrainsMono.ttf"
        font_id = QFontDatabase.addApplicationFont(font_path)
        font_mono_id = QFontDatabase.addApplicationFont(font_mono_path)

        if font_id != -1:
            self.font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            print(f"Font loaded: {self.font_family}")
        else:
            print("Failed to load Noto Sans JP!")

        if font_mono_id != -1:
            font_mono_family = QFontDatabase.applicationFontFamilies(font_mono_id)[0]
            print(f"Font loaded: {font_mono_family}")
        else:
            print("Failed to load JetBrains Mono!")

        # System Theme Detection
        initial_mode = Theme.detect_system_theme()
        Theme.set_mode(initial_mode)

        self.setFont(QFont(self.font_family, 10))
        self.init_ui()
        self.update_ui_state()
        self.apply_theme()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tool_bar = ToolBarComponent()
        layout.addWidget(self.tool_bar)

        # Main Content Area with Splitters
        self.content_stack = QWidget()
        self.content_layout = QVBoxLayout(self.content_stack)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        # Vertical Splitter (Top vs Bottom)
        self.v_splitter = QSplitter(Qt.Orientation.Vertical)

        # Top Section: Horizontal Splitter (FileTree vs StringList)
        self.h_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.file_section = FileTreeComponent()
        self.file_section.file_selected.connect(self.on_file_selected)
        self.h_splitter.addWidget(self.file_section)

        self.string_section = StringListComponent()
        self.string_section.string_selected.connect(self.on_string_selected)
        self.h_splitter.addWidget(self.string_section)

        self.h_splitter.setStretchFactor(0, 1)
        self.h_splitter.setStretchFactor(1, 2)

        self.v_splitter.addWidget(self.h_splitter)

        # Bottom Section: Editor Panel
        self.editor_section = EditorPanelComponent()
        self.editor_section.set_fields_enabled(False)
        self.editor_section.translation_changed.connect(self.on_save_translation)
        self.editor_section.request_next.connect(self.go_to_next_string)
        self.editor_section.request_prev.connect(self.go_to_prev_string)
        self.editor_section.font_changed.connect(self.on_font_settings_changed)
        self.v_splitter.addWidget(self.editor_section)

        self.v_splitter.setStretchFactor(0, 2)
        self.v_splitter.setStretchFactor(1, 1)

        self.content_layout.addWidget(self.v_splitter)

        # Welcome Panel (Empty State)
        self.welcome_panel = WelcomePanel()
        self.welcome_panel.extract_requested.connect(self.handle_extract)
        self.welcome_panel.load_requested.connect(self.handle_load)

        # Stacked Widget to switch between Welcome and Content
        self.stack = QStackedWidget()
        self.stack.addWidget(self.welcome_panel)
        self.stack.addWidget(self.content_stack)

        layout.addWidget(self.stack)

        self.string_section.request_focus_editor.connect(self.focus_translation_editor)

        # Status Bar
        self.status_bar = QStatusBar()
        self.status_bar.setFont(Theme.FONT)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Plugin Info in Status Bar
        self.status_plugin_label = QLabel("")
        self.status_plugin_label.setFont(Theme.FONT)
        self.status_plugin_label.setStyleSheet(
            f"color: {Theme.TEXT_MAIN}; background: transparent; margin-right: 8px; border: none"
        )
        self.status_bar.addPermanentWidget(self.status_plugin_label)

        # Footer in Status Bar
        self.footer = QLabel("© 2024 Revi Wardana Putra.")
        self.footer.setFont(Theme.FONT)
        self.footer.setStyleSheet(
            f"color: {Theme.TEXT_MAIN}; background: transparent; border: none"
        )
        self.status_bar.addPermanentWidget(self.footer)

        # Connect Toolbar Actions
        self.tool_bar.btn_save.clicked.connect(self.handle_save)
        self.tool_bar.btn_save_as.clicked.connect(self.handle_save_as)
        self.tool_bar.btn_apply_plugin.clicked.connect(self.handle_apply_plugin)
        self.tool_bar.btn_shortcuts.clicked.connect(self.handle_show_shortcuts)
        self.tool_bar.btn_close.clicked.connect(self.handle_close)
        self.tool_bar.btn_repack.clicked.connect(self.handle_repack)
        self.tool_bar.remove_plugin_requested.connect(self.handle_remove_plugin)
        self.tool_bar.theme_changed.connect(self.handle_theme_changed)
        self.string_section.import_txt_requested.connect(self.handle_import_txt)
        self.string_section.replace_all_requested.connect(self.handle_replace_all)

        # Connect Manager Signals
        self.manager.project_loaded.connect(self.on_project_loaded)
        self.manager.project_closed.connect(self.on_project_closed)
        self.manager.data_changed.connect(lambda: self.refresh_ui_full(True))
        self.manager.dirty_changed.connect(self.update_ui_state)
        self.manager.error_occurred.connect(
            lambda msg: QMessageBox.critical(self, "Error", msg)
        )
        self.manager.status_message.connect(self.status_bar.showMessage)

        # Setup Global Shortcuts
        self.setup_global_shortcuts()

        # Initial Theme Apply
        self.apply_theme()

    def setup_global_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self.handle_extract)
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.handle_load)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.handle_save)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self).activated.connect(
            self.handle_save_as
        )
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(self.handle_close)
        QShortcut(QKeySequence("F5"), self).activated.connect(self.handle_repack)
        QShortcut(QKeySequence("Ctrl+P"), self).activated.connect(
            self.handle_apply_plugin
        )
        QShortcut(QKeySequence("Ctrl+H"), self).activated.connect(
            self.handle_show_shortcuts
        )

    def on_project_loaded(self, path):
        self.apply_editor_font_from_manager()
        self.update_ui_state()
        self.refresh_ui_full()
        self.status_bar.showMessage(f"Loaded: {os.path.basename(path)}")
        self.show_toast(f"Loaded: {os.path.basename(path)}")

    def on_project_closed(self):
        self.update_ui_state()
        self.status_bar.showMessage("Ready")

    def flush_save(self):
        if self.editor_section.save_timer.isActive():
            self.editor_section.save_timer.stop()
            self.on_save_translation(self.editor_section.trans_edit.toPlainText())

    def on_file_selected(self, idx):
        self.flush_save()
        self.current_file_idx = idx

        keyword = self.file_section.get_search_text()
        show_warnings = self.file_section.is_warning_filter_active()

        filtered_items = self.manager.get_filtered_entries(idx, keyword, show_warnings)

        self.string_section.set_strings(filtered_items)

        # Highlight current file in the tree
        current_entries = self.manager.data[idx]["entries"]
        self.file_section.update_current_file_text(idx, current_entries)

        # Update Path Label di String List
        file_path = self.manager.data[idx]["file_path"]
        self.string_section.set_file_path(file_path)

        # Update Info Bar in editor
        file_path = self.manager.data[idx]["file_path"]
        self.editor_section.set_fields_enabled(False)
        self.editor_section.set_data(
            info_text=f"{os.path.basename(file_path)}, Line 0",
            original_text="",
            translated_text="",
        )

    def on_string_selected(self, real_idx):
        """Handler when a text line is selected in List View."""
        self.flush_save()
        self.current_string_idx = real_idx

        file_path = self.manager.data[self.current_file_idx]["file_path"]
        entry = self.manager.data[self.current_file_idx]["entries"][real_idx]

        # Update editor via editor_section component
        self.editor_section.set_fields_enabled(True)
        self.editor_section.set_data(
            info_text=f"{os.path.basename(file_path)}, Line {real_idx + 1}",
            original_text=entry["original"],
            translated_text=entry.get("translated", ""),
        )

    def focus_translation_editor(self):
        self.editor_section.trans_edit.setFocus()
        cursor = self.editor_section.trans_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.editor_section.trans_edit.setTextCursor(cursor)

    def on_save_translation(self, text):
        if self.current_file_idx == -1 or self.current_string_idx == -1:
            return

        txt = text.replace("\n", "\\n")

        current_row = self.string_section.list_widget.currentRow()
        self.string_section.update_item_color(current_row, txt)
        self.string_section.update_item_text(current_row, txt)

        current_entries = self.manager.data[self.current_file_idx]["entries"]
        self.file_section.update_current_file_text(
            self.current_file_idx, current_entries
        )

        self.manager.update_translation(
            self.current_file_idx, self.current_string_idx, txt
        )

        self.file_section.update_global_progress(
            self.manager.full_data.get("content", [])
        )

    def on_filter_changed(self):
        """Handler when search keyword changes (after debounce)."""
        if not self.manager.is_active():
            return

        keyword = self.file_section.get_search_text()
        show_warnings = self.file_section.is_warning_filter_active()
        visible_files = self.manager.get_filtered_files(keyword, show_warnings)

        # Update Tree View
        self.file_section.set_data(visible_files, self.manager.data)

        # If a file is currently open, also update its string list
        if self.current_file_idx != -1:
            self.on_file_selected(self.current_file_idx)
        else:
            self.editor_section.set_fields_enabled(False)

    def check_unsaved_changes(self):
        """Show confirmation dialog if there are unsaved changes. Returns True if safe to proceed, False to abort."""
        if self.manager.is_active() and self.manager.is_dirty:
            self.flush_save()
            res = QMessageBox.warning(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
            )
            if res == QMessageBox.StandardButton.Save:
                self.handle_save()
                return True
            elif res == QMessageBox.StandardButton.Cancel:
                return False
            elif res == QMessageBox.StandardButton.Discard:
                return True
        return True

    def handle_extract(self):
        if not self.check_unsaved_changes():
            return
        # Only allow when welcome panel is shown or via menu (handled by visibility)
        if self.stack.currentWidget() != self.welcome_panel:
            return
        src = QFileDialog.getExistingDirectory(self, "Select .sta Folder")
        if not src:
            return
        dest, _ = QFileDialog.getSaveFileName(self, "Save Project JSON", "", "*.json")
        if dest:
            self.manager.extract(src, dest)
            self.setWindowTitle(f"STA Translator Tool - {Path(*Path(dest).parts[-2:])}")

    def handle_load(self):
        if not self.check_unsaved_changes():
            return
        # Only allow when welcome panel is shown or via menu
        if self.stack.currentWidget() != self.welcome_panel:
            return
        path, _ = QFileDialog.getOpenFileName(self, "Open Project JSON", "", "*.json")
        if path:
            self.manager.load(path)
            self.setWindowTitle(f"STA Translator Tool - {Path(*Path(path).parts[-2:])}")

    def handle_save(self):
        if not self.manager.is_active():
            return
        self.flush_save()
        self.manager.save()
        self.update_ui_state()
        self.show_toast("Project saved successfully")

    def handle_save_as(self):
        if not self.manager.is_active():
            return
        self.flush_save()
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Project As", self.manager.path, "*.json"
        )
        if path:
            if not path.lower().endswith(".json"):
                path += ".json"
            self.manager.path = path
            self.manager.save(path)
            self.setWindowTitle(f"STA Translator Tool - {Path(*Path(path).parts[-2:])}")
            self.update_ui_state()
            self.show_toast("Project saved successfully")

    def load_string_to_editor(self):
        """Function to load data from JSON to Editor."""
        if self.current_file_idx == -1 or self.current_string_idx == -1:
            return

        file_data = self.manager.data[self.current_file_idx]
        entry = file_data["entries"][self.current_string_idx]

        settings = self.manager.full_data.get("settings", {})
        font_settings = settings.get("font", {})
        f_name = font_settings.get("name", "Noto Sans JP")
        f_size = font_settings.get("size", 12)

        self.editor_section.set_data(
            entry["original"], entry.get("translated", ""), f_name, f_size
        )

    def refresh_ui_full(self, preserve_selection=True):
        if not self.manager.is_active():
            return

        # Save current state
        curr_file = self.current_file_idx
        curr_string = self.current_string_idx

        keyword = self.file_section.get_search_text()
        show_warnings = self.file_section.is_warning_filter_active()
        visible_files = self.manager.get_filtered_files(keyword, show_warnings)

        self.file_section.set_data(
            visible_files, self.manager.data, active_idx=curr_file
        )
        self.update_ui_state()
        self.apply_editor_font_from_manager()
        self.file_section.update_global_progress(self.manager.data)
        for i, file_data in enumerate(self.manager.data):
            self.file_section.update_current_file_text(i, file_data["entries"])

        # Restore selection
        if preserve_selection and curr_file != -1:
            # Note: set_data handles tree selection logic via active_idx
            if curr_string != -1:
                # Trigger reload of string list and re-select
                self.on_file_selected(curr_file)
                self.string_section.list_widget.setCurrentRow(curr_string)

    def handle_close(self):
        if not self.check_unsaved_changes():
            return

        # Force save if timer is running
        self.flush_save()

        self.manager.close()
        self.current_file_idx = -1
        self.current_string_idx = -1

        # Reset UI in each component
        self.file_section.model.clear()
        self.string_section.list_widget.clear()
        self.string_section.set_file_path("Select a file...")
        self.status_plugin_label.setText("")
        self.editor_section.set_data("No file selected", "", "")
        self.update_ui_state()
        self.status_bar.showMessage("Ready")

    def handle_repack(self):
        if not self.manager.is_active():
            return

        self.flush_save()

        out = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if out:
            self.manager.repack(out)

    def handle_apply_plugin(self):
        if not self.manager.is_active():
            return

        path, _ = QFileDialog.getOpenFileName(
            self, "Select Plugin JSON", "", "JSON Files (*.json)"
        )
        if not path:
            return

        # Update Settings and Save
        settings = self.manager.full_data.get("settings", {})
        if "plugin" not in settings:
            settings["plugin"] = {}
        settings["plugin"]["path"] = path

        self.manager.apply_plugin()
        self.manager.save()
        self.refresh_ui_full(preserve_selection=True)
        self.show_toast("Plugin applied!")

    def handle_remove_plugin(self):
        if not self.manager.is_active():
            return

        res = QMessageBox.question(
            self,
            "Remove Plugin",
            "Are you sure you want to remove the plugin and reverse its changes?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if res == QMessageBox.StandardButton.Yes:
            self.manager.reverse_plugin()
            settings = self.manager.full_data.get("settings", {})
            if "plugin" in settings:
                settings["plugin"]["path"] = ""

            self.manager.is_dirty = True
            self.manager.save()
            self.refresh_ui_full()
            self.show_toast("Plugin removed")

    def handle_import_txt(self):
        if self.current_file_idx == -1:
            QMessageBox.warning(self, "Warning", "Please select a file first!")
            return

        path, _ = QFileDialog.getOpenFileName(
            self, "Import Translation from TXT", "", "Text Files (*.txt)"
        )
        if path:
            success, msg = self.manager.import_txt(self.current_file_idx, path)
            if success:
                self.on_file_selected(self.current_file_idx)
                self.show_toast("Import successful")

    def handle_replace_all(self):
        if self.current_file_idx == -1:
            QMessageBox.warning(self, "Warning", "Please select a file first!")
            return

        dialog = ReplaceDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            count = self.manager.replace_all(
                self.current_file_idx,
                data["find"],
                data["replace"],
                data["case_sensitive"],
                data["source"],
            )
            if count > 0:
                self.on_file_selected(self.current_file_idx)
                self.show_toast(f"Replaced {count} occurrences")
            else:
                self.show_toast("No matches found", duration=Theme.TOAST_NORMAL)

    def show_toast(self, message, duration=None):
        if duration is None:
            duration = Theme.TOAST_NORMAL
        if not self.toast:
            self.toast = ToastNotification(self)
        self.toast.show_message(message, duration)

    def handle_show_shortcuts(self):
        dialog = ShortcutsDialog(self)
        dialog.exec()

    def go_to_next_string(self):
        curr = self.string_section.list_widget.currentRow()
        if curr < self.string_section.list_widget.count() - 1:
            self.on_save_translation(self.editor_section.trans_edit.toPlainText())
            self.string_section.list_widget.setCurrentRow(curr + 1)

    def go_to_prev_string(self):
        curr = self.string_section.list_widget.currentRow()
        if curr > 0:
            self.on_save_translation(self.editor_section.trans_edit.toPlainText())
            self.string_section.list_widget.setCurrentRow(curr - 1)

    def on_font_settings_changed(self, name, size):
        if self.manager.is_active():
            settings = self.manager.full_data.get("settings", {})
            if "font" not in settings:
                settings["font"] = {}
            settings["font"]["name"] = name
            settings["font"]["size"] = size
            self.manager.is_dirty = True
            self.update_ui_state()

    def apply_editor_font_from_manager(self):
        font_name = "Noto Sans JP"
        font_size = 12

        if self.manager.is_active():
            settings = self.manager.full_data.get("settings", {})
            font_data = settings.get("font", {})
            font_name = font_data.get("name", font_name)
            font_size = font_data.get("size", font_size)

        self.editor_section.apply_fonts(font_name, font_size)

    def update_ui_state(self):
        is_active = self.manager.is_active()
        p_name = os.path.basename(self.manager.path) if is_active else ""
        p_path = self.manager.path if is_active else ""

        has_plugin = False
        plugin_name = ""
        if is_active:
            settings = self.manager.full_data.get("settings", {})
            plugin_path = settings.get("plugin", {}).get("path")
            if plugin_path:
                has_plugin = True
                plugin_name = os.path.basename(plugin_path)

        self.tool_bar.update_state(
            is_active,
            p_name,
            p_path,
            has_plugin=has_plugin,
            is_dirty=self.manager.is_dirty,
        )
        if is_active:
            title_suffix = " *" if self.manager.is_dirty else ""
            self.setWindowTitle(f"STA Translator Tool - {Path(*Path(p_name).parts[-2:])}{title_suffix}")
        else:
            self.setWindowTitle("STA Translator Tool")

        self.status_plugin_label.setText(
            f"Plugin: {plugin_name}" if plugin_name else ""
        )
        self.status_plugin_label.setVisible(is_active)

        # Toggle visibility
        active = self.manager.is_active()
        self.stack.setCurrentWidget(
            self.content_stack if active else self.welcome_panel
        )

        # Inactive state handles
        if not active:
            pass  # No specific inactive state handles needed here after refactoring to QStackedWidget

    def apply_global_styles(self):
        app_font = QFont(self.font_family)
        app_font.setPixelSize(Theme.FONT_SIZE)
        self.setFont(app_font)

        self.string_section.apply_font(self.font_family)

        # Editor follows Project Manager settings
        self.apply_editor_font_from_manager()

    def handle_theme_changed(self):
        new_mode = (
            Theme.MODE_LIGHT
            if Theme.current_mode == Theme.MODE_DARK
            else Theme.MODE_DARK
        )
        Theme.set_mode(new_mode)
        self.apply_theme()
        self.show_toast(f"Switched to {new_mode.capitalize()} Mode")

    def apply_theme(self):
        # Apply to central window
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {Theme.BG_APP};
                color: {Theme.TEXT_MAIN};
            }}
            {Theme.TOOLTIP_STYLE}
            """
        )

        # Apply icons & styles to components
        self.tool_bar.apply_theme(
            has_plugin=self.manager.is_active()
            and bool(
                self.manager.full_data.get("settings", {}).get("plugin", {}).get("path")
            )
        )
        self.file_section.apply_theme()
        self.string_section.apply_theme()
        self.editor_section.apply_theme()
        self.welcome_panel.apply_theme()

        # Update Status Bar
        self.status_bar.setStyleSheet(
            f"""
            QStatusBar {{ 
                background: {Theme.BG_CONTAINER}; 
                border-top: 1px solid {Theme.BORDER}; 
                color: {Theme.TEXT_MAIN};
            }}
            """
        )
        self.status_plugin_label.setStyleSheet(
            f"color: {Theme.TEXT_MAIN}; background: transparent; margin-right: 8px; border: none;"
        )
        self.footer.setStyleSheet(
            f"color: {Theme.TEXT_MAIN}; background: transparent; border: none"
        )

        # Apply Scrollbar Styles to any dynamic scroll areas
        for scroll in self.findChildren(QSplitter):
            scroll.setStyleSheet(
                f"""
            QSplitter::handle {{ background: {Theme.BORDER}; }}
            QSplitter::handle:horizontal{{ width: 1px; }}
            QSplitter::handle:vertical{{ height: 1px; }}
            """
            )

        # Refresh Global Font
        self.apply_global_styles()

    def closeEvent(self, event):
        if not self.check_unsaved_changes():
            event.ignore()
            return

        self.flush_save()
        self.manager.close()
        event.accept()
