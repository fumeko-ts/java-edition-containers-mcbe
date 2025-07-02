import os
import chardet

def get_file_info(file_path):
    info = {}
    info['path'] = os.path.abspath(file_path)
    info['name'] = os.path.basename(file_path)
    info['size'] = os.path.getsize(file_path)

    # Try detecting encoding from first 4KB
    try:
        with open(file_path, 'rb') as f:
            raw = f.read(4096)
            result = chardet.detect(raw)
            encoding = result['encoding']
    except Exception:
        encoding = "Unknown"

    info['encoding'] = encoding

    # Try counting characters
    char_count = "N/A"
    if encoding:
        try:
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                char_count = len(f.read())
        except Exception:
            pass

    info['char_count'] = char_count
    return info

def scan_ui_folder():
    target_folder = './ui'
    output_path = 'file_report.txt'

    if not os.path.exists(target_folder):
        print("Folder './ui' not found.")
        return

    with open(output_path, 'w', encoding='utf-8') as report:
        for root, _, files in os.walk(target_folder):
            for filename in files:
                file_path = os.path.join(root, filename)
                info = get_file_info(file_path)

                report.write(f"Path        : {info['path']}\n")
                report.write(f"Name        : {info['name']}\n")
                report.write(f"Size (bytes): {info['size']}\n")
                report.write(f"Encoding    : {info['encoding']}\n")
                report.write(f"Characters  : {info['char_count']}\n")
                report.write("-" * 40 + "\n")

    print(f"Scan complete. Report saved to '{output_path}'.")

if __name__ == "__main__":
    scan_ui_folder()
