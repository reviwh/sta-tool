# STA Translator Tool

STA Translator Tool is a desktop application built with PyQt6 that provides an intuitive graphical user interface for extracting, translating, and repacking string data from game files (e.g., `.sta` files).

## Features

- **Project Management**: Create, open, and manage translation projects with an integrated file tree.
- **String Extraction & Repacking**: Automatically extract translatable strings from supported file formats and securely repack them.
- **Plugin System**: Extend support to different games by adding custom JSON plugin schemas (e.g., *Kamen Rider Battride War*).
- **Search & Replace**: Efficiently find and modify specific dialogue lines across hundreds of files.
- **Auto-Save & Safe Close**: Tracks unsaved changes and automatically saves to a temporary backup to prevent data loss.
- **Modern UI**: Clean and customizable dark/fluid UI with configurable typography, smooth animations, and toast notifications.

## Requirements

- Python 3.9+
- [PyQt6](https://pypi.org/project/PyQt6/)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YourUsername/sta-tools.git
   cd sta-tools
   ```

2. (Optional but recommended) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To start the STA Translator Tool, simply run `main.py`:

```bash
python main.py
```

### Building an Executable

If you want to build a standalone executable using PyInstaller:

```bash
pyinstaller --name "STA Translator" --noconsole --windowed main.py
```

## Contributing

Contributions are welcome! If you have suggestions or bug reports, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
