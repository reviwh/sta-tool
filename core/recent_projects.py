import os

from PyQt6.QtCore import QSettings

MAX_RECENT = 5
_ORG = "Reviwh"
_APP = "STA Translator"
_KEY = "recent_projects"


def _settings():
    return QSettings(_ORG, _APP)


def _normalize(path):
    return os.path.normpath(os.path.abspath(path))


def _save(paths):
    settings = _settings()
    settings.setValue(_KEY, paths)
    settings.sync()


def get_recent_projects():
    """Return the recent project paths that still exist on disk."""
    stored = _settings().value(_KEY, [])
    if isinstance(stored, str):
        stored = [stored]

    paths = []
    seen = set()
    changed = False
    for path in stored:
        if not isinstance(path, str):
            changed = True
            continue
        normalized = _normalize(path)
        if normalized in seen or not os.path.isfile(normalized):
            changed = True
            continue
        seen.add(normalized)
        paths.append(normalized)

    if changed:
        _save(paths)
    return paths[:MAX_RECENT]


def add_recent_project(path):
    """Move the given project to the top of the recent list."""
    normalized = _normalize(path)
    paths = [p for p in get_recent_projects() if p != normalized]
    paths.insert(0, normalized)
    paths = paths[:MAX_RECENT]
    _save(paths)
    return paths


def remove_recent_project(path):
    """Remove the given project from the recent list."""
    normalized = _normalize(path)
    paths = [p for p in get_recent_projects() if p != normalized]
    _save(paths)
    return paths
