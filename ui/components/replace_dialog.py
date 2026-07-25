import os
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
    QFrame,
    QScrollArea,
    QWidget,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon
from ui.theme import Theme
from core.utils import resource_path


class ReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Replace All")
        self.setFixedWidth(350)

        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        top_layout = QVBoxLayout()
        top_layout.setContentsMargins(8, 8, 8, 8)
        top_layout.setSpacing(4)

        label_style = f"color: {Theme.TEXT_MAIN}; background-color: transparent; "

        # 1. Find
        self.find_label = QLabel("Find word:")
        self.find_label.setFont(Theme.FONT)
        self.find_label.setStyleSheet(label_style)
        top_layout.addWidget(self.find_label)
        self.find_edit = QLineEdit()
        self.find_edit.setFont(Theme.FONT)
        top_layout.addWidget(self.find_edit)
        top_layout.addSpacing(4)

        # 2. Replace
        self.replace_label = QLabel("Replace with:")
        self.replace_label.setFont(Theme.FONT)
        self.replace_label.setStyleSheet(label_style)
        top_layout.addWidget(self.replace_label)
        self.replace_edit = QLineEdit()
        self.replace_edit.setFont(Theme.FONT)
        top_layout.addWidget(self.replace_edit)
        top_layout.addSpacing(4)

        # 3. Source Selection
        source_layout = QHBoxLayout()
        source_layout.setContentsMargins(0, 0, 0, 0)
        source_layout.setSpacing(8)

        macth_label = QLabel("Match against:")
        macth_label.setFont(Theme.FONT)
        macth_label.setStyleSheet(label_style)
        source_layout.addWidget(macth_label)
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

        # 4. Options
        self.case_check = QCheckBox("Case Sensitive")
        self.case_check.setFont(Theme.FONT)
        self.case_check.setCursor(Qt.CursorShape.PointingHandCursor)
        top_layout.addWidget(self.case_check)
        top_layout.addSpacing(16)

        layout.addLayout(top_layout)
        layout.addStretch()

        # 5. Buttons
        container = QWidget()
        container.setStyleSheet(
            f"QWidget {{background-color: {Theme.BG_CONTAINER}; border-top: 1px solid {Theme.BORDER};}}"
        )
        btn_layout = QHBoxLayout(container)
        btn_layout.setContentsMargins(8, 8, 8, 8)
        btn_layout.setSpacing(8)

        icon_size = QSize(16, 16)
        self.btn_replace = QPushButton("Replace All")
        self.btn_replace.setFont(Theme.FONT)
        self.btn_replace.setIcon(
            QIcon(resource_path("assets/icons/white/find_replace.svg"))
        )
        self.btn_replace.setIconSize(icon_size)
        self.btn_replace.setToolTip("Execute replacement logic")
        self.btn_replace.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_replace.setDefault(True)
        self.btn_replace.clicked.connect(self.accept)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setFont(Theme.FONT)
        self.btn_cancel.setIcon(Theme.get_icon("close"))
        self.btn_cancel.setIconSize(icon_size)
        self.btn_cancel.setToolTip("Discard changes and close dialog")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
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

    def apply_theme(self):
        self.setStyleSheet(
            f"""
            QDialog {{ 
                background-color: {Theme.BG_APP}; 
                color: {Theme.TEXT_MAIN}; 
            }}
            QLineEdit {{ 
                background-color: {Theme.BG_PANEL}; 
                color: {Theme.TEXT_MAIN}; 
                border: 1px solid {Theme.BORDER}; 
                border-radius: 4px; 
                padding: 4px; 
            }}
            QCheckBox {{ 
                color: {Theme.TEXT_MAIN}; 
                background-color: transparent;
            }}
            QCheckBox::indicator, QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                margin-top: 1px
            }}
            QCheckBox::indicator:checked {{
                image: url({os.path.join(Theme.ICON_PATH, "check_box.svg")});
            }}
            QCheckBox::indicator:unchecked {{
                image: url({os.path.join(Theme.ICON_PATH, "check_box_blank.svg")});
            }}
            QRadioButton {{ 
                color: {Theme.TEXT_MAIN}; 
                background-color: transparent;
            }}
            QRadioButton::indicator:checked {{
                image: url({os.path.join(Theme.ICON_PATH, "radio_button_check.svg")});
            }}
            QRadioButton::indicator:unchecked {{
                image: url({os.path.join(Theme.ICON_PATH, "radio_button_uncheck.svg")});
            }}
            QFrame {{
                color: {Theme.BORDER};
            }}
            {Theme.DEFAULT_BUTTON_STYLE}
            {Theme.TOOLTIP_STYLE}
        """
        )
