from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QColorDialog,
)
from PyQt6.QtCore import pyqtSignal, Qt, QPointF, QRectF
from PyQt6.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QPainter,
    QPen,
    QPolygonF,
)

from core.color_cache import add_custom_color, get_custom_colors
from core.utils import resource_path
from ui.theme import Theme

_FONT_FAMILY = None


def _noto_font_family():
    global _FONT_FAMILY
    if _FONT_FAMILY is not None:
        return _FONT_FAMILY
    family = "Noto Sans JP"
    if family not in QFontDatabase.families():
        font_id = QFontDatabase.addApplicationFont(
            resource_path("assets/fonts/NotoSansJP-Regular.ttf")
        )
        if font_id != -1:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                family = families[0]
    _FONT_FAMILY = family
    return family


class ColorSwatch(QWidget):
    clicked = pyqtSignal()

    def __init__(self, color=None, tooltip="", parent=None):
        super().__init__(parent)
        self._color = QColor(color) if color is not None else None
        self.setFixedSize(18, 18)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        if tooltip:
            self.setToolTip(tooltip)

    def set_color(self, color):
        self._color = QColor(color) if color is not None else None
        self.update()

    def color(self):
        return QColor(self._color) if self._color is not None else None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(1, 1, self.width() - 2, self.height() - 2)

        painter.setPen(QPen(QColor(Theme.BORDER), 1))
        painter.setBrush(
            self._color if self._color is not None else QColor(Theme.BG_APP)
        )
        painter.drawRoundedRect(rect, 4, 4)

        if self._color is None:
            painter.setPen(QPen(QColor("#FF0000"), 1.4))
            painter.drawLine(
                QPointF(rect.left() + 3, rect.bottom() - 3),
                QPointF(rect.right() - 3, rect.top() + 3),
            )

        if self.underMouse():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(Theme.TEXT_MAIN), 1.4))
            painter.drawRoundedRect(rect, 4, 4)

        painter.end()

    def enterEvent(self, event):
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.update()
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.rect().contains(
            event.position().toPoint()
        ):
            self.clicked.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)


class TextColorPopup(QWidget):
    color_selected = pyqtSignal(QColor)
    color_cleared = pyqtSignal()
    closed = pyqtSignal()

    SWATCH_COLUMNS = 5

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("text_color_popup_outer")
        self.setFont(QFont(_noto_font_family()))
        self._colors = []
        self._current_color = QColor("#E60014")
        self._custom_colors = get_custom_colors()
        self._picking_color = False
        self._build_ui()
        self._rebuild_project_swatches()
        self._rebuild_custom_swatches()

    def _build_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        self._container = QWidget(self)
        self._container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._container.setObjectName("text_color_popup")
        outer_layout.addWidget(self._container)

        layout = QVBoxLayout(self._container)
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(6)

        colors_label = QLabel("Project colors")
        colors_label.setObjectName("text_color_popup_label")
        layout.addWidget(colors_label)

        self._swatch_grid = QGridLayout()
        self._swatch_grid.setContentsMargins(0, 0, 0, 0)
        self._swatch_grid.setHorizontalSpacing(6)
        self._swatch_grid.setVerticalSpacing(6)
        self._swatch_grid.setColumnStretch(self.SWATCH_COLUMNS, 1)
        layout.addLayout(self._swatch_grid)

        custom_label = QLabel("Recent colors")
        custom_label.setObjectName("text_color_popup_label")
        layout.addWidget(custom_label)

        self._custom_grid = QGridLayout()
        self._custom_grid.setContentsMargins(0, 0, 0, 0)
        self._custom_grid.setHorizontalSpacing(6)
        self._custom_grid.setVerticalSpacing(6)
        self._custom_grid.setColumnStretch(self.SWATCH_COLUMNS, 1)
        layout.addLayout(self._custom_grid)

        self.add_btn = QPushButton("+")
        self.add_btn.setObjectName("text_color_add_btn")
        self.add_btn.setFixedSize(18, 18)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setToolTip("Pick a new color")
        self.add_btn.clicked.connect(self._on_add_custom_color)

    def set_color(self, color):
        if isinstance(color, QColor) and color.isValid():
            self._current_color = QColor(color)

    def set_colors(self, colors):
        cleaned = []
        for color in colors:
            if not isinstance(color, str):
                continue
            qcolor = QColor(color)
            if qcolor.isValid():
                cleaned.append(qcolor.name())
        self._colors = cleaned
        self._custom_colors = get_custom_colors()
        self._rebuild_project_swatches()
        self._rebuild_custom_swatches()

    def _layout_widgets(self, grid, widgets):
        for index, widget in enumerate(widgets):
            row = index // self.SWATCH_COLUMNS
            column = index % self.SWATCH_COLUMNS
            grid.addWidget(
                widget,
                row,
                column,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
            )

    def _make_swatch(self, hex_color):
        swatch = ColorSwatch(hex_color, hex_color.upper())
        swatch.clicked.connect(
            lambda _=False, value=hex_color: self._on_pick(QColor(value))
        )
        return swatch

    def _make_custom_swatch(self, hex_color):
        swatch = ColorSwatch(hex_color, hex_color.upper())
        swatch.clicked.connect(
            lambda _=False, value=hex_color: self._on_pick(QColor(value))
        )
        return swatch

    def _rebuild_project_swatches(self):
        while self._swatch_grid.count():
            item = self._swatch_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        self.clear_swatch = ColorSwatch(None, "Remove color")
        self.clear_swatch.clicked.connect(self._on_clear)
        widgets = [self.clear_swatch]

        seen = set()
        for hex_color in self._colors:
            qcolor = QColor(hex_color)
            if not qcolor.isValid():
                continue
            normalized = qcolor.name()
            if normalized in seen:
                continue
            seen.add(normalized)
            widgets.append(self._make_swatch(normalized))

        self._layout_widgets(self._swatch_grid, widgets)
        self._update_size()

    def _rebuild_custom_swatches(self):
        while self._custom_grid.count():
            item = self._custom_grid.takeAt(0)
            widget = item.widget()
            if widget is not None and widget is not self.add_btn:
                widget.setParent(None)
                widget.deleteLater()

        widgets = [self.add_btn]
        for hex_color in self._custom_colors:
            qcolor = QColor(hex_color)
            if not qcolor.isValid():
                continue
            widgets.append(self._make_custom_swatch(qcolor.name()))

        self._layout_widgets(self._custom_grid, widgets)
        self._update_size()

    def _on_add_custom_color(self):
        parent = self.parent() if self.parent() is not None else self
        self._picking_color = True
        try:
            color = QColorDialog.getColor(
                self._current_color, parent, "Select Color"
            )
        finally:
            self._picking_color = False
        if not color.isValid():
            if not self.isVisible():
                self.closed.emit()
            return
        self._current_color = QColor(color)
        self._custom_colors = add_custom_color(color)
        self._rebuild_custom_swatches()
        self.show()
        self.raise_()

    def _update_size(self):
        self.layout().activate()
        self.setFixedSize(self.sizeHint())

    def refresh_theme(self):
        for widget in self.findChildren(ColorSwatch):
            widget.update()
        self.update()

    def _on_pick(self, color):
        self.color_selected.emit(QColor(color))
        self.close()

    def _on_clear(self):
        self.color_cleared.emit()
        self.close()

    def hideEvent(self, event):
        if not self._picking_color:
            self.closed.emit()
        super().hideEvent(event)


