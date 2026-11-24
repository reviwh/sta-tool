from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QKeySequence, QShortcut, QIntValidator

from ui.theme import Theme


class GoToLineDialog(QDialog):
    line_selected = pyqtSignal(int)

    def __init__(self, max_line, parent=None):
        super().__init__(parent)
        self.max_line = max_line
        self.setObjectName("goto_line_dialog")
        self.setWindowTitle("Go to Line")
        self.setModal(True)
        self.setFixedWidth(300)

        self._toggle_shortcut = QShortcut(QKeySequence("Esc"), self)
        self._toggle_shortcut.activated.connect(self.reject)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.form_widget = QWidget()
        self.form_widget.setObjectName("goto_line_form")
        form_layout = QVBoxLayout(self.form_widget)
        form_layout.setContentsMargins(8, 8, 8, 8)
        form_layout.setSpacing(4)

        self.label = QLabel(f"Enter line number (1-{self.max_line}):")
        self.label.setFont(Theme.FONT)
        form_layout.addWidget(self.label)

        self.line_input = QLineEdit()
        self.line_input.setFont(Theme.FONT)
        self.line_input.setPlaceholderText("Line number")
        self.line_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.line_input.setValidator(QIntValidator(1, self.max_line, self))
        self.line_input.returnPressed.connect(self._on_accept)
        form_layout.addWidget(self.line_input)

        self.error_label = QLabel("")
        self.error_label.setFont(Theme.FONT)
        self.error_label.setStyleSheet(f"color: {Theme.ERROR};")
        self.error_label.setVisible(False)
        form_layout.addWidget(self.error_label)

        layout.addWidget(self.form_widget)
        layout.addStretch()

        container = QWidget()
        container.setObjectName("goto_line_footer")
        btn_layout = QHBoxLayout(container)
        btn_layout.setContentsMargins(8, 8, 8, 8)
        btn_layout.setSpacing(8)

        icon_size = QSize(16, 16)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setFont(Theme.FONT)
        self.btn_cancel.setIcon(Theme.get_icon("close"))
        self.btn_cancel.setIconSize(icon_size)
        self.btn_cancel.setToolTip("Discard and close dialog")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setAutoDefault(False)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)

        self.btn_go = QPushButton("Go")
        self.btn_go.setFont(Theme.FONT)
        self.btn_go.setIcon(Theme.get_primary_icon("arrow_forward"))
        self.btn_go.setIconSize(icon_size)
        self.btn_go.setToolTip("Navigate to the specified line")
        self.btn_go.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_go.setDefault(True)
        self.btn_go.clicked.connect(self._on_accept)
        btn_layout.addWidget(self.btn_go)

        layout.addWidget(container)

    def _on_accept(self):
        text = self.line_input.text().strip()
        if not text:
            return
        try:
            line_num = int(text)
            if 1 <= line_num <= self.max_line:
                self.line_selected.emit(line_num)
                self.accept()
            else:
                self.line_input.setStyleSheet(
                    f"border: 1px solid {Theme.ERROR};"
                )
                self.error_label.setText(
                    f"Invalid line number. Please enter 1-{self.max_line}."
                )
                self.error_label.setVisible(True)
        except ValueError:
            self.line_input.setStyleSheet(
                f"border: 1px solid {Theme.ERROR};"
            )
            self.error_label.setText(
                f"Invalid input. Please enter 1-{self.max_line}."
            )
            self.error_label.setVisible(True)

    def showEvent(self, event):
        super().showEvent(event)
        self.line_input.setFocus(Qt.FocusReason.OtherFocusReason)
        if self.line_input.text():
            self.line_input.selectAll()
        self.line_input.setStyleSheet("")
        self.error_label.setVisible(False)
        self.error_label.setText("")
