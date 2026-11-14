from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QFontComboBox,
    QSpinBox,
    QPushButton,
    QApplication,
)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer, QEvent
from PyQt6.QtGui import (
    QShortcut,
    QKeySequence,
    QColor,
    QTextCharFormat,
    QTextFormat,
)

from ui.theme import Theme
from ui.color_tags import cursor_to_text, document_to_text, text_to_html
from ui.components.text_color_picker import TextColorButton, TextColorPopup


class EditorPanelComponent(QWidget):
    translation_changed = pyqtSignal(str)
    request_next = pyqtSignal()
    request_prev = pyqtSignal()
    font_changed = pyqtSignal(str, int)
    copy_occurred = pyqtSignal(str)
    undo_requested = pyqtSignal()
    redo_requested = pyqtSignal()
    undo_state_changed = pyqtSignal(bool, bool)
    request_focus_list = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("editor_panel")
        self._loaded_translation = ""
        self._translation_dirty = False
        self._text_color = QColor("#E60014")
        self._color_active = False
        self._project_colors = []
        self.color_btn = None
        self._color_popup = None
        self.init_ui()
        self.setMinimumHeight(200)

        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self._emit_change)

        self.setup_shortcuts()

    def setup_shortcuts(self):
        self.sc_next = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.sc_next.activated.connect(self.request_next.emit)

        self.sc_prev = QShortcut(QKeySequence("Ctrl+Shift+Return"), self)
        self.sc_prev.activated.connect(self.request_prev.emit)

        self.sc_font_dec = QShortcut(QKeySequence("Ctrl+Shift+,"), self)
        self.sc_font_dec.activated.connect(self.decrease_font_size)

        self.sc_font_inc = QShortcut(QKeySequence("Ctrl+Shift+."), self)
        self.sc_font_inc.activated.connect(self.increase_font_size)

        self.sc_color_toggle = QShortcut(QKeySequence("Ctrl+K"), self)
        self.sc_color_toggle.activated.connect(self.toggle_color_tag)

    def toggle_color_tag(self):
        if not self.trans_edit.isEnabled():
            return
        if self._color_active:
            self._clear_color()
        else:
            self._apply_color(self._text_color)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(8, 8, 8, 0)
        header_layout.setSpacing(8)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.info_label = QLabel("No file selected")
        self.info_label.setObjectName("info_label")
        header_layout.addWidget(self.info_label, 1)

        font_controls_label = QLabel("Font:")
        font_controls_label.setFont(Theme.FONT)
        font_controls = QHBoxLayout()
        font_controls.addWidget(font_controls_label)
        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self._on_font_ui_changed)
        font_controls.addWidget(self.font_combo)

        font_controls_size_label = QLabel("Size:")
        font_controls_size_label.setFont(Theme.FONT)
        font_controls.addWidget(font_controls_size_label)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setFont(Theme.FONT)
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.valueChanged.connect(self._on_font_ui_changed)
        font_controls.addWidget(self.font_size_spin)

        header_layout.addLayout(font_controls)
        layout.addLayout(header_layout)

        editor_layout = QHBoxLayout()
        editor_layout.setContentsMargins(8, 0, 8, 8)
        editor_layout.setSpacing(8)

        self.orig_edit = QTextEdit()
        self.orig_edit.setReadOnly(True)
        self.orig_edit.setTabChangesFocus(True)
        self.orig_container = self._make_editor_container(self.orig_edit, "original")

        self.trans_edit = QTextEdit()
        self.trans_edit.setTabChangesFocus(True)
        self.trans_container = self._make_editor_container(
            self.trans_edit, "translated", with_color=True
        )

        editor_layout.addWidget(self.orig_container)
        editor_layout.addWidget(self.trans_container)
        layout.addLayout(editor_layout, 2)

        self.trans_edit.textChanged.connect(self._on_text_changed)
        self.trans_edit.currentCharFormatChanged.connect(
            self._on_current_char_format_changed
        )
        self.trans_edit.installEventFilter(self)
        self.orig_edit.installEventFilter(self)

        self.apply_theme()

    def _make_editor_container(self, edit, label, with_color=False):
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)

        if with_color:
            self.color_btn = TextColorButton()
            self.color_btn.clicked.connect(self._open_color_popup)
            btn_row.addWidget(self.color_btn)

        btn_row.addStretch()

        copy_btn = QPushButton()
        copy_btn.setObjectName("copy_btn")
        copy_btn.setIcon(Theme.get_icon("content_copy"))
        copy_btn.setFixedSize(24, 24)
        copy_btn.setToolTip(f"Copy all {label} text")
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.clicked.connect(
            lambda: self._copy_text(edit, use_selection=False)
        )
        btn_row.addWidget(copy_btn)

        container_layout.addLayout(btn_row)
        container_layout.addWidget(edit)

        edit._copy_button = copy_btn
        return container

    def set_project_colors(self, colors):
        self._project_colors = [
            color for color in (colors or []) if isinstance(color, str)
        ]
        if self._color_popup is not None:
            self._color_popup.set_colors(self._project_colors)

    def _open_color_popup(self):
        if self._color_popup is None:
            self._color_popup = TextColorPopup(self)
            self._color_popup.color_selected.connect(self._apply_color)
            self._color_popup.color_cleared.connect(self._clear_color)
            self._color_popup.closed.connect(self._on_color_popup_closed)

        self._color_popup.set_colors(self._project_colors)
        self._color_popup.set_color(self._text_color)
        self._color_popup.move(
            self.color_btn.mapToGlobal(self.color_btn.rect().bottomLeft())
        )
        self.color_btn.set_open(True)
        self._color_popup.show()
        self._color_popup.raise_()

    def _on_color_popup_closed(self):
        if self.color_btn is not None:
            self.color_btn.set_open(False)

    def _apply_color(self, color):
        if not isinstance(color, QColor) or not color.isValid():
            return
        self._text_color = QColor(color)
        self._color_active = True

        char_format = QTextCharFormat()
        char_format.setForeground(self._text_color)
        self.trans_edit.mergeCurrentCharFormat(char_format)
        self.trans_edit.setFocus()
        self._update_color_buttons()

    def _clear_color(self):
        char_format = self.trans_edit.currentCharFormat()
        char_format.clearProperty(QTextFormat.Property.ForegroundBrush)
        self.trans_edit.setCurrentCharFormat(char_format)
        self._color_active = False
        self.trans_edit.setFocus()
        self._update_color_buttons()

    def _on_current_char_format_changed(self, char_format):
        self._sync_color_state(char_format)

    def _sync_color_state(self, char_format=None):
        if char_format is None:
            char_format = self.trans_edit.currentCharFormat()

        has_color = char_format.hasProperty(
            QTextFormat.Property.ForegroundBrush
        ) and char_format.foreground().style() != Qt.BrushStyle.NoBrush
        if has_color:
            color = char_format.foreground().color()
            if color.isValid():
                self._text_color = color

        self._color_active = has_color
        self._update_color_buttons()

    def _update_color_buttons(self):
        if self.color_btn is not None:
            self.color_btn.set_color(self._text_color)
            self.color_btn.set_active(self._color_active)

    def _copy_text(self, edit, use_selection=True):
        clipboard = QApplication.clipboard()
        cursor = edit.textCursor()
        if use_selection and cursor.hasSelection():
            clipboard.setText(cursor_to_text(cursor))
        else:
            clipboard.setText(document_to_text(edit.document()))
        self.copy_occurred.emit("Text copied to clipboard")

    def eventFilter(self, obj, event):
        """Route undo/redo keys to the application history.

        The text edit handles Ctrl+Z on its own, so the key press is consumed
        here and forwarded to the controller which decides between the local
        (in text field) undo and the application wide history.
        """
        if (
            obj in (self.trans_edit, self.orig_edit)
            and event.type() == QEvent.Type.ContextMenu
        ):
            menu = obj.createStandardContextMenu(event.pos())
            for action in menu.actions():
                label = action.text().replace("&", "").split("\t")[0].strip()
                if label == "Copy":
                    try:
                        action.triggered.disconnect()
                    except TypeError:
                        pass
                    action.triggered.connect(
                        lambda _=False, edit=obj: self._copy_text(edit)
                    )
                    break
            menu.exec(obj.mapToGlobal(event.pos()))
            menu.deleteLater()
            return True

        if (
            obj in (self.trans_edit, self.orig_edit)
            and event.type() == QEvent.Type.KeyPress
        ):
            key = event.key()
            modifiers = event.modifiers()
            ctrl = modifiers & Qt.KeyboardModifier.ControlModifier
            shift = modifiers & Qt.KeyboardModifier.ShiftModifier

            if ctrl and key == Qt.Key.Key_Z and not shift:
                self.undo_requested.emit()
                return True

            if ctrl and key == Qt.Key.Key_Y:
                self.redo_requested.emit()
                return True

            if (
                ctrl
                and key in (Qt.Key.Key_C, Qt.Key.Key_Insert)
                and obj.textCursor().hasSelection()
            ):
                self._copy_text(obj)
                return True

            if ctrl and shift and key == Qt.Key.Key_Z and not self.has_local_redo():
                self.redo_requested.emit()
                return True

            if key == Qt.Key.Key_Escape:
                self.request_focus_list.emit()
                return True

        return super().eventFilter(obj, event)

    def focus_editor(self):
        """Give the translation field focus with the cursor at the end."""
        self.trans_edit.setFocus()
        cursor = self.trans_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.trans_edit.setTextCursor(cursor)

    def has_local_focus(self):
        """True when the translation text field owns the keyboard focus."""
        return self.trans_edit.hasFocus()

    def has_local_undo(self):
        """True when the text field still holds undoable steps."""
        return self.trans_edit.document().isUndoAvailable()

    def has_local_redo(self):
        """True when the text field still holds redoable steps."""
        return self.trans_edit.document().isRedoAvailable()

    def undo_local(self):
        """Undo the last step typed inside the text field."""
        self.trans_edit.undo()

    def redo_local(self):
        """Redo the last step undone inside the text field."""
        self.trans_edit.redo()

    def set_data(self, info_text, original_text, translated_text):
        self.trans_edit.blockSignals(True)
        self.orig_edit.blockSignals(True)

        self.info_label.setText(info_text)
        self.orig_edit.setHtml(text_to_html(original_text.replace("\\n", "\n")))
        self.trans_edit.setHtml(
            text_to_html((translated_text or "").replace("\\n", "\n"))
        )

        self.trans_edit.blockSignals(False)
        self.orig_edit.blockSignals(False)

        self._loaded_translation = translated_text or ""
        self._translation_dirty = False
        self._sync_color_state()

        is_valid = bool(
            info_text
            and (info_text != "No file selected" and not info_text.endswith("Line 0"))
        )
        self.set_fields_enabled(is_valid)
        self.undo_state_changed.emit(self.has_local_undo(), self.has_local_redo())

    def set_fields_enabled(self, enabled):
        self.trans_edit.setEnabled(enabled)
        self.font_combo.setEnabled(enabled)
        self.font_size_spin.setEnabled(enabled)
        if self.color_btn is not None:
            self.color_btn.setEnabled(enabled)
        if not enabled and self._color_popup is not None:
            self._color_popup.close()

        if not enabled:
            self.trans_edit.setPlaceholderText("Select a line to start editing...")
        else:
            self.trans_edit.setPlaceholderText("")

    def get_translation_text(self):
        """The project string with color tags restored from the rich text."""
        if not self._translation_dirty:
            return self._loaded_translation
        return document_to_text(self.trans_edit.document())

    def _on_text_changed(self):
        self._translation_dirty = True
        self.save_timer.start(500)
        self.undo_state_changed.emit(self.has_local_undo(), self.has_local_redo())

    def _emit_change(self):
        text = self.get_translation_text()
        self.translation_changed.emit(text)

    def apply_fonts(self, family, size):
        self.font_combo.blockSignals(True)
        self.font_size_spin.blockSignals(True)

        self.font_combo.setCurrentText(family)
        self.font_size_spin.setValue(size)

        font = self.orig_edit.font()
        font.setFamily(family)
        font.setPointSize(size)
        self.orig_edit.setFont(font)
        self.trans_edit.setFont(font)

        self.font_combo.blockSignals(False)
        self.font_size_spin.blockSignals(False)

    def _on_font_ui_changed(self):
        family = self.font_combo.currentFont().family()
        if self.font_combo.currentText():
            family = self.font_combo.currentText()
        size = self.font_size_spin.value()

        font = self.orig_edit.font()
        font.setFamily(family)
        font.setPointSize(size)
        self.orig_edit.setFont(font)
        self.trans_edit.setFont(font)

        self.font_changed.emit(family, size)

    def increase_font_size(self):
        self.font_size_spin.setValue(self.font_size_spin.value() + 1)

    def decrease_font_size(self):
        self.font_size_spin.setValue(self.font_size_spin.value() - 1)

    def apply_theme(self):
        for edit in (self.orig_edit, self.trans_edit):
            btn = getattr(edit, "_copy_button", None)
            if btn is not None:
                btn.setIcon(Theme.get_icon("content_copy"))
        self._update_color_buttons()
        if self._color_popup is not None:
            self._color_popup.refresh_theme()
