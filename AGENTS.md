# STA Translator Tool — Agent Guide

## Stack

- Python 3.10+ / PyQt6 desktop app (single dependency: `PyQt6`)
- No tests, no linter, no formatter, no typechecker configured
- Entrypoint: `main.py` → `ui/main_window.py:StaTranslator`

## Commands

| Action | Command |
|--------|---------|
| Run | `python main.py` |
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

`\x00ATS` (5B magic) + version (3B) + total lines (4B BE) + reserved (4B) + entries[] — each: 4B BE length + UTF-8 string. Newlines stored as `\n` in JSON, converted to/from `\\n`.

## Architecture

- `core/extractor.py` — reads `.sta` → JSON project
- `core/repacker.py` — writes JSON project → `.sta`
- `core/project_manager.py` — QObject with signals; owns lifecycle (load, save, extract, repack, autosave)
- `ui/` — PyQt6 components; `tool_bar`, `file_tree`, `string_list`, `editor_panel`, `welcome_panel`
- `ui/theme.py` — dark/light mode, SVG icon paths switch per mode

## Plugins

- JSON list: `[{ "hex": "EE8080", "string": "[L-Analog]" }]` — replaces raw UTF-8 bytes with display tags
- **Auto-applied on project load**, reversed before repack, re-applied after (`project_manager.py:195-259`)

## Key behaviors

- **Autosave** every 5 min to `.{filename}.tmp` in project directory
- **Fonts**: `assets/fonts/NotoSansJP-Regular.ttf` + `JetBrainsMono.ttf` loaded at startup
- **Icons**: `assets/icons/white/` (dark mode) / `assets/icons/black/` (light mode); SVG
- **Keyboard shortcuts**: `Ctrl+N` extract, `Ctrl+O` open, `Ctrl+S` save, `Ctrl+Shift+S` save-as, `Ctrl+W` close, `F5` repack, `Ctrl+P` apply plugin, `Ctrl+H` show shortcuts
- **Import TXT**: line-by-line translation import; entry count must match exactly
- **Warning filter**: entries where `translated` has content but is only whitespace are flagged

## Project convention

- Window title shows `STA Translator Tool - Folder/Name *` (asterisk when dirty)
- Plugin paths are stored in project JSON `settings.plugin.path`
- `resource_path()` in `core/utils.py` resolves PyInstaller `sys._MEIPASS` or cwd
