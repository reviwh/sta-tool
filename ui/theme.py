from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import QApplication
import os
from core.utils import resource_path


class Theme:
    MODE_DARK = "dark"
    MODE_LIGHT = "light"
    current_mode = MODE_DARK
    _qss_cache = ""

    WARNING = "#E7A917"

    BG_APP = "#212121"
    BG_PANEL = "#181818"
    BG_CONTAINER = "#2e2e32"
    HOVER = "#3a3a3a"
    TEXT_MAIN = "#E5E7EB"
    TEXT_SECONDARY = "#9CA3AF"
    BORDER = "#2f2f2f"
    SECONDARY_BG_COLOR = "#3a3a3a"

    PRIMARY_BG_COLOR = "#803982F7"
    SUCCESS_BG_COLOR = "#8000C853"
    WARNING_BG_COLOR = "#80E7A917"
    TRANSPARENT = "#00000000"

    FONT_SIZE = 10
    SPACING = 8

    ICON_PATH = resource_path("assets/icons/white/")
    PRIMARY_ICON_PATH = resource_path("assets/icons/white/")

    FONT = QFont("Noto Sans JP", 10)
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
            cls.ICON_PATH = resource_path("assets/icons/black/")
        else:
            cls.BG_APP = "#212121"
            cls.BG_PANEL = "#181818"
            cls.BG_CONTAINER = "#2e2e32"
            cls.HOVER = "#3a3a3a"
            cls.TEXT_MAIN = "#E5E7EB"
            cls.TEXT_SECONDARY = "#9CA3AF"
            cls.BORDER = "#2f2f2f"
            cls.SECONDARY_BG_COLOR = "#3a3a3a"
            cls.ICON_PATH = resource_path("assets/icons/white/")

        cls._load_qss()

    @classmethod
    def _load_qss(cls):
        qss_file = os.path.join(
            resource_path("ui/styles"), f"{cls.current_mode}.qss"
        )
        try:
            with open(qss_file, "r", encoding="utf-8") as f:
                content = f.read()
            cls._qss_cache = content.replace("@ICON_PATH@", cls.ICON_PATH)
        except FileNotFoundError:
            cls._qss_cache = ""

    @classmethod
    def apply_qss(cls, app=None):
        if app is None:
            app = QApplication.instance()
        if app is None:
            return
        if not cls._qss_cache:
            cls._load_qss()
        app.setStyleSheet(cls._qss_cache)

    @classmethod
    def detect_system_theme(cls):
        try:
            from PyQt6.QtGui import QPalette
            app = QApplication.instance()
            if app is None:
                return cls.MODE_DARK
            palette = app.palette()
            bg_color = palette.color(QPalette.ColorRole.Window)
            if bg_color.lightness() < 128:
                return cls.MODE_DARK
            return cls.MODE_LIGHT
        except Exception:
            return cls.MODE_DARK

    @classmethod
    def get_icon(cls, icon_name):
        path = os.path.join(cls.ICON_PATH, icon_name + ".svg")
        return QIcon() if not os.path.exists(path) else QIcon(path)

    @classmethod
    def get_primary_icon(cls, icon_name):
        path = os.path.join(cls.PRIMARY_ICON_PATH, icon_name + ".svg")
        return QIcon() if not os.path.exists(path) else QIcon(path)
