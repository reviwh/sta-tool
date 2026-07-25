# STA Translator Tool — Agent Guide

## Stack

- Python 3.10+ / PyQt6 desktop app (single dependency: `PyQt6`)
- No tests, no linter, no formatter, no typechecker configured
- Entrypoint: `main.py` → `controller/app_controller.py:AppController` → `core/project_manager.py` (Model) + `ui/main_window.py:StaTranslator` (View)
- Repo-local skill available: `.agents/skills/pyqt6-ui-development-rules/SKILL.md`

## Commands

| Action | Command |
|--------|---------|
| Run | `./venv/bin/python main.py` |
| Build standalone | `pyinstaller app.spec` |
| CI build | GitHub Actions on release `published`; builds Linux + Windows |

## Project JSON format

```json
{
  "settings": { "font": { "name": "...", "size": 12 }, "plugin": { "path": "" } },
  "header": { "magic": "\\u0000ATS ", "version": "120313", "reserved": "00000000" },
  "content": [{ "file_path": "root/sub/file.sta", "entries": [{ "original": "...", "translated": "" }] }]
}
```

## .sta binary format (big-endian)

`\x00ATS ` (5B magic) + version (3B hex) + total lines (4B BE) + reserved (4B) + entries[] — each: 4B BE length + UTF-8 string. Newlines stored as `\n` in JSON, converted to/from `\\n` on extract/repack.

## Architecture (MVC)

```
main.py ──► controller/app_controller.py ──► core/project_manager.py  (Model)
                  │
                  ▼
           ui/main_window.py + ui/components/*  (View)
```

- **Model** (`core/`): `project_manager.py` — QObject with signals; owns lifecycle (load, save, extract, repack, autosave, CSV/TXT import/export, replace-all); `extractor.py` / `repacker.py` handle binary I/O
- **View** (`ui/`): `main_window.py:StaTranslator` — pure UI layout, theme, widget composition; components in `ui/components/`
- **Controller** (`controller/`): `app_controller.py:AppController` — coordinates Model ↔ View, handles all user actions, file dialogs, state management
- `ui/theme.py` — dark/light mode, SVG icon paths switch per mode
- `core/utils.py:resource_path()` — resolves PyInstaller `sys._MEIPASS` or cwd

## Plugins

- JSON list: `[{ "hex": "EE8080", "string": "[L-Analog]" }]` — replaces raw UTF-8 bytes with display tags
- **Auto-applied on project load**, reversed before repack, re-applied after (`project_manager.py:196-260`)
- Plugin path stored in `settings.plugin.path`; `plugins/` dir is gitignored

## Key behaviors

- **Autosave** every 5 min to `.{filename}.tmp` in project directory; deleted on manual save
- **Fonts**: `assets/fonts/NotoSansJP-Regular.ttf` + `JetBrainsMono.ttf` loaded at startup; persisted per-project in JSON `settings.font`
- **Icons**: `assets/icons/white/` (dark mode) / `assets/icons/black/` (light mode); SVG
- **Keyboard shortcuts**: `Ctrl+N` extract, `Ctrl+O` open, `Ctrl+S` save, `Ctrl+Shift+S` save-as, `Ctrl+W` close, `F5` repack, `Ctrl+P` apply plugin, `Ctrl+H` show shortcuts
- **Import**: TXT (line-by-line, entry count must match) and CSV (`file`, `original_text`, `translation` columns)
- **Export**: CSV with headers `file`, `original_text`, `translation`
- **Warning filter**: entries where `translated` has content but is only whitespace are flagged
- **Window title**: `STA Translator Tool - Folder/Name *` (asterisk when dirty)
