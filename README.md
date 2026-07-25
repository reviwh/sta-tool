# STA Translator Tool

Desktop application built with PyQt6 for extracting, translating, and repacking string data from `.sta` game files.

## Features

- **Project Management** — Create, open, and manage translation projects with an integrated file tree
- **Extract & Repack** — Extract translatable strings from `.sta` files and repack them with translations
- **CSV Import/Export** — Import and export translations via CSV for external editing
- **Plugin System** — Extend support to different games via custom JSON plugin schemas
- **Search & Replace** — Find and replace across all entries in a project
- **Dark/Light Themes** — Toggle between dark and light mode
- **Copy to Clipboard** — Copy original text with one click

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
