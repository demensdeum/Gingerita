#!/usr/bin/env python3

import os
import sys
import json
import subprocess

def detect_type(filepath):
    try:
        output = subprocess.check_output(["file", filepath], encoding="utf-8", errors="ignore")
        if "shared object" in output or "dynamically linked shared library" in output:
            return "library"
        elif "executable" in output or "Mach-O" in output:
            return "executable"
        else:
            return None
    except subprocess.CalledProcessError:
        return None

def get_dependencies(filepath):
    try:
        output = subprocess.check_output(["otool", "-L", filepath], encoding="utf-8", errors="ignore")
        lines = output.splitlines()[1:]  # пропускаем первую строку
        deps = []
        for line in lines:
            dep = line.strip().split(' ')[0]
            deps.append(dep)
        return deps
    except subprocess.CalledProcessError:
        return []

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <directory> <output.json>")
        sys.exit(1)

    search_dir = sys.argv[1]
    output_json = sys.argv[2]

    if not os.path.isdir(search_dir):
        print(f"Error: {search_dir} is not a directory")
        sys.exit(1)

    result = []

    for root, dirs, filenames in os.walk(search_dir, followlinks=False):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            print(filepath)

            if os.path.islink(filepath):
                print("symlink")
                continue

            file_type = detect_type(filepath)
            if file_type:
                dependencies = get_dependencies(filepath)
                result.append({
                    "path": filepath,
                    "type": file_type,
                    "dependencies": dependencies
                })

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump({"files": result}, f, indent=2, ensure_ascii=False)

    print(f"Done! Output saved to {output_json}")

if __name__ == "__main__":
    main()
