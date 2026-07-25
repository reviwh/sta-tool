import os
from pathlib import Path
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QDialog
from PyQt6.QtCore import QObject

from core.project_manager import ProjectManager
from ui.components.replace_dialog import ReplaceDialog
from ui.components.shortcuts_dialog import ShortcutsDialog
from ui.components.toast import ToastNotification


class AppController(QObject):
    def __init__(self, model: ProjectManager, view):
        super().__init__()
        self.model = model
        self.view = view
        self.current_file_idx = -1
        self.current_string_idx = -1
        self._toast = None
        self._connect_signals()

    def _connect_signals(self):
        v = self.view
        m = self.model

        # Model -> View
        m.project_loaded.connect(self._on_project_loaded)
        m.project_closed.connect(self._on_project_closed)
        m.dirty_changed.connect(self._update_ui_state)
        m.error_occurred.connect(lambda msg: QMessageBox.critical(v, "Error", msg))
        m.status_message.connect(v.status_bar.showMessage)

        # View close handler
        v.close_handler = self._on_close_requested

        # View signals (shortcuts)
        v.extract_requested.connect(self._on_extract_requested)
        v.load_requested.connect(self._on_load_requested)

        # View signals (from menu bar)
        v.save_requested.connect(self._on_save_requested)
        v.save_as_requested.connect(self._on_save_as_requested)
        v.close_project_requested.connect(self._on_close_project_requested)
        v.repack_requested.connect(self._on_repack_requested)
        v.apply_plugin_requested.connect(self._on_apply_plugin_requested)
        v.remove_plugin_requested.connect(self._on_remove_plugin_requested)
        v.theme_changed.connect(self._on_theme_toggle_requested)
        v.export_csv_requested.connect(self._on_export_csv_requested)
        v.import_csv_requested.connect(self._on_import_csv_requested)
        v.shortcuts_requested.connect(self._on_shortcuts_requested)
        v.replace_all_requested.connect(self._on_replace_all_requested)

        # File tree
        v.file_section.file_selected.connect(self._on_file_selected)
        v.file_section.filter_changed.connect(self._on_filter_changed)

        # String list
        v.string_section.string_selected.connect(self._on_string_selected)
        v.string_section.request_focus_editor.connect(self._focus_translation_editor)
        v.string_section.import_txt_requested.connect(self._on_import_txt_requested)
        v.string_section.replace_all_requested.connect(self._on_replace_all_requested)

        # Editor
        v.editor_section.translation_changed.connect(self._on_save_translation)
        v.editor_section.request_next.connect(self._go_to_next_string)
        v.editor_section.request_prev.connect(self._go_to_prev_string)
        v.editor_section.font_changed.connect(self._on_font_settings_changed)
        v.editor_section.copy_occurred.connect(lambda msg: self._show_toast(msg))

        # Welcome panel
        v.welcome_panel.extract_requested.connect(self._on_extract_requested)
        v.welcome_panel.load_requested.connect(self._on_load_requested)

    def _flush_save(self):
        if self.view.editor_section.save_timer.isActive():
            self.view.editor_section.save_timer.stop()
            self._on_save_translation(
                self.view.editor_section.trans_edit.toPlainText()
            )

    def _on_project_loaded(self, path):
        self._apply_editor_font()
        self._update_ui_state()
        self._refresh_ui()
        self.view.status_bar.showMessage(f"Loaded: {os.path.basename(path)}")
        self._show_toast(f"Loaded: {os.path.basename(path)}")

    def _on_project_closed(self):
        self._update_ui_state()
        self.view.status_bar.showMessage("Ready")

    def _on_close_requested(self, event):
        if not self._check_unsaved_changes():
            event.ignore()
            return
        self._flush_save()
        self.model.close()
        self.current_file_idx = -1
        self.current_string_idx = -1
        self.view.file_section.model.clear()
        self.view.string_section.list_widget.clear()
        self.view.string_section.set_file_path("Select a file...")
        self.view.status_plugin_label.setText("")
        self.view.editor_section.set_data("No file selected", "", "")
        self.view.editor_section.set_fields_enabled(False)
        self._update_ui_state()
        self.view.status_bar.showMessage("Ready")
        event.accept()

    def _on_file_selected(self, idx):
        self._flush_save()
        self.current_file_idx = idx
        keyword = self.view.file_section.get_search_text()
        show_warnings = self.view.file_section.is_warning_filter_active()
        filtered_items = self.model.get_filtered_entries(idx, keyword, show_warnings)
        self.view.string_section.set_strings(filtered_items)
        current_entries = self.model.data[idx]["entries"]
        self.view.file_section.update_current_file_text(idx, current_entries)
        file_path = self.model.data[idx]["file_path"]
        self.view.string_section.set_file_path(file_path)
        self.view.editor_section.set_fields_enabled(False)
        self.view.editor_section.set_data(
            info_text=f"{os.path.basename(file_path)}, Line 0",
            original_text="",
            translated_text="",
        )

    def _on_string_selected(self, real_idx):
        self._flush_save()
        self.current_string_idx = real_idx
        file_path = self.model.data[self.current_file_idx]["file_path"]
        entry = self.model.data[self.current_file_idx]["entries"][real_idx]
        self.view.editor_section.set_fields_enabled(True)
        self.view.editor_section.set_data(
            info_text=f"{os.path.basename(file_path)}, Line {real_idx + 1}",
            original_text=entry["original"],
            translated_text=entry.get("translated", ""),
        )

    def _focus_translation_editor(self):
        self.view.editor_section.trans_edit.setFocus()
        cursor = self.view.editor_section.trans_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.view.editor_section.trans_edit.setTextCursor(cursor)

    def _on_save_translation(self, text):
        if self.current_file_idx == -1 or self.current_string_idx == -1:
            return
        txt = text.replace("\n", "\\n")
        current_row = self.view.string_section.list_widget.currentRow()
        self.view.string_section.update_item_color(current_row, txt)
        self.view.string_section.update_item_text(current_row, txt)
        current_entries = self.model.data[self.current_file_idx]["entries"]
        self.view.file_section.update_current_file_text(
            self.current_file_idx, current_entries
        )
        self.model.update_translation(
            self.current_file_idx, self.current_string_idx, txt
        )
        self.view.update_global_progress(self.model.data)

    def _on_filter_changed(self):
        if not self.model.is_active():
            return
        keyword = self.view.file_section.get_search_text()
        show_warnings = self.view.file_section.is_warning_filter_active()
        visible_files = self.model.get_filtered_files(keyword, show_warnings)
        self.view.file_section.set_data(visible_files, self.model.data)
        if self.current_file_idx != -1:
            self._on_file_selected(self.current_file_idx)
        else:
            self.view.editor_section.set_fields_enabled(False)

    def _check_unsaved_changes(self):
        if self.model.is_active() and self.model.is_dirty:
            self._flush_save()
            res = QMessageBox.warning(
                self.view,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
            )
            if res == QMessageBox.StandardButton.Save:
                self._on_save_requested()
                return True
            elif res == QMessageBox.StandardButton.Cancel:
                return False
            elif res == QMessageBox.StandardButton.Discard:
                return True
        return True

    def _on_extract_requested(self):
        if self.view.stack.currentWidget() != self.view.welcome_panel:
            return
        if not self._check_unsaved_changes():
            return
        src = QFileDialog.getExistingDirectory(self.view, "Select .sta Folder")
        if not src:
            return
        dest, _ = QFileDialog.getSaveFileName(
            self.view, "Save Project JSON", "", "*.json"
        )
        if dest:
            self.model.extract(src, dest)
            self.view.setWindowTitle(
                f"STA Translator Tool - {Path(*Path(dest).parts[-2:])}"
            )

    def _on_load_requested(self):
        if self.view.stack.currentWidget() != self.view.welcome_panel:
            return
        if not self._check_unsaved_changes():
            return
        path, _ = QFileDialog.getOpenFileName(
            self.view, "Open Project JSON", "", "*.json"
        )
        if path:
            self.model.load(path)
            self.view.setWindowTitle(
                f"STA Translator Tool - {Path(*Path(path).parts[-2:])}"
            )

    def _on_save_requested(self):
        if not self.model.is_active():
            return
        self._flush_save()
        self.model.save()
        self._update_ui_state()
        self._show_toast("Project saved successfully")

    def _on_save_as_requested(self):
        if not self.model.is_active():
            return
        self._flush_save()
        path, _ = QFileDialog.getSaveFileName(
            self.view, "Save Project As", self.model.path, "*.json"
        )
        if path:
            if not path.lower().endswith(".json"):
                path += ".json"
            self.model.path = path
            self.model.save(path)
            self.view.setWindowTitle(
                f"STA Translator Tool - {Path(*Path(path).parts[-2:])}"
            )
            self._update_ui_state()
            self._show_toast("Project saved successfully")

    def _on_close_project_requested(self):
        if not self.model.is_active():
            return
        if not self._check_unsaved_changes():
            return
        self._flush_save()
        self.model.close()
        self.current_file_idx = -1
        self.current_string_idx = -1
        self.view.file_section.model.clear()
        self.view.string_section.list_widget.clear()
        self.view.string_section.set_file_path("Select a file...")
        self.view.status_plugin_label.setText("")
        self.view.editor_section.set_data("No file selected", "", "")
        self._update_ui_state()
        self.view.status_bar.showMessage("Ready")

    def _on_repack_requested(self):
        if not self.model.is_active():
            return
        self._flush_save()
        out = QFileDialog.getExistingDirectory(self.view, "Select Output Folder")
        if out:
            self.model.repack(out)

    def _on_apply_plugin_requested(self):
        if not self.model.is_active():
            return
        path, _ = QFileDialog.getOpenFileName(
            self.view, "Select Plugin JSON", "", "JSON Files (*.json)"
        )
        if not path:
            return
        settings = self.model.full_data.get("settings", {})
        if "plugin" not in settings:
            settings["plugin"] = {}
        settings["plugin"]["path"] = path
        self.model.apply_plugin()
        self.model.save()
        self._refresh_ui(preserve_selection=True)
        self._show_toast("Plugin applied!")

    def _on_remove_plugin_requested(self):
        if not self.model.is_active():
            return
        res = QMessageBox.question(
            self.view,
            "Remove Plugin",
            "Are you sure you want to remove the plugin and reverse its changes?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if res == QMessageBox.StandardButton.Yes:
            self.model.reverse_plugin()
            settings = self.model.full_data.get("settings", {})
            if "plugin" in settings:
                settings["plugin"]["path"] = ""
            self.model.is_dirty = True
            self.model.save()
            self._refresh_ui()
            self._show_toast("Plugin removed")

    def _on_import_txt_requested(self):
        if self.current_file_idx == -1:
            QMessageBox.warning(self.view, "Warning", "Please select a file first!")
            return
        path, _ = QFileDialog.getOpenFileName(
            self.view, "Import Translation from TXT", "", "Text Files (*.txt)"
        )
        if path:
            success, msg = self.model.import_txt(self.current_file_idx, path)
            if success:
                self._on_file_selected(self.current_file_idx)
                self._show_toast("Import successful")

    def _on_export_csv_requested(self):
        if not self.model.is_active():
            return
        self._flush_save()
        path, _ = QFileDialog.getSaveFileName(
            self.view, "Export CSV", "", "CSV Files (*.csv)"
        )
        if path:
            if not path.lower().endswith(".csv"):
                path += ".csv"
            success, msg = self.model.export_csv(path)
            if success:
                self._show_toast("CSV export successful")

    def _on_import_csv_requested(self):
        if not self.model.is_active():
            return
        path, _ = QFileDialog.getOpenFileName(
            self.view, "Import CSV", "", "CSV Files (*.csv)"
        )
        if path:
            success, msg = self.model.import_csv(path)
            if success:
                self._refresh_ui()
                self._show_toast("CSV import successful")

    def _on_replace_all_requested(self):
        if self.current_file_idx == -1:
            QMessageBox.warning(self.view, "Warning", "Please select a file first!")
            return
        dialog = ReplaceDialog(self.view)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            count = self.model.replace_all(
                self.current_file_idx,
                data["find"],
                data["replace"],
                data["case_sensitive"],
                data["source"],
            )
            if count > 0:
                self._on_file_selected(self.current_file_idx)
                self._show_toast(f"Replaced {count} occurrences")
            else:
                self._show_toast("No matches found", duration=1000)

    def _on_shortcuts_requested(self):
        dialog = ShortcutsDialog(self.view)
        dialog.exec()

    def _go_to_next_string(self):
        v = self.view
        curr = v.string_section.list_widget.currentRow()
        if curr < v.string_section.list_widget.count() - 1:
            self._on_save_translation(v.editor_section.trans_edit.toPlainText())
            v.string_section.list_widget.setCurrentRow(curr + 1)

    def _go_to_prev_string(self):
        v = self.view
        curr = v.string_section.list_widget.currentRow()
        if curr > 0:
            self._on_save_translation(v.editor_section.trans_edit.toPlainText())
            v.string_section.list_widget.setCurrentRow(curr - 1)

    def _on_font_settings_changed(self, name, size):
        if self.model.is_active():
            settings = self.model.full_data.get("settings", {})
            if "font" not in settings:
                settings["font"] = {}
            settings["font"]["name"] = name
            settings["font"]["size"] = size
            self.model.is_dirty = True
            self._update_ui_state()

    def _apply_editor_font(self):
        font_name = "Noto Sans JP"
        font_size = 12
        if self.model.is_active():
            settings = self.model.full_data.get("settings", {})
            font_data = settings.get("font", {})
            font_name = font_data.get("name", font_name)
            font_size = font_data.get("size", font_size)
        self.view.editor_section.apply_fonts(font_name, font_size)

    def _refresh_ui(self, preserve_selection=True):
        if not self.model.is_active():
            return
        curr_file = self.current_file_idx
        curr_string = self.current_string_idx
        keyword = self.view.file_section.get_search_text()
        show_warnings = self.view.file_section.is_warning_filter_active()
        visible_files = self.model.get_filtered_files(keyword, show_warnings)
        self.view.file_section.set_data(
            visible_files, self.model.data, active_idx=curr_file
        )
        self._update_ui_state()
        self._apply_editor_font()
        self.view.update_global_progress(self.model.data)
        for i, file_data in enumerate(self.model.data):
            self.view.file_section.update_current_file_text(i, file_data["entries"])
        if preserve_selection and curr_file != -1:
            if curr_string != -1:
                self._on_file_selected(curr_file)
                self.view.string_section.list_widget.setCurrentRow(curr_string)

    def _update_ui_state(self):
        is_active = self.model.is_active()
        p_name = os.path.basename(self.model.path) if is_active else ""

        has_plugin = False
        plugin_name = ""
        if is_active:
            settings = self.model.full_data.get("settings", {})
            plugin_path = settings.get("plugin", {}).get("path")
            if plugin_path:
                has_plugin = True
                plugin_name = os.path.basename(plugin_path)

        v = self.view
        v.update_file_menu_state(is_active, has_plugin=has_plugin)

        if is_active:
            title_suffix = " *" if self.model.is_dirty else ""
            v.setWindowTitle(
                f"STA Translator Tool - {Path(*Path(p_name).parts[-2:])}{title_suffix}"
            )
        else:
            v.setWindowTitle("STA Translator Tool")

        v.status_plugin_label.setText(
            f"Plugin: {plugin_name}" if plugin_name else ""
        )
        v.status_plugin_label.setVisible(is_active)
        v.global_progress.setVisible(is_active)
        v.stack.setCurrentWidget(v.content_stack if is_active else v.welcome_panel)
        if is_active:
            v.apply_global_styles()

    def _on_theme_toggle_requested(self):
        from ui.theme import Theme
        new_mode = (
            Theme.MODE_LIGHT
            if Theme.current_mode == Theme.MODE_DARK
            else Theme.MODE_DARK
        )
        Theme.set_mode(new_mode)
        self.view.apply_theme()
        self._show_toast(f"Switched to {new_mode.capitalize()} Mode")

    def _show_toast(self, message, duration=None):
        if duration is None:
            duration = 3000
        if not self._toast:
            self._toast = ToastNotification(self.view)
        self._toast.show_message(message, duration)
