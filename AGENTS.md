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
  │      replace-all, plugin apply/reverse, undo/redo history)
  │     ├── core/extractor.py  — folder → project JSON
  │     ├── core/repacker.py   — project JSON → .sta folder
  │     └── core/undo_stack.py — EditCommand + UndoStack (history)
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

## Replace All

- Dialog: `ui/components/replace_dialog.py` — the **scope** tabs (`Current file` / `Whole project`) sit at the top; the find field, replace field, **match against** radio (`Original` / `Translated`) and case-sensitive checkbox live inside the tab content
- The form is a single widget that is **reparented** into the active tab page (`_move_form_to`), so both tabs share one state
- Each scope tab explains itself through a **tab tooltip** (`setTabToolTip`), not a label inside the page
- The `Current file` tab is only added when a file is selected (`ReplaceDialog(..., has_file=...)`); without it the dialog shows the `Whole project` tab alone
- Entry points: `Ctrl+H` (file scope), `Ctrl+Shift+H` (project scope) — both in the `&Edit` menu; the string-list button opens the dialog with the last used state
- The dialog is **modeless** (`show()`, not `exec()`): the main window stays fully usable while it is open, so files/entries can still be browsed before replacing
- The open dialog is kept in `AppController._replace_dialog`; opening it again just raises it and switches the scope, and it is closed when the project closes (`_on_project_closed` → `_close_replace_dialog`)
- `Ctrl+H` / `Ctrl+Shift+H` also work inside the dialog (own `QShortcut`s) to switch the scope tab
- The find/replace fields are single line: a line break is entered with `Shift+Enter` (or `Ctrl+Enter`) and is kept as the `\n` escape the data uses; pasted line breaks are converted the same way
- `ProjectManager.replace_all(..., scope="file"|"project")` returns `(replaced_count, matched_count, affected_files)`
- Project scope touches every file in `content` and is recorded as **one** undo command (`Replace All (Project)`), so a single `Ctrl+Z` reverts the whole run
- `ReplaceDialog.SCOPE_FILE` / `ReplaceDialog.SCOPE_PROJECT` are the scope constants; the dialog state (incl. scope) is cached in `AppController._replace_state`

## Undo / Redo

- `Ctrl+Z` undo, `Ctrl+Y` redo (also in the `&Edit` menu)
- **In the translation field** the text edit keeps its own history: `Ctrl+Z` / `Ctrl+Shift+Z` undo/redo the typed text while the field has focus
- **Everywhere else** the app history (`core/undo_stack.py`) takes over:
  - Editing a translation records one command per entry (all typing of that entry merges into a single command)
  - Undo of a translation restores the previous value **and moves the selection/focus back to that entry**
  - Replace All / TXT import / CSV import are recorded as one bulk command → undo reverts all of it, redo re-applies it
- The editor consumes `Ctrl+Z` / `Ctrl+Y` in `eventFilter` — a plain `QShortcut` never reaches the action because `QTextEdit` handles those keys itself
- History is cleared on project load/close; a new edit clears the redo stack

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
- **Replace All**: matches against `original` or `translated` (radio button); scope is `file` (current file) or `project` (all files)

## Build / Distribution

- `app.spec` bundles `assets/` as PyInstaller data; `console=False` (no terminal window)
- `core/utils.py:resource_path()` resolves to `sys._MEIPASS` if frozen, else `os.path.abspath(".")`
- UPX compression enabled; no macOS build in CI

## Gotchas

- **Repack output**: strips first component of `file_path` (the root folder) when writing via `Path(*parts[1:])`
- **Extracted JSON path**: `root_folder_name/relative/path/file.sta`
- **TXT import strips whitespace** via `.strip()` on every line — intentional blank entries with spaces are collapsed
- **Warning filter** matches entries where `len(trans.strip()) == 0 and len(trans) > 0` (whitespace-only); interacts with keyword filter (both conditions must match when warnings-only is on)
