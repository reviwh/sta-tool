from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QColor

_ORG = "Reviwh"
_APP = "STA Translator"
_KEY = "custom_colors"
MAX_CUSTOM_COLORS = 6


def _settings():
    return QSettings(_ORG, _APP)


def _normalize(color):
    qcolor = QColor(color)
    if not qcolor.isValid():
        return None
    return qcolor.name()


def _save(colors):
    settings = _settings()
    settings.setValue(_KEY, colors)
    settings.sync()


def get_custom_colors():
    """Return cached custom colors, newest first, without duplicates."""
    stored = _settings().value(_KEY, [])
    if isinstance(stored, str):
        stored = [stored]

    colors = []
    seen = set()
    changed = False
    for color in stored:
        normalized = _normalize(color) if isinstance(color, str) else None
        if normalized is None or normalized in seen:
            changed = True
            continue
        seen.add(normalized)
        colors.append(normalized)

    if changed:
        _save(colors)
    return colors


def add_custom_color(color):
    """Move the given color to the front, keeping only the most recent ones."""
    normalized = _normalize(color)
    if normalized is None:
        return get_custom_colors()
    colors = [c for c in get_custom_colors() if c != normalized]
    colors.insert(0, normalized)
    colors = colors[:MAX_CUSTOM_COLORS]
    _save(colors)
    return colors


def trim_custom_colors():
    """Keep only the most recent custom colors and drop the rest."""
    stored = get_custom_colors()
    colors = stored[:MAX_CUSTOM_COLORS]
    if colors != stored:
        _save(colors)
    return colors
