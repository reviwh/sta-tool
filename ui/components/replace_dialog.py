from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QTabWidget,
    QWidget,
)
from PyQt6.QtCore import Qt, QSize, QEvent
from PyQt6.QtGui import QFont, QKeySequence, QShortcut
from ui.theme import Theme
from ui.components.clear_button import ClearButtonMixin


class ReplaceDialog(ClearButtonMixin, QDialog):
    SCOPE_FILE = "file"
    SCOPE_PROJECT = "project"

    def __init__(self, parent=None, state=None, scope=None, has_file=True):
        super().__init__(parent)
        self.setObjectName("replace_dialog")
        self.setWindowTitle("Replace All")
        self.setFixedWidth(350)
        # Modeless: the main window stays fully usable while the dialog is open
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)

        self._tab_scopes = []
        self._scope_shortcuts = []
        self._tab_bar = None
        self._break_edits = []
        self._normalizing = False
        self.form_widget = None
        self.init_ui(has_file)
        self._restore_state(state, scope)

    def init_ui(self, has_file=True):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.scope_tabs = QTabWidget()
        self.scope_tabs.setFont(Theme.FONT)
        self.scope_tabs.currentChanged.connect(self._on_scope_changed)
        if has_file:
            self._add_scope_tab(
                self.SCOPE_FILE,
                "Current file",
                "Replace inside the file that is currently selected in the tree.",
            )
        self._add_scope_tab(
            self.SCOPE_PROJECT,
            "Whole project",
            "Replace inside every file of the project.\n"
            "\n"
            "The whole replacement can be undone in a single step.",
        )
        layout.addWidget(self.scope_tabs)
        self._install_tab_cursor()

        self.form_widget = self._build_form()
        self._move_form_to(self.scope_tabs.currentIndex())

        layout.addStretch()

        container = QWidget()
        container.setObjectName("replace_footer")
        btn_layout = QHBoxLayout(container)
        btn_layout.setContentsMargins(8, 8, 8, 8)
        btn_layout.setSpacing(8)

        icon_size = QSize(16, 16)
        self.btn_replace = QPushButton("Replace All")
        self.btn_replace.setFont(Theme.FONT)
        self.btn_replace.setIcon(Theme.get_primary_icon("find_replace"))
        self.btn_replace.setIconSize(icon_size)
        self.btn_replace.setToolTip(
            "Find and replace in all entries of the selected scope"
        )
        self.btn_replace.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_replace.setDefault(True)
        self.btn_replace.clicked.connect(self.accept)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setFont(Theme.FONT)
        self.btn_cancel.setIcon(Theme.get_icon("close"))
        self.btn_cancel.setIconSize(icon_size)
        self.btn_cancel.setToolTip("Discard changes and close dialog")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setAutoDefault(False)
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_replace)
        layout.addWidget(container)

        self._install_scope_shortcuts()

    def _install_scope_shortcuts(self):
        """Allow scope switching with the same keys used by the main window."""
        for keys, scope in (
            (QKeySequence("Ctrl+H"), self.SCOPE_FILE),
            (QKeySequence("Ctrl+Shift+H"), self.SCOPE_PROJECT),
        ):
            shortcut = QShortcut(keys, self)
            shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
            shortcut.activated.connect(lambda s=scope: self._select_scope(s))
            self._scope_shortcuts.append(shortcut)

    def _install_tab_cursor(self):
        """Show a pointer cursor while the mouse hovers a scope tab."""
        self._tab_bar = self.scope_tabs.tabBar()
        self._tab_bar.setMouseTracking(True)
        self._tab_bar.installEventFilter(self)

    def _setup_line_breaks(self, edit):
        """Allow line breaks inside a single line field.

        The stored entries keep their line breaks as the two characters
        ``\\n``, so a real line break typed with Shift+Enter or pasted into
        the field is kept as that escape sequence.
        """
        self._break_edits.append(edit)
        edit.installEventFilter(self)
        edit.textChanged.connect(lambda _text, e=edit: self._normalize_breaks(e))
        edit.setToolTip(
            "Press Shift+Enter to insert a line break\n"
            "Pasted line breaks are kept as \\n as well"
        )

    def _insert_line_break(self, edit):
        """Insert the line break escape at the current cursor position."""
        pos = edit.cursorPosition()
        edit.insert("\\n")
        edit.setCursorPosition(pos + 2)

    def _normalize_breaks(self, edit):
        """Replace real line breaks in the field with the ``\\n`` escape."""
        if self._normalizing:
            return
        text = edit.text()
        if "\n" not in text and "\r" not in text:
            return
        escaped = self._escape_line_breaks(text)
        pos = edit.cursorPosition()
        extra = self._count_breaks(text[:pos])
        self._normalizing = True
        try:
            edit.setText(escaped)
            edit.setCursorPosition(min(pos + extra, len(escaped)))
        finally:
            self._normalizing = False

    @staticmethod
    def _escape_line_breaks(text):
        """Convert real line breaks into the ``\\n`` escape used by the data."""
        return text.replace("\r\n", "\\n").replace("\r", "\\n").replace("\n", "\\n")

    @staticmethod
    def _count_breaks(text):
        """Count the real line breaks inside the given text."""
        return text.count("\n") + text.count("\r") - text.count("\r\n")

    def eventFilter(self, obj, event):
        if obj is self._tab_bar:
            if event.type() == QEvent.Type.MouseMove:
                over_tab = self._tab_bar.tabAt(event.pos()) >= 0
                self._tab_bar.setCursor(
                    Qt.CursorShape.PointingHandCursor
                    if over_tab
                    else Qt.CursorShape.ArrowCursor
                )
            elif event.type() == QEvent.Type.Leave:
                self._tab_bar.setCursor(Qt.CursorShape.ArrowCursor)
        elif obj in self._break_edits:
            if event.type() == QEvent.Type.KeyPress:
                key = event.key()
                mods = event.modifiers()
                if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and (
                    mods & Qt.KeyboardModifier.ShiftModifier
                    or mods & Qt.KeyboardModifier.ControlModifier
                ):
                    self._insert_line_break(obj)
                    return True
        return super().eventFilter(obj, event)

    def _build_form(self):
        """Build the shared form shown inside the active scope tab."""
        form = QWidget()
        form.setObjectName("replace_form")
        form_layout = QVBoxLayout(form)
        form_layout.setContentsMargins(8, 8, 8, 8)
        form_layout.setSpacing(4)

        self.find_label = QLabel("Find:")
        self.find_label.setFont(Theme.FONT)
        form_layout.addWidget(self.find_label)
        self.find_edit = QLineEdit()
        self.find_edit.setFont(Theme.FONT)
        self._add_clear_button(self.find_edit)
        self._setup_line_breaks(self.find_edit)
        form_layout.addWidget(self.find_edit)
        form_layout.addSpacing(4)

        self.replace_label = QLabel("Replace with:")
        self.replace_label.setFont(Theme.FONT)
        form_layout.addWidget(self.replace_label)
        self.replace_edit = QLineEdit()
        self.replace_edit.setFont(Theme.FONT)
        self._add_clear_button(self.replace_edit)
        self._setup_line_breaks(self.replace_edit)
        form_layout.addWidget(self.replace_edit)
        form_layout.addSpacing(4)

        source_layout = QHBoxLayout()
        source_layout.setContentsMargins(0, 0, 0, 0)
        source_layout.setSpacing(8)

        self.match_label = QLabel("Match against:")
        self.match_label.setFont(Theme.FONT)
        self.match_label.setToolTip(
            "Searches the find text in:\n"
            "Original - the source text\n"
            "Translated - the current translation"
        )
        source_layout.addWidget(self.match_label)
        source_layout.addStretch()

        self.radio_original = QRadioButton("Original")
        self.radio_original.setFont(Theme.FONT)
        self.radio_original.setCursor(Qt.CursorShape.PointingHandCursor)
        self.radio_original.setToolTip(
            "Search the original text.\n"
            "\n"
            "No translation: the original\n"
            "text is replaced and becomes\n"
            "the translation.\n"
            "\n"
            "With translation: only the\n"
            "matching part is replaced."
        )
        self.radio_translated = QRadioButton("Translated")
        self.radio_translated.setChecked(True)
        self.radio_translated.setFont(Theme.FONT)
        self.radio_translated.setCursor(Qt.CursorShape.PointingHandCursor)
        self.radio_translated.setToolTip(
            "Search the current translation\n"
            "and replace it in place.\n"
            "\n"
            "Entries without a translation\n"
            "are skipped."
        )

        self.source_group = QButtonGroup(self)
        self.source_group.addButton(self.radio_original)
        self.source_group.addButton(self.radio_translated)

        source_layout.addWidget(self.radio_original)
        source_layout.addWidget(self.radio_translated)
        form_layout.addLayout(source_layout)
        form_layout.addSpacing(4)

        self.case_check = QCheckBox("Case-sensitive")
        self.case_check.setFont(Theme.FONT)
        self.case_check.setCursor(Qt.CursorShape.PointingHandCursor)
        form_layout.addWidget(self.case_check)

        return form

    def _add_scope_tab(self, scope, title, description):
        """Append a scope tab; the description is shown as a tab tooltip."""
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(4)

        self.scope_tabs.addTab(page, title)
        self.scope_tabs.setTabToolTip(self.scope_tabs.count() - 1, description)
        self._tab_scopes.append(scope)

    def _on_scope_changed(self, index):
        """Move the shared form into the newly selected scope tab."""
        if self.form_widget is None:
            return
        self._move_form_to(index)

    def _move_form_to(self, index):
        """Reparent the shared form into the page of the given tab."""
        page = self.scope_tabs.widget(index)
        if page is None:
            return

        current_parent = self.form_widget.parentWidget()
        if current_parent is page:
            return

        if current_parent is not None and current_parent.layout() is not None:
            current_parent.layout().removeWidget(self.form_widget)

        page.layout().addWidget(self.form_widget)

    def _restore_state(self, state, scope=None):
        if state:
            self.find_edit.setText(self._escape_line_breaks(state.get("find", "")))
            self.replace_edit.setText(
                self._escape_line_breaks(state.get("replace", ""))
            )
            self.case_check.setChecked(state.get("case_sensitive", False))
            if state.get("source") == "original":
                self.radio_original.setChecked(True)
            else:
                self.radio_translated.setChecked(True)
            self._select_scope(state.get("scope", self.SCOPE_PROJECT))

        if scope:
            self._select_scope(scope)

    def _select_scope(self, scope):
        """Activate the tab matching the given scope, if it is available."""
        if scope in self._tab_scopes:
            self.scope_tabs.setCurrentIndex(self._tab_scopes.index(scope))

    def set_scope(self, scope):
        """Activate the tab matching the given scope, if it is available."""
        self._select_scope(scope)

    def get_data(self):
        return {
            "find": self._escape_line_breaks(self.find_edit.text()),
            "replace": self._escape_line_breaks(self.replace_edit.text()),
            "case_sensitive": self.case_check.isChecked(),
            "source": "original" if self.radio_original.isChecked() else "translated",
            "scope": self.get_scope(),
        }

    def get_scope(self):
        index = self.scope_tabs.currentIndex()
        if 0 <= index < len(self._tab_scopes):
            return self._tab_scopes[index]
        return self.SCOPE_PROJECT
