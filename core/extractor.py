import json
import os
import re
import struct
from pathlib import Path

_COLOR_TAG_RE = re.compile(r"<COLOR=0x([0-9A-Fa-f]{8})>", re.IGNORECASE)


def collect_project_colors(content):
    """Return every unique color tag used in the project content."""
    colors = []
    seen = set()
    for file_entry in content:
        if not isinstance(file_entry, dict):
            continue
        entries = file_entry.get("entries", [])
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            for key in ("original", "translated"):
                text = entry.get(key)
                if not isinstance(text, str):
                    continue
                for match in _COLOR_TAG_RE.finditer(text):
                    color = "#" + match.group(1)[:6].lower()
                    if color not in seen:
                        seen.add(color)
                        colors.append(color)
    return colors


def extract_folder_to_json(input_folder, output_json):
    # 1. Normalisasi Nama File Output
    if not output_json.lower().endswith(".json"):
        output_json += ".json"

    base_path = Path(input_folder).resolve()
    root_folder_name = base_path.name
    # Cari semua file .sta secara rekursif
    files = list(base_path.rglob("*.sta"))

    if not files:
        print("Error: Tidak ada file .sta ditemukan.")
        return False

    # 2. Ambil Header dari file pertama sebagai referensi project
    header_data = {"magic": "", "version": "", "reserved": ""}
    try:
        with open(files[0], "rb") as f:
            header_data["magic"] = f.read(5).decode("utf-8", errors="ignore")
            header_data["version"] = f.read(3).hex()
            f.seek(12)
            header_data["reserved"] = f.read(4).hex()
    except Exception as e:
        print(f"Gagal membaca header sample: {e}")

    extracted_content = []

    # 3. Iterasi Semua File
    for file_path in files:
        try:
            # Gunakan folder induk sebagai root di dalam JSON path
            relative_path = file_path.relative_to(base_path)
            final_json_path = Path(root_folder_name) / relative_path

            with open(file_path, "rb") as f:
                # Cek Magic
                magic = f.read(5)
                if magic != b"\x00ATS ":
                    print(f"SKIP: {file_path} (Magic mismatch: {magic!r})")
                    continue

                # Baca total baris (Big Endian)
                f.seek(8)
                total_lines_data = f.read(4)
                if not total_lines_data:
                    continue
                total_lines = struct.unpack(">I", total_lines_data)[0]

                # Lompat ke awal konten string
                f.seek(16)
                entries = []

                MAX_LINES = 1_000_000
                if total_lines > MAX_LINES:
                    print(f"SKIP: {file_path} (too many lines: {total_lines})")
                    continue

                for _ in range(total_lines):
                    len_data = f.read(4)
                    if len(len_data) < 4:
                        break

                    length = struct.unpack(">I", len_data)[0]
                    if length > 100_000:
                        print(f"SKIP: {file_path} (string too long: {length} bytes)")
                        break

                    raw_content = f.read(length)

                    content = raw_content.decode("utf-8", errors="replace").replace("\n", "\\n")
                    entries.append({"original": content, "translated": ""})

                extracted_content.append(
                    {"file_path": str(final_json_path), "entries": entries}
                )
                print(f"Extracted: {final_json_path} ({total_lines} lines)")

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # 4. Susun Struktur Akhir
    new_structure = {
        "settings": {
            "font": {"name": "Noto Sans JP", "size": 12},
            "plugin": {"path": ""},
            "colors": collect_project_colors(extracted_content),
        },
        "header": header_data,
        "content": extracted_content,
    }

    # 5. Simpan ke JSON
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(new_structure, f, indent=4, ensure_ascii=False)

    return True
