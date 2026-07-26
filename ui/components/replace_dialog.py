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
    QWidget,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from ui.theme import Theme


class ReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("replace_dialog")
        self.setWindowTitle("Replace All")
        self.setFixedWidth(350)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        top_layout = QVBoxLayout()
        top_layout.setContentsMargins(8, 8, 8, 8)
        top_layout.setSpacing(4)

        self.find_label = QLabel("Find:")
        self.find_label.setFont(Theme.FONT)
        top_layout.addWidget(self.find_label)
        self.find_edit = QLineEdit()
        self.find_edit.setFont(Theme.FONT)
        top_layout.addWidget(self.find_edit)
        top_layout.addSpacing(4)

        self.replace_label = QLabel("Replace with:")
        self.replace_label.setFont(Theme.FONT)
        top_layout.addWidget(self.replace_label)
        self.replace_edit = QLineEdit()
        self.replace_edit.setFont(Theme.FONT)
        top_layout.addWidget(self.replace_edit)
        top_layout.addSpacing(4)

        source_layout = QHBoxLayout()
        source_layout.setContentsMargins(0, 0, 0, 0)
        source_layout.setSpacing(8)

        match_label = QLabel("Match against:")
        match_label.setFont(Theme.FONT)
        source_layout.addWidget(match_label)
        source_layout.addStretch()

        self.radio_original = QRadioButton("Original")
        self.radio_original.setFont(Theme.FONT)
        self.radio_original.setCursor(Qt.CursorShape.PointingHandCursor)
        self.radio_translated = QRadioButton("Translated")
        self.radio_translated.setChecked(True)
        self.radio_translated.setFont(Theme.FONT)
        self.radio_translated.setCursor(Qt.CursorShape.PointingHandCursor)

        self.source_group = QButtonGroup(self)
        self.source_group.addButton(self.radio_original)
        self.source_group.addButton(self.radio_translated)

        source_layout.addWidget(self.radio_original)
        source_layout.addWidget(self.radio_translated)
        top_layout.addLayout(source_layout)
        top_layout.addSpacing(4)

        self.case_check = QCheckBox("Case-sensitive")
        self.case_check.setFont(Theme.FONT)
        self.case_check.setCursor(Qt.CursorShape.PointingHandCursor)
        top_layout.addWidget(self.case_check)
        top_layout.addSpacing(16)

        layout.addLayout(top_layout)
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
        self.btn_replace.setToolTip("Find and replace in all entries")
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

    def get_data(self):
        return {
            "find": self.find_edit.text(),
            "replace": self.replace_edit.text(),
            "case_sensitive": self.case_check.isChecked(),
            "source": "original" if self.radio_original.isChecked() else "translated",
        }


