from PyQt6.QtWidgets import QWidget, QFrame, QLabel, QVBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import (
    Qt,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    QPoint,
)
from ui.theme import Theme


class ToastNotification(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.container = QFrame(self)
        self.container.setObjectName("toast_container")

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(16, 10, 16, 10)
        self.label = QLabel("")
        self.label.setFont(Theme.FONT)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.label)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.container)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_anim.setDuration(400)
        self.opacity_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_toast)

    def show_message(self, message, duration=2000):
        try:
            self.opacity_anim.finished.disconnect(self.close)
        except TypeError:
            pass

        self.label.setText(message)
        self.adjustSize()

        if self.parent():
            parent_rect = self.parent().rect()
            x = (parent_rect.width() - self.width()) // 2
            y = parent_rect.height() - self.height() - 50
            self.move(self.parent().mapToGlobal(QPoint(x, y)))

        self.show()
        self.opacity_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.start()

        self.timer.start(duration)

    def hide_toast(self):
        self.opacity_anim.setEasingCurve(QEasingCurve.Type.InQuad)
        self.opacity_anim.setStartValue(1.0)
        self.opacity_anim.setEndValue(0.0)
        self.opacity_anim.finished.connect(self.close)
        self.opacity_anim.start()
