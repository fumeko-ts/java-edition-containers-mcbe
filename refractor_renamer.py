import os  # refractor_renamer.py
import json
import re
import subprocess
import shutil


def remove_json_comments(text):
    text = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return text


def json_compact(obj, indent=2, level=0, max_inline_len=100):
    space = " " * (indent * level)
    next_space = " " * (indent * (level + 1))

    def is_primitive(val):
        return isinstance(val, (str, int, float, bool)) or val is None

    def is_simple(val):
        if is_primitive(val):
            return True
        if isinstance(val, dict) and all(is_primitive(v) for v in val.values()):
            return True
        return False

    if isinstance(obj, dict):
        if not obj:
            return "{}"

        items = []
        for k, v in obj.items():
            if is_primitive(v):
                items.append(f"{json.dumps(k)}: {json.dumps(v)}")
            else:
                items.append(f"{json.dumps(k)}: {json_compact(v, indent, level + 1)}")
        inline = "{" + ", ".join(items) + "}"
        if len(inline) <= max_inline_len:
            return inline

        lines = []
        for k, v in obj.items():
            val = json_compact(v, indent, level + 1, max_inline_len)
            lines.append(f"{next_space}{json.dumps(k)}: {val}")
        return "{\n" + ",\n".join(lines) + "\n" + space + "}"

    elif isinstance(obj, list):
        if not obj:
            return "[]"

        if all(isinstance(i, dict) and is_simple(i) for i in obj):
            inline_items = [
                json_compact(i, indent, level + 1, max_inline_len) for i in obj
            ]
            inline = "[ " + ", ".join(inline_items) + " ]"
            if len(inline) <= max_inline_len:
                return inline

        if all(is_primitive(i) for i in obj):
            inline = "[ " + ", ".join(json.dumps(i) for i in obj) + " ]"
            if len(inline) <= max_inline_len:
                return inline

        lines = [
            f"{next_space}{json_compact(i, indent, level + 1, max_inline_len)}"
            for i in obj
        ]
        return "[\n" + ",\n".join(lines) + "\n" + space + "]"

    else:
        return json.dumps(obj)


def replace_multiple_texts(obj, replacements):
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if k == "bindings":
                new_obj[k] = v
                continue

            if "#" in k or "$" in k or k.startswith("$"):
                new_key = k
            else:
                new_key = k
                for target_text, replacement_text in replacements:
                    new_key = new_key.replace(target_text, replacement_text)

            if isinstance(v, str):
                if "#" in v or "$" in v or v.startswith("$"):
                    new_val = v
                else:
                    new_val = v
                    for target_text, replacement_text in replacements:
                        new_val = new_val.replace(target_text, replacement_text)
            else:
                new_val = replace_multiple_texts(v, replacements)

            new_obj[new_key] = new_val
        return new_obj

    elif isinstance(obj, list):
        return [replace_multiple_texts(i, replacements) for i in obj]

    elif isinstance(obj, str):
        if "#" in obj or "$" in obj or obj.startswith("$"):
            return obj
        else:
            new_str = obj
            for target_text, replacement_text in replacements:
                new_str = new_str.replace(target_text, replacement_text)
            return new_str

    else:
        return obj

def refactor_text_in_files(root_dir, replacements):
    valid_extensions = {".json", ".atemp"}
    files_to_process = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if any(file.endswith(ext) for ext in valid_extensions):
                files_to_process.append(os.path.join(root, file))

    backups = []
    total_updated = 0

    for file_path in files_to_process:
        filename = os.path.basename(file_path)

        if filename == "_global_variables.json":
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            modified_content = content
            for target_text, replacement_text in replacements:
                modified_content = modified_content.replace(target_text, replacement_text)

            backup_path = file_path + ".bak_refractor"
            shutil.copyfile(file_path, backup_path)
            backups.append((file_path, backup_path))

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(modified_content)

            print(f"Refactored without formatting: {file_path}")
            total_updated += 1
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        cleaned_content = remove_json_comments(content)
        try:
            data = json.loads(cleaned_content)
        except json.JSONDecodeError as e:
            print(f"Skipping invalid JSON file: {file_path}\n  Error: {e}")
            continue

        backup_path = file_path + ".bak_refractor"
        shutil.copyfile(file_path, backup_path)
        backups.append((file_path, backup_path))

        new_data = replace_multiple_texts(data, replacements)
        formatted_json = json_compact(new_data, indent=2)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(formatted_json)

        dir_path, filename = os.path.split(file_path)
        new_filename = filename
        for target_text, replacement_text in replacements:
            if target_text in new_filename:
                new_filename = new_filename.replace(target_text, replacement_text)

        if new_filename != filename:
            new_file_path = os.path.join(dir_path, new_filename)
            try:
                os.rename(file_path, new_file_path)
                print(f"Renamed file: {file_path} -> {new_file_path}")
                backups[-1] = (new_file_path, backup_path)
                file_path = new_file_path
            except Exception as e:
                print(f"Failed to rename file {file_path}: {e}")

        print(f"Processed (cleaned/formatted): {file_path}")
        total_updated += 1

    print(f"Finished processing {total_updated} files.\n")

    if total_updated > 0:
        answer = input("Do you want to revert the changes? (y/N): ").strip().lower()
        if answer == "y":
            for orig_file, backup_file in backups:
                try:
                    shutil.copyfile(backup_file, orig_file)
                    os.remove(backup_file)
                    print(f"Reverted changes in {orig_file}")
                except Exception as e:
                    print(f"Failed to revert {orig_file}: {e}")
            print("Revert complete.")
        else:
            for _, backup_file in backups:
                try:
                    os.remove(backup_file)
                except:
                    pass


