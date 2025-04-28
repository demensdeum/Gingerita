import json
import os
import subprocess
import sys

if len(sys.argv) < 2:
    print("Usage: python patch_dependencies.py <input_json_file>")
    sys.exit(1)

input_json_path = sys.argv[1]

# Load the JSON
with open(input_json_path, 'r') as f:
    data = json.load(f)

# Prefixes
source_prefix = "/Users/iliaprokhorov/CraftRoot/lib/"
target_prefix = "@executable_path/../Frameworks/"

# Iterate through all files
for file in data["files"]:
    file_path = file["path"]
    for dep in file["dependencies"]:
        if dep.startswith(source_prefix):
            filename = os.path.basename(dep)
            new_dep = os.path.join(target_prefix, filename)
            print(f"Patching {file_path}: {dep} -> {new_dep}")

            # Execute install_name_tool command
            subprocess.run([
                "install_name_tool",
                "-change", dep, new_dep, file_path
            ], check=True)

print("✅ All dependencies have been patched using install_name_tool.")
