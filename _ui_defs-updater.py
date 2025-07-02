import os
import json

ROOT_DIR = "ui"
VALID_EXTENSIONS = {".atemp", ".json"}
ui_defs = []

for root, _, files in os.walk(ROOT_DIR):
    # Skip files that are directly inside the root folder (ui/)
    if root == ROOT_DIR:
        continue
    for file in files:
        if any(file.endswith(ext) for ext in VALID_EXTENSIONS):
            rel_path = os.path.relpath(os.path.join(root, file), ROOT_DIR).replace("\\", "/")
            full_path = f"ui/{rel_path}"
            if "_ui_defs.json" not in full_path:
                ui_defs.append(full_path)

output = { "ui_defs": ui_defs }
out_path = os.path.join(ROOT_DIR, "_ui_defs.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(f"{out_path} created with {len(ui_defs)} entries.")