class TextColorButton(QWidget):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._color = QColor("#E60014")
        self._active = False
        self._open = False
        self._pressed = False
        self.setFixedSize(42, 24)
        self.setFont(QFont(_noto_font_family()))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._update_tooltip()

    def set_color(self, color):
        if isinstance(color, QColor) and color.isValid():
            self._color = QColor(color)
            self._update_tooltip()
            self.update()

    def set_active(self, active):
        self._active = bool(active)
        self._update_tooltip()
        self.update()

    def set_open(self, is_open):
        self._open = bool(is_open)
        self.update()

    def _update_tooltip(self):
        if self._active:
            self.setToolTip(
                f"Text color {self._color.name().upper()} (Ctrl+K to toggle)"
            )
        else:
            self.setToolTip("Text color (Ctrl+K to apply)")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        text_color = QColor(
            Theme.TEXT_MAIN if self.isEnabled() else Theme.TEXT_SECONDARY
        )
        painter.setPen(text_color)
        font = painter.font()
        font.setFamily(_noto_font_family())
        font.setBold(True)
        font.setPixelSize(12)
        painter.setFont(font)
        painter.drawText(QRectF(0, 0, 21, 19), Qt.AlignmentFlag.AlignCenter, "T")

        bar_rect = QRectF(5, 18, 12, 3)
        if self._active and self._color.isValid():
            painter.setPen(QPen(QColor(Theme.TEXT_SECONDARY), 0.8))
            painter.setBrush(self._color)
            painter.drawRoundedRect(bar_rect, 1, 1)
        else:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(text_color)
            painter.drawRoundedRect(bar_rect, 1, 1)
            painter.setPen(QPen(QColor("#FF0000"), 1))
            painter.drawLine(
                QPointF(bar_rect.right(), bar_rect.top()),
                QPointF(bar_rect.left(), bar_rect.bottom()),
            )

        pen = QPen(text_color, 1.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        if self._open:
            chevron = [QPointF(27, 14.5), QPointF(31.5, 10), QPointF(36, 14.5)]
        else:
            chevron = [QPointF(27, 10), QPointF(31.5, 14.5), QPointF(36, 10)]
        painter.drawPolyline(QPolygonF(chevron))
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            self._pressed = True
            self.update()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        was_pressed = self._pressed
        self._pressed = False
        self.update()
        if (
            was_pressed
            and event.button() == Qt.MouseButton.LeftButton
            and self.rect().contains(event.position().toPoint())
            and self.isEnabled()
        ):
            self.clicked.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (
            Qt.Key.Key_Space,
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter,
        ):
            self.clicked.emit()
            event.accept()
            return
        super().keyPressEvent(event)
