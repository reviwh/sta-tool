# STA Translator Tool

Desktop application built with PyQt6 for extracting, translating, and repacking string data from `.sta` game files (proprietary big-endian binary format).

## Features

- **Extract & Repack** — Extract translatable strings from `.sta` files into a JSON project and repack them with translations
- **Project Management** — Open, save, and manage translation projects with an integrated file tree
- **CSV Import/Export** — Import and export translations via CSV for external editing
- **TXT Import** — Per-file text import with line-count validation
- **Plugin System** — Replace hex-encoded characters with human-readable tags via custom JSON plugin schemas
- **Search & Replace** — Find and replace across all entries in the current file
- **Dark/Light Themes** — Toggle between dark and light mode (auto-detects system theme)
- **Autosave** — Automatic backup every 5 minutes to a `.tmp` file

## Requirements

- Python 3.10+
- [PyQt6](https://pypi.org/project/PyQt6/)

## Installation

```bash
git clone https://github.com/reviwh/sta-tool.git
cd sta-tool
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

### Build Standalone Executable

```bash
pyinstaller app.spec
```

Pre-built binaries are available on the [Releases](https://github.com/reviwh/sta-tool/releases) page.

## License

MIT