def search_text_in_files(root_dir, search_text):
    valid_extensions = {".json", ".atemp"}
    files_to_search = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if any(file.endswith(ext) for ext in valid_extensions):
                files_to_search.append(os.path.join(root, file))

    print(f"Searching for '{search_text}' in {len(files_to_search)} files...\n")
    found_any = False
    for file_path in files_to_search:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Could not read file {file_path}: {e}")
            continue

        matched_lines = []
        for idx, line in enumerate(lines, start=1):
            if search_text in line:
                matched_lines.append((idx, line.strip()))

        if matched_lines:
            found_any = True
            print(f"File: {file_path}")
            for lineno, line_content in matched_lines:
                print(f"  Line {lineno}: {line_content}")
            print()

    if not found_any:
        print(f"No occurrences of '{search_text}' found in any files.")


def run_ui_defs():
    ui_script_path = os.path.join("_ui_defs-updater.py")
    if os.path.isfile(ui_script_path):
        print(f"Running {ui_script_path} ...")
        try:
            subprocess.run([os.sys.executable, ui_script_path], check=True)
            print("_ui_defs-updater.py completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"_ui_defs-updater.py failed with error: {e}")
    else:
        print(f"{ui_script_path} not found, skipping run.")


def load_rr_config(config_path="rr.config"):
    if not os.path.exists(config_path):
        print(f"Config file '{config_path}' not found.")
        return True, []

    with open(config_path, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    replacements = []
    rename = True
    cleaned_lines = []

    for line in raw_lines:
        line = re.sub(r"//.*$", "", line).strip()
        if line:
            cleaned_lines.append(line)

    if not cleaned_lines:
        return rename, []

    if cleaned_lines[0].lower() == "rename = false":
        rename = False
        cleaned_lines = cleaned_lines[1:]
    elif cleaned_lines[0].lower() == "rename = true":
        rename = True
        cleaned_lines = cleaned_lines[1:]

    it = iter(cleaned_lines)
    try:
        while True:
            find = next(it).strip()
            replace = next(it).strip()
            replacements.append((find, replace))
    except StopIteration:
        pass

    return rename, replacements


if __name__ == "__main__":
    root_dir = "."

    use_config = input("Use rr.config? (y/N): ").strip().lower() == "y"
    if use_config:
        rename, replacements = load_rr_config()
        if not replacements:
            print("No valid replacements found in config. Exiting.")
        else:
            refactor_text_in_files(root_dir, replacements)
    else:
        while True:
            mode = (
                input("Do you want to perform a search-only? (y/N): ").strip().lower()
            )
            if mode == "y":
                search_text = input("Enter the text to search for: ").strip()
                if not search_text:
                    print("Empty search text, aborting search.")
                    continue
                search_text_in_files(root_dir, search_text)
                print("Search complete.\n")
            else:
                replacements = []
                while True:
                    target_text = input("Enter the text to find: ").strip()
                    if not target_text:
                        print("Empty input. Skipping.")
                        continue

                    replacement_text = input("Enter the replacement text: ").strip()
                    replacements.append((target_text, replacement_text))

                    more = (
                        input("Do you want to add another rename rule? (y/N): ")
                        .strip()
                        .lower()
                    )
                    if more != "y":
                        break

                if replacements:
                    refactor_text_in_files(root_dir, replacements)
                break

    run_ui_defs()
