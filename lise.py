import os
import re

LICENSE_TEXT = """\
/**
// © 2025 ashura_temps,    All Rights Reserved.
//
// This UI is custom-made. You are allowed to use it **only as-is**, inside the game.
// Do not modify, extract, reuse, or share any part of this UI including .json, .atemp files,
// layout structure, or design.
//
// Not allowed:
//   - Editing the UI (even for private/personal use)
//   - Using parts of the code or layout in your own pack
//   - Reuploading, redistributing, or hosting these files elsewhere
//   - Converting texture packs to Bedrock using this UI
//
// By using this project, you agree to these terms.
*/
"""

SKIP_FILES = {"_ui_defs.json"}

def add_or_replace_license(file_path):
    filename = os.path.basename(file_path)
    if filename in SKIP_FILES:
        print(f"Skipping skipped file {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    license_pattern = r"^\s*/\*\*[\s\S]*?\*/\s*"

    if re.match(license_pattern, content, flags=re.MULTILINE):
        content_new = re.sub(license_pattern, LICENSE_TEXT + "\n", content, count=1, flags=re.MULTILINE)
        print(f"Replaced license in {file_path}")
    else:
        content_new = LICENSE_TEXT + "\n" + content
        print(f"Added license in {file_path}")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content_new)


if __name__ == "__main__":
    directory = "./ui"
    for root, _, files in os.walk(directory):
        for fname in files:
            if fname.endswith((".json", ".atemp")):
                add_or_replace_license(os.path.join(root, fname))
