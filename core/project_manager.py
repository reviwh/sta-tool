from PyQt6.QtCore import QObject, pyqtSignal, QTimer
import csv
import json
import os
import re
from core.extractor import extract_folder_to_json
from core.repacker import repack_from_json


class ProjectManager(QObject):
    project_loaded = pyqtSignal(str)  # Emits path
    project_closed = pyqtSignal()
    data_changed = pyqtSignal()
    dirty_changed = pyqtSignal()
    error_occurred = pyqtSignal(str)
    status_message = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.full_data = {}
        self.path = None
        self.is_dirty = False
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)

    @staticmethod
    def validate_project_json(data):
        """Verify project JSON schema."""
        if not isinstance(data, dict):
            return False, "Project JSON must be an object"

        required_keys = ["settings", "header", "content"]
        for key in required_keys:
            if key not in data:
                return False, f"Missing required key: {key}"

        if not isinstance(data["content"], list):
            return False, "'content' must be a list"

        return True, "Valid project JSON"

    @staticmethod
    def validate_plugin_json(data):
        """Verify plugin JSON schema (list of hex/string objects)."""
        if not isinstance(data, list):
            return False, "Plugin JSON must be a list of objects"

        for i, item in enumerate(data):
            if not isinstance(item, dict):
                return False, f"Item at index {i} is not an object"
            if "hex" not in item:
                return False, f"Item at index {i} missing 'hex' key"
            if "string" not in item:
                return False, f"Item at index {i} missing 'string' key"

        return True, "Valid plugin JSON"

    @property
    def data(self):
        return self.full_data.get("content", [])

    def load(self, path):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                valid, msg = self.validate_project_json(data)
                if not valid:
                    self.error_occurred.emit(msg)
                    return False, msg

                self.full_data = data
                self.path = path
                self.is_dirty = False
                self.apply_plugin()  # Auto-apply plugin on load
                self.autosave_timer.start(300000)  # 5 minutes
                self.project_loaded.emit(path)
                return True, "Success"
            except Exception as e:
                self.error_occurred.emit(str(e))
                return False, str(e)
        return False, "File not found"

    def extract(self, src_folder, dest_json):
        """Extract folder to JSON and load it."""
        try:
            # Match extension handling in core.extractor
            if not dest_json.lower().endswith(".json"):
                dest_json += ".json"

            self.status_message.emit("Extracting folder...")
            if extract_folder_to_json(src_folder, dest_json):
                self.status_message.emit("Extraction complete")
                return self.load(dest_json)
            return False, "Extraction failed"
        except Exception as e:
            self.error_occurred.emit(f"Extraction failed: {e}")
            return False, str(e)

    def repack(self, out_dir):
        """Repack JSON back to binary folder."""
        if not self.is_active():
            return False, "No active project"

        try:
            self.status_message.emit("Repacking...")
            self.reverse_plugin()
            self.save()
            repack_from_json(self.path, out_dir)
            self.apply_plugin()  # Re-apply for UI
            self.save()
            self.status_message.emit("Repack complete")
            return True, "Success"
        except Exception as e:
            self.error_occurred.emit(f"Repack failed: {e}")
            return False, str(e)

    def import_txt(self, file_idx, txt_path):
        """Import translation from TXT file for a specific file index."""
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines()]

            entries = self.data[file_idx]["entries"]
            if len(lines) != len(entries):
                msg = f"Line count mismatch! TXT: {len(lines)}, JSON: {len(entries)}"
                self.error_occurred.emit(msg)
                return False, msg

            for i, line in enumerate(lines):
                entries[i]["translated"] = line

            self.is_dirty = True
            self.data_changed.emit()
            return True, "Success"
        except Exception as e:
            self.error_occurred.emit(f"Import failed: {e}")
            return False, str(e)

    def replace_all(self, file_idx, find_str, replace_str, case_sensitive, source_key):
        """Find and replace all occurrences in a file's entries."""
        if file_idx < 0 or file_idx >= len(self.data):
            return 0

        entries = self.data[file_idx]["entries"]
        change_count = 0
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.compile(re.escape(find_str), flags)

        for entry in entries:
            source_text = entry.get(source_key, "")
            target_text = entry.get("translated", "")

            if pattern.search(source_text):
                new_text, n = pattern.subn(replace_str, target_text)
                if n > 0:
                    entry["translated"] = new_text
                    change_count += n

        if change_count > 0:
            self.is_dirty = True
            self.data_changed.emit()

        return change_count

    def _get_plugins(self):
        settings = self.full_data.get("settings", {})
        plugin_path = settings.get("plugin", {}).get("path")
        if plugin_path and os.path.exists(plugin_path):
            try:
                with open(plugin_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Validate strict format
                valid, _ = self.validate_plugin_json(data)
                if valid:
                    return data

                # Fallback for legacy dict format: {"hex": "string"}
                if isinstance(data, dict):
                    return [{"hex": k, "string": v} for k, v in data.items()]

                # If list but invalid schema, try to filter
                if isinstance(data, list):
                    return [
                        item
                        for item in data
                        if isinstance(item, dict) and "hex" in item
                    ]

            except Exception as e:
                print(f"Error loading plugin file: {e}")
        return []

    def apply_plugin(self):
        plugins = self._get_plugins()
        if not plugins:
            return

        for file_item in self.full_data["content"]:
            for entry in file_item["entries"]:
                for p in plugins:
                    try:
                        hex_str = p.get("hex", "")
                        # Validate hex string
                        if not all(c in "0123456789abcdefABCDEF" for c in hex_str):
                            continue

                        raw_bytes = bytes.fromhex(hex_str)
                        target_char = raw_bytes.decode("utf-8")

                        if target_char in entry["original"]:
                            entry["original"] = entry["original"].replace(
                                target_char, p["string"]
                            )
                        if (
                            entry.get("translated")
                            and target_char in entry["translated"]
                        ):
                            entry["translated"] = entry["translated"].replace(
                                target_char, p["string"]
                            )
                    except Exception as e:
                        print(f"Plugin Error (Hex {p.get('hex')}): {e}")

    def reverse_plugin(self):
        """Convert tags back into characters before Repack (e.g., [Square] -> character)"""
        plugins = self._get_plugins()
        if not plugins:
            return

        for file_item in self.full_data["content"]:
            for entry in file_item["entries"]:
                for p in plugins:
                    try:
                        hex_str = p.get("hex", "")
                        # Validate hex string
                        if not all(c in "0123456789abcdefABCDEF" for c in hex_str):
                            continue

                        raw_bytes = bytes.fromhex(hex_str)
                        target_char = raw_bytes.decode("utf-8")

                        # Revert in original text
                        if p["string"] in entry["original"]:
                            entry["original"] = entry["original"].replace(
                                p["string"], target_char
                            )

                        # Revert in translated text
                        if (
                            entry.get("translated")
                            and p["string"] in entry["translated"]
                        ):
                            entry["translated"] = entry["translated"].replace(
                                p["string"], target_char
                            )
                    except Exception as e:
                        pass

    def export_csv(self, csv_path):
        """Export all entries to CSV with headers: file, original_text, translation."""
        try:
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["file", "original_text", "translation"])
                for item in self.data:
                    file_path = item["file_path"]
                    for entry in item["entries"]:
                        writer.writerow([
                            file_path,
                            entry["original"],
                            entry.get("translated", ""),
                        ])
            return True, "Success"
        except Exception as e:
            self.error_occurred.emit(f"CSV export failed: {e}")
            return False, str(e)

    def import_csv(self, csv_path):
        """Import translations from CSV matching by file and original_text."""
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames is None:
                    self.error_occurred.emit("CSV file is empty")
                    return False, "Empty CSV"

                required = {"file", "original_text", "translation"}
                if not required.issubset(reader.fieldnames):
                    msg = f"CSV missing required columns: {required - set(reader.fieldnames)}"
                    self.error_occurred.emit(msg)
                    return False, msg

                # Build lookup: (file_path, original) -> list of (file_idx, entry_idx)
                lookup = {}
                for file_idx, item in enumerate(self.data):
                    for entry_idx, entry in enumerate(item["entries"]):
                        key = (item["file_path"], entry["original"])
                        lookup.setdefault(key, []).append((file_idx, entry_idx))

                count = 0
                for row in reader:
                    key = (row["file"], row["original_text"])
                    matches = lookup.get(key)
                    if matches:
                        for file_idx, entry_idx in matches:
                            self.data[file_idx]["entries"][entry_idx]["translated"] = row["translation"]
                            count += 1

            if count > 0:
                self.is_dirty = True
                self.data_changed.emit()
                self.status_message.emit(f"Imported {count} translations from CSV")
            return True, "Success"
        except Exception as e:
            self.error_occurred.emit(f"CSV import failed: {e}")
            return False, str(e)

    def update_translation(self, file_idx, string_idx, text):
        if file_idx < 0 or string_idx < 0:
            return

        if self.data:
            self.data[file_idx]["entries"][string_idx]["translated"] = text
            if not self.is_dirty:
                self.is_dirty = True
                self.dirty_changed.emit()

    def save(self, path=None):
        save_path = path if path else self.path
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(self.full_data, f, indent=4, ensure_ascii=False)
            if save_path == self.path:
                self.is_dirty = False
                
                # Hapus file autosave jika ada
                tmp_path = os.path.join(os.path.dirname(self.path), f".{os.path.basename(self.path)}.tmp")
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
                
                # Timer tetap direstart untuk mulai loop baru dari awal sejak point save
                self.autosave_timer.start(300000)

    def close(self):
        self.autosave_timer.stop()
        self.full_data = {}
        self.path = None
        self.is_dirty = False
        self.project_closed.emit()

    def autosave(self):
        if self.path and self.is_dirty:
            filename = os.path.basename(self.path)
            dirname = os.path.dirname(self.path)
            tmp_path = os.path.join(dirname, f".{filename}.tmp")
            try:
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(self.full_data, f, indent=4, ensure_ascii=False)
                self.status_message.emit(f"Autosaved to .{filename}.tmp")
            except Exception as e:
                print(f"Autosave failed: {e}")

    def is_active(self):
        return bool(self.full_data and "content" in self.full_data)

    def get_filtered_files(self, keyword, show_warnings_only=False):
        if not keyword and not show_warnings_only:
            return [item["file_path"] for item in self.data]

        keyword = keyword.lower() if keyword else ""
        filtered = []
        for item in self.data:
            match = False
            for entry in item["entries"]:
                trans = entry.get("translated", "")

                # Warning condition: has content but only whitespace
                is_warning = len(trans.strip()) == 0 and len(trans) > 0

                if show_warnings_only:
                    if is_warning:
                        if not keyword or (
                            keyword in entry["original"].lower()
                            or keyword in trans.lower()
                        ):
                            match = True
                            break
                else:
                    if not keyword or (
                        keyword in entry["original"].lower() or keyword in trans.lower()
                    ):
                        match = True
                        break

            if match:
                filtered.append(item["file_path"])
        return filtered

    def get_filtered_entries(self, file_idx, keyword, show_warnings_only=False):
        """Mengembalikan daftar (index_asli, entry) yang cocok dengan keyword."""
        keyword = keyword.lower() if keyword else ""
        results = []

        for i, e in enumerate(self.data[file_idx]["entries"]):
            trans = e.get("translated", "")
            is_warning = len(trans.strip()) == 0 and len(trans) > 0

            if show_warnings_only:
                if not is_warning:
                    continue

            if not keyword or (
                keyword in e["original"].lower() or keyword in trans.lower()
            ):
                results.append((i, e))

        return results
