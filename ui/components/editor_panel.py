# ui/components/editor_panel.py
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QFontComboBox,
    QSpinBox,
)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QShortcut, QKeySequence

from ui.theme import Theme


class EditorPanelComponent(QWidget):
    # Event when user stops typing (debounce save)
    translation_changed = pyqtSignal(str)
    # Signal untuk navigasi baris
    request_next = pyqtSignal()
    request_prev = pyqtSignal()
    # Signal saat font berubah di UI (untuk di-save ke config)
    font_changed = pyqtSignal(str, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setMinimumHeight(200)

        # Debounce Timer for Saving (500ms)
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self._emit_change)

        # Setup Shortcuts
        self.setup_shortcuts()

    def setup_shortcuts(self):
        # Ctrl+Enter: Next Line
        self.sc_next = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.sc_next.activated.connect(self.request_next.emit)

        # Ctrl+Shift+Enter: Previous Line
        self.sc_prev = QShortcut(QKeySequence("Ctrl+Shift+Return"), self)
        self.sc_prev.activated.connect(self.request_prev.emit)

        # Ctrl+Shift+< (Decrease Font)
        self.sc_font_dec = QShortcut(
            QKeySequence("Ctrl+Shift+,"), self
        )  # Dalam banyak layout, < adalah Shift+,
        self.sc_font_dec.activated.connect(self.decrease_font_size)

        # Ctrl+Shift+> (Increase Font)
        self.sc_font_inc = QShortcut(
            QKeySequence("Ctrl+Shift+."), self
        )  # Dalam banyak layout, > adalah Shift+.
        self.sc_font_inc.activated.connect(self.increase_font_size)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(8, 8, 8, 0)
        header_layout.setSpacing(8)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.info_label = QLabel("No file selected")
        header_layout.addWidget(self.info_label, 1)

        label_style = "background: transparent; border: none;"

        font_controls_label = QLabel("Font:")
        font_controls_label.setFont(Theme.FONT)
        font_controls_label.setStyleSheet(label_style)
        font_controls = QHBoxLayout()
        font_controls.addWidget(font_controls_label)
        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self._on_font_ui_changed)
        font_controls.addWidget(self.font_combo)

        font_controls_size_label = QLabel("Size:")
        font_controls_size_label.setFont(Theme.FONT)
        font_controls_size_label.setStyleSheet(label_style)
        font_controls.addWidget(font_controls_size_label)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setFont(Theme.FONT)
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.valueChanged.connect(self._on_font_ui_changed)
        font_controls.addWidget(self.font_size_spin)

        header_layout.addLayout(font_controls)
        layout.addLayout(header_layout)

        # Editors Layout
        editor_layout = QHBoxLayout()
        editor_layout.setContentsMargins(8, 0, 8, 8)
        editor_layout.setSpacing(8)

        self.orig_edit = QTextEdit()
        self.orig_edit.setReadOnly(True)

        self.trans_edit = QTextEdit()

        editor_layout.addWidget(self.orig_edit)
        editor_layout.addWidget(self.trans_edit)
        layout.addLayout(editor_layout, 2)

        self.trans_edit.textChanged.connect(self._on_text_changed)

        self.apply_theme()

    def set_data(self, info_text, original_text, translated_text):
        self.trans_edit.blockSignals(True)
        self.orig_edit.blockSignals(True)

        self.info_label.setText(info_text)
        self.orig_edit.setPlainText(original_text)
        self.trans_edit.setPlainText(translated_text or "")

        self.trans_edit.blockSignals(False)
        self.orig_edit.blockSignals(False)

        is_valid = bool(
            info_text
            and (info_text != "No file selected" and not info_text.endswith("Line 0"))
        )
        self.set_fields_enabled(is_valid)

    def set_fields_enabled(self, enabled):
        self.trans_edit.setEnabled(enabled)
        self.font_combo.setEnabled(enabled)
        self.font_size_spin.setEnabled(enabled)

        if not enabled:
            self.trans_edit.setPlaceholderText("Select a string to start editing...")
        else:
            self.trans_edit.setPlaceholderText("")

    def _on_text_changed(self):
        self.save_timer.start(500)

    def _emit_change(self):
        text = self.trans_edit.toPlainText()
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
        # Update UI dulu
        family = self.font_combo.currentFont().family()
        # Jika combo box menggunakan text aslinya lebih akurat
        if self.font_combo.currentText():
            family = self.font_combo.currentText()

        size = self.font_size_spin.value()

        font = self.orig_edit.font()
        font.setFamily(family)
        font.setPointSize(size)
        self.orig_edit.setFont(font)
        self.trans_edit.setFont(font)

        # Notify parent to save to JSON
        self.font_changed.emit(family, size)

    def increase_font_size(self):
        self.font_size_spin.setValue(self.font_size_spin.value() + 1)

    def decrease_font_size(self):
        self.font_size_spin.setValue(self.font_size_spin.value() - 1)

    def apply_theme(self):
        self.setStyleSheet(
            f"""
                background-color: {Theme.BG_APP}; 
                color: {Theme.TEXT_MAIN}; 
                border-top: 1px solid {Theme.BORDER};
        """
        )
        self.info_label.setStyleSheet(
            f"""
            color: {Theme.TEXT_MAIN}; 
            font-weight: 500; 
            background: transparent;
            border: none;
            """
        )

        edit_style = f"""
            QTextEdit {{
                background-color: {Theme.BG_PANEL};
                color: {Theme.TEXT_MAIN};
                border: 1px solid {Theme.BORDER};
                border-radius: 4px;
            }}
            QTextEdit:disabled {{
                background-color: {Theme.BG_APP};
                color: {Theme.TEXT_SECONDARY};
            }}
        """
        self.orig_edit.setStyleSheet(edit_style)
        self.trans_edit.setStyleSheet(edit_style)

        # Scrollbars
        self.orig_edit.verticalScrollBar().setStyleSheet(Theme.SCROLLBAR_STYLE)
        self.trans_edit.verticalScrollBar().setStyleSheet(Theme.SCROLLBAR_STYLE)

        # Style font controls
        self.font_combo.setStyleSheet(Theme.COMBOBOX_STYLE)
        self.font_size_spin.setStyleSheet(Theme.SPINBOX_STYLE)
