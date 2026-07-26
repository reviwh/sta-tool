# STA Translator Tool — Agent Guide

## Stack

- Python 3.10+ / PyQt6 (single dep)
- No tests, linter, formatter, or typechecker
- Entrypoint: `main.py` → `ProjectManager` (Model) + `StaTranslator` (View) → `AppController` (Controller)
- Repo skill: `pyqt6-ui-development-rules` (managed via skills-lock.json)

## Commands

| Action | Command |
|--------|---------|
| Run | `./venv/bin/python main.py` |
| Build | `pyinstaller app.spec` (output: `dist/STA-Translator` or `.exe`) |
| CI | GitHub Actions on release `published`; builds Linux + Windows |

## Binary format (.sta, big-endian)

```
\x00ATS  (5B magic)
+ 3B version hex
+ 4B BE total lines
+ 4B BE reserved
+ entries[] each: 4B BE length + UTF-8 string
```

Newlines stored as `\n` in JSON, converted to/from `\\n` on extract/repack.

## Architecture (MVC)

All file I/O runs on the main thread (no `QThread` usage despite skill recommendations).

```
main.py — QApplication init, wires Model → View → Controller
  ├── core/project_manager.py  — QObject with signals; lifecycle owner
  │     (load, save, extract, repack, autosave, CSV/TXT import/export,
  │      replace-all, plugin apply/reverse)
  │     ├── core/extractor.py  — folder → project JSON
  │     └── core/repacker.py   — project JSON → .sta folder
  ├── ui/main_window.py:StaTranslator — QMainWindow, widget composition
  │   ├── ui/components/file_tree.py
  │   ├── ui/components/string_list.py
  │   ├── ui/components/editor_panel.py
  │   ├── ui/components/welcome_panel.py
  │   ├── ui/components/menu_bar.py
  │   ├── ui/components/replace_dialog.py
  │   ├── ui/components/shortcuts_dialog.py
  │   └── ui/components/toast.py
  ├── ui/theme.py:Theme — static class; holds color constants, QSS loading, icon paths
  └── controller/app_controller.py — QObject; connects all signals between Model ↔ View
```

All signals connected in `AppController._connect_signals()`. Window close goes through `view.close_handler = _on_close_requested` (set in controller).

## Key behaviors

- **Autosave** every 5 min to `.{filename}.tmp`; deleted on manual save
- **Editor save**: 500ms debounce timer before emitting `translation_changed`
- **Window title**: `STA Translator Tool - Folder/Name *` (asterisk when dirty)
- **Progress bar**: shows % of entries with non-whitespace translations
- **Copyright footer**: `© 2024 Revi Wardana Putra.`

## Plugins

- JSON list: `[{ "hex": "EE8080", "string": "[L-Analog]" }]`
- **Auto-applied on project load**, reversed before repack, re-applied after
- Plugin path stored in `settings.plugin.path`; `plugins/` dir gitignored
- Supports legacy dict format `{"hex": "string", ...}` (auto-converted)
- **Hex validation**: non-hex chars silently skipped (`continue` on invalid)

## Theme / Styling

- QSS files: `ui/styles/{dark,light}.qss` — **`@ICON_PATH@` placeholder replaced at runtime** by `Theme._load_qss()`
- Icons: `assets/icons/white/` (dark mode) / `assets/icons/black/` (light mode); SVG
- `Theme.set_mode()` switches color constants + `ICON_PATH`; calls `_load_qss()`
- `PRIMARY_ICON_PATH` is hardcoded to `assets/icons/white/` and **never switches** — used by `welcome_panel.py` icons (always white)
- System theme detected via `QPalette.ColorRole.Window` lightness: < 128 = dark

## Fonts

- `assets/fonts/NotoSansJP-Regular.ttf` + `JetBrainsMono.ttf` loaded at startup via `QFontDatabase.addApplicationFont()`
- Persisted per-project in JSON `settings.font` (name + size)
- `StaTranslator.__init__()` sets `self.font_family = "Noto Sans JP"` before fonts are loaded

## Imports / Exports

- **CSV columns**: `file`, `original_text`, `translation` (import matches by composite key `(file_path, original)`)
- **CSV import** supports duplicate keys (multiple matches per lookup)
- **TXT import**: per-file, line count must match exactly; each line is `.strip()`-ped
- **Replace All**: current file only, matches against `original` or `translated` (radio button)

## Build / Distribution

- `app.spec` bundles `assets/` as PyInstaller data; `console=False` (no terminal window)
- `core/utils.py:resource_path()` resolves to `sys._MEIPASS` if frozen, else `os.path.abspath(".")`
- UPX compression enabled; no macOS build in CI

## Gotchas

- **Repack output**: strips first component of `file_path` (the root folder) when writing via `Path(*parts[1:])`
- **Extracted JSON path**: `root_folder_name/relative/path/file.sta`
- **TXT import strips whitespace** via `.strip()` on every line — intentional blank entries with spaces are collapsed
- **Warning filter** matches entries where `len(trans.strip()) == 0 and len(trans) > 0` (whitespace-only); interacts with keyword filter (both conditions must match when warnings-only is on)
