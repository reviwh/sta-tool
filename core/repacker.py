import json
import struct
import os
from pathlib import Path

import json
import struct
from pathlib import Path

def repack_from_json(json_path, output_root):
    with open(json_path, 'r', encoding='utf-8') as jf:
        project_data = json.load(jf)
    
    # Ambil data dari struktur baru
    header_info = project_data.get('header', {})
    content_list = project_data.get('content', [])
    output_base = Path(output_root)

    for file_data in content_list:
        # file_path di JSON berisi "FolderRoot/Sub/File.sta"
        # Kita ambil part setelah folder root agar tidak double folder saat repack
        parts = Path(file_data['file_path']).parts
        relative_path = Path(*parts[1:]) if len(parts) > 1 else Path(parts[0])
        
        new_file_path = output_base / relative_path
        new_file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(new_file_path, 'wb') as f:
                # 1. Header Magic (5 bytes sesuai extractor Anda)
                # Gunakan .ljust(5) untuk memastikan spasi tetap ada jika terhapus
                magic = header_info.get('magic', '\x00ATS ').encode('utf-8')
                f.write(magic[:5]) 
                
                # 2. Version (3 bytes) - Konversi kembali dari Hex
                version_hex = header_info.get('version', '120313')
                f.write(bytes.fromhex(version_hex))
                
                # 3. Total Lines (Total entries dalam file ini)
                entries = file_data['entries']
                f.write(struct.pack('>I', len(entries)))
                
                # 4. Reserved (4 bytes) - Konversi kembali dari Hex
                reserved_hex = header_info.get('reserved', '00000000')
                f.write(bytes.fromhex(reserved_hex))
                
                # 5. Strings Data
                for entry in entries:
                    text = entry['translated'] if entry.get('translated') else entry['original']
                    
                    text = text.replace('\\n', '\n')
                    encoded_text = text.encode('utf-8')
                    
                    f.write(struct.pack('>I', len(encoded_text)))
                    f.write(encoded_text)
                    
            print(f"✔️ Repacked: {new_file_path}")
        except Exception as e:
            print(f"❌ Error Repacking {relative_path}: {e}")

    return True