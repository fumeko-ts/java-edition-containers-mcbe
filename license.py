import os
import json

def add_header_to_files(root_folder):
    header = """// -------------------------------------------------------------------------
// JAVA CONTAINERS BEDROCK license info
// -------------------------------------------------------------------------
// © 2025 Ashura Temps. All rights reserved.
// 
// YOU MAY:
// - Use this pack normally in gameplay
// - Modify vanilla textures (Mojang-owned)
//
// YOU MAY NOT:
// - Reuse /ui or /atemp files and their contents in other packs 
// - use this pack for porting purpose's or eanything of the sort
// - use this as a base for a "client"
// - Upload to Marketplace
// - Post on MCPEDL without code obfuscation
//
// Full terms: https://github.com/fumeko-ts/java-edition-containers-mcbe
// Vanilla assets remain Mojang AB property.
// -------------------------------------------------------------------------
"""
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.endswith(('.json', '.atemp')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if content.startswith('// -------------------------------------------------------------------------'):
                        print(f"Skipped (header exists): {file_path}")
                        continue
                    if file.endswith('.json'):
                        try:
                            json.loads(content) 
                        except json.JSONDecodeError as e:
                            print(f"Skipped (invalid JSON): {file_path} - {str(e)}")
                            continue
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(header + '\n' + content)
                    print(f"Processed: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
if __name__ == "__main__":
    ui_folder = os.path.join(os.getcwd(), 'ui')
    if os.path.exists(ui_folder):
        add_header_to_files(ui_folder)
    else:
        print(f"Error: 'ui' folder not found at {ui_folder}")