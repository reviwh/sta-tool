from PyQt6.QtGui import QColor, QIcon, QPixmap, QPainter, QFont
from PyQt6.QtCore import Qt
import os


class Theme:
    MODE_DARK = "dark"
    MODE_LIGHT = "light"
    current_mode = MODE_DARK

    @staticmethod
    def _create_color(hex_str, alpha):
        c = QColor(hex_str)
        c.setAlpha(alpha)
        return c

    # --- Theme Definitions ---
    # Common Colors (Brand)
    PRIMARY = "#3982F7"
    SUCCESS = "#00C853"
    WARNING = "#E7A917"
    WHITE = "#E5E7EB"
    BLACK = "#1F1F1F"

    # Dynamic Colors (initialized to Dark Mode)
    BG_APP = "#212121"
    BG_PANEL = "#181818"
    BG_CONTAINER = "#2e2e32"
    HOVER = "#3a3a3a"
    TEXT_MAIN = "#E5E7EB"
    TEXT_SECONDARY = "#9CA3AF"
    BORDER = "#2f2f2f"
    SECONDARY_BG_COLOR = "#3a3a3a"
    PRIMARY_HOVER = "#5094ff"
    WARNING_HOVER = "#e8b425"

    # Derived Colors
    PRIMARY_BG_COLOR = "#803982F7"
    SUCCESS_BG_COLOR = "#8000C853"
    WARNING_BG_COLOR = "#80E7A917"
    TRANSPARENT = "#00000000"

    # UI Metrics
    FONT_SIZE = 10
    FONT_SIZE_SMALL = 8
    FONT_SIZE_LARGE = 12
    MARGIN = 8
    PADDING = 4
    SPACING = 8

    ICON_PATH = "assets/icons/white/"
    TOAST_SHORT = 1000
    TOAST_NORMAL = 3000

    FONT = QFont("Noto Sans JP", 10)
    FONT_BOLD = QFont("Noto Sans JP", 10, QFont.Weight.Bold)
    FONT_ITALIC = QFont("Noto Sans JP", 10, italic=True)

    HEADER_FONT = QFont("Noto Sans JP", 24, QFont.Weight.Medium)
    HEADER_COLOR = PRIMARY

    LABEL_FONT = QFont("Noto Sans JP", 12, QFont.Weight.Bold)
    MONO_FONT = QFont("JetBrains Mono", 10)

    @classmethod
    def set_mode(cls, mode):
        cls.current_mode = mode
        if mode == cls.MODE_LIGHT:
            cls.BG_APP = "#F8F9FB"
            cls.BG_PANEL = "#eaeaea"
            cls.BG_CONTAINER = "#ffffff"
            cls.HOVER = "#E5E7EB"
            cls.TEXT_MAIN = "#1F1F1F"
            cls.TEXT_SECONDARY = "#6B7280"
            cls.BORDER = "#E5E7EB"
            cls.SECONDARY_BG_COLOR = "#F1F5F9"
            cls.ICON_PATH = "assets/icons/black/"
        else:
            cls.BG_APP = "#212121"
            cls.BG_PANEL = "#181818"
            cls.BG_CONTAINER = "#2e2e32"
            cls.HOVER = "#3a3a3a"
            cls.TEXT_MAIN = "#E5E7EB"
            cls.TEXT_SECONDARY = "#9CA3AF"
            cls.BORDER = "#2f2f2f"
            cls.SECONDARY_BG_COLOR = "#3a3a3a"
            cls.ICON_PATH = "assets/icons/white/"

        # Update global style caches
        cls.refresh_styles()

    @classmethod
    def detect_system_theme(cls):
        """Detects if system is in dark mode (PyQt6 specific)"""
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtGui import QPalette
            import sys

            palette = QApplication.palette(sys.argv)
            bg_color = palette.color(QPalette.ColorRole.Window)
            # Simple brightness detection
            if bg_color.lightness() < 128:
                return cls.MODE_DARK
            return cls.MODE_LIGHT
        except Exception:
            return cls.MODE_DARK

    @classmethod
    def refresh_styles(cls):
        cls.BUTTON_STYLE = f"""
            QPushButton {{
                background-color: {Theme.BG_CONTAINER};
                color: {Theme.TEXT_MAIN};
                border: 1px solid {Theme.BORDER};
                border-radius: 4px;
                padding: 2px 4px;
                text-align: center;
            }}

            QPushButton:hover,
            QPushButton:pressed {{
                background-color: {Theme.HOVER};
            }}

            QPushButton:disabled {{
                background-color: {Theme.SECONDARY_BG_COLOR};
                color: {Theme.TEXT_SECONDARY};
            }}
        """
        cls.DEFAULT_BUTTON_STYLE = f"""
            {cls.BUTTON_STYLE}
            QPushButton:default {{
                background-color: {Theme.PRIMARY};
                font-weight: 500;
                color: {Theme.WHITE};
                border: none;
            }}

            QPushButton:default:hover,
            QPushButton:default:pressed {{
                background-color: {Theme.PRIMARY_HOVER};
            }}
        """
        cls.BUTTON_WARNING_STYLE = f"""
            {cls.BUTTON_STYLE}
            QPushButton:checked {{
                background-color: {Theme.WARNING};
                color: {Theme.WHITE};
                border: none;
            }}
            QPushButton:checked:hover,
            QPushButton:checked:pressed {{
                background-color: {Theme.WARNING_HOVER};
            }}
        """
        cls.TOOLTIP_STYLE = f"""
            QToolTip {{
                background-color: {Theme.BG_CONTAINER};
                color: {Theme.TEXT_MAIN};
                border: 1px solid {Theme.BORDER};
                padding: 2px;
            }}
        """
        cls.TREEVIEW_STYLE = f"""
            QTreeView {{ 
                border: solid 1px {Theme.BORDER};
                border-radius: 4px; 
                background-color: {Theme.BG_PANEL}; 
                color: {Theme.TEXT_MAIN};
            }}
            QTreeView::item:hover {{ 
                background-color: {Theme.PRIMARY_BG_COLOR}; 
            }}
            QTreeView::item:selected {{ 
                background-color: {Theme.PRIMARY}; 
                color: {Theme.WHITE}; 
            }}
            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings  {{
                border-image: none;
                image: url({cls.ICON_PATH}arrow_right.svg);
            }}
            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings  {{
                border-image: none;
                image: url({cls.ICON_PATH}arrow_down.svg);
            }}
        """
        cls.SCROLLBAR_STYLE = f"""
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 6px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {cls.PRIMARY};
                min-height: 20px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {cls.PRIMARY_HOVER};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background: transparent;
                height: 6px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: {cls.PRIMARY};
                min-width: 20px;
                border-radius: 3px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {cls.PRIMARY_HOVER};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """

        cls.COMBOBOX_STYLE = f"""
            QComboBox {{
                border: 1px solid {cls.BORDER};
                border-radius: 4px;
                padding: 4px 10px;
                background-color: {cls.BG_PANEL};
                color: {cls.TEXT_MAIN};
            }}
            QComboBox:hover {{
                border-color: {cls.PRIMARY};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: url({cls.ICON_PATH}arrow_down.svg);
                border-left: 1px solid {cls.BORDER};
                border-right: none;
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {cls.BG_CONTAINER};
                color: {cls.TEXT_MAIN};
                font-size: 10pt;
                selection-background-color: {cls.PRIMARY};
                border: 1px solid {cls.BORDER};
                border-radius: 12px;
                outline: none;
            }}
            {cls.SCROLLBAR_STYLE}
        """

        cls.SPINBOX_STYLE = f"""
            QSpinBox {{
                background-color: {Theme.BG_PANEL}; 
                color: {Theme.TEXT_MAIN}; 
                border: 1px solid {Theme.BORDER}; 
                border-radius: 4px; 
                padding: 2px 6px;
            }}
            QSpinBox::up-button {{
                subcontrol-position: center right;
                margin-right: 2px;
            }}
            QSpinBox::down-button {{
                subcontrol-position: center left;
                margin-left: 2px;
            }}
            QSpinBox::up-button,
            QSpinBox::down-button {{
                border: solid 1px {Theme.BORDER};
                border-radius: 4px;
            }}
            QSpinBox::up-arrow {{
                border-image: url({cls.ICON_PATH}add.svg);
                width: 16px;
                height: 16px;
            }}
            QSpinBox::down-arrow {{
                border-image: url({cls.ICON_PATH}remove.svg);
                width: 16px;
                height: 16px;
            }}
        """

    # Initial style call
    TOOLTIP_STYLE = ""
    TREEVIEW_STYLE = ""
    SCROLLBAR_STYLE = ""
    COMBOBOX_STYLE = ""
    SPINBOX_STYLE = ""

    @classmethod
    def get_icon(cls, icon_name):
        path = os.path.join(cls.ICON_PATH, icon_name + ".svg")
        return QIcon() if not os.path.exists(path) else QIcon(path)
