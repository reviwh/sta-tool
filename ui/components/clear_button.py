from PyQt6.QtWidgets import QToolButton
from PyQt6.QtCore import Qt, QSize, QEvent
from ui.theme import Theme


class ClearButtonMixin:
    """Adds a themed clear (x) button inside a QLineEdit.

    The host widget must inherit QWidget; eventFilter is chained via super().
    """

    def _add_clear_button(self, edit):
        if not hasattr(self, "_clear_buttons"):
            self._clear_buttons = []

        btn = QToolButton(edit)
        btn.setIcon(Theme.get_icon("close"))
        btn.setIconSize(QSize(14, 14))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setToolTip("Clear text")
        btn.setStyleSheet("QToolButton { background: transparent; border: none; }")
        btn.hide()
        btn.clicked.connect(edit.clear)
        edit.textChanged.connect(lambda: self._position_clear_button(edit, btn))
        edit.installEventFilter(self)
        edit.setStyleSheet("QLineEdit { padding-right: 24px; }")
        self._clear_buttons.append((edit, btn))
        return btn

    def _position_clear_button(self, edit, btn):
        visible = bool(edit.text())
        btn.setVisible(visible)
        if visible:
            btn.move(edit.width() - btn.width() - 6, (edit.height() - btn.height()) // 2)

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.Type.Resize, QEvent.Type.Show):
            for edit, btn in getattr(self, "_clear_buttons", []):
                if obj is edit:
                    self._position_clear_button(edit, btn)
        return super().eventFilter(obj, event)
