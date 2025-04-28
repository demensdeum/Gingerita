import os
import shutil
import subprocess
import sys

CRAFTROOT_PATH = "/Users/iliaprokhorov/CraftRoot/lib"
BIN_PATH = "/Users/iliaprokhorov/Sources/DemensDeum/Gingerita/bin"
APP_FRAMEWORKS_RPATH = "@executable_path/../Frameworks"
SKIP_ERRORS = False
CHECK_MISSING = False
error_files = []
missing_deps = set()

def run_command(cmd, file_path=None):
    """Run subprocess command and print."""
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Command FAILED!")
        if file_path:
            error_files.append(file_path)
        if not SKIP_ERRORS:
            sys.exit(1)

def is_macho(file_path):
    """Check if file is a Mach-O executable or dynamic library."""
    try:
        output = subprocess.check_output(["file", file_path], text=True)
        return "Mach-O" in output
    except subprocess.CalledProcessError:
        return False

def get_dependencies(file_path):
    """Get list of dependencies using otool."""
    try:
        output = subprocess.check_output(["otool", "-L", file_path], text=True)
        lines = output.splitlines()
        deps = []
        for line in lines[1:]:
            dep = line.strip().split(' ')[0]
            deps.append(dep)
        return deps
    except subprocess.CalledProcessError:
        return []

def get_rpaths(file_path):
    """Extract list of LC_RPATH entries."""
    try:
        output = subprocess.check_output(["otool", "-l", file_path], text=True)
        lines = output.splitlines()
        rpaths = []
        inside_rpath = False
        for line in lines:
            if "cmd LC_RPATH" in line:
                inside_rpath = True
            elif inside_rpath and "path" in line:
                path_value = line.strip().split(' ')[1]
                rpaths.append(path_value)
                inside_rpath = False
        return rpaths
    except subprocess.CalledProcessError:
        return []

def fix_rpath(file_path):
    """Fix LC_RPATH entries."""
    rpaths = get_rpaths(file_path)

    if CRAFTROOT_PATH in rpaths:
        print(f"Removing bad rpath {CRAFTROOT_PATH} from {file_path}")
        run_command(["install_name_tool", "-delete_rpath", CRAFTROOT_PATH, file_path], file_path)

    if APP_FRAMEWORKS_RPATH not in rpaths:
        print(f"Adding correct rpath {APP_FRAMEWORKS_RPATH} to {file_path}")
        run_command(["install_name_tool", "-add_rpath", APP_FRAMEWORKS_RPATH, file_path], file_path)
    else:
        print(f"✅ Correct rpath already present in {file_path}")

def fix_dependencies(file_path, app_path):
    """Fix dependency paths and install_name (id) for a given Mach-O file."""
    deps = get_dependencies(file_path)
    file_basename = os.path.basename(file_path)
    frameworks_dir = os.path.join(app_path, "Contents", "Frameworks")

    for dep in deps:
        dep_basename = os.path.basename(dep)

        if dep.startswith(CRAFTROOT_PATH) or dep.startswith(BIN_PATH):
            if dep_basename == file_basename:
                new_id = f"@rpath/{file_basename}"
                print(f"⚡ Fixing install_name (id) for {file_path}: {dep} -> {new_id}")
                run_command(["install_name_tool", "-id", new_id, file_path], file_path)
            else:
                new_dep = f"@rpath/{dep_basename}"
                print(f"⚡ Fixing dependency: {dep} -> {new_dep}")
                run_command(["install_name_tool", "-change", dep, new_dep, file_path], file_path)

def check_missing_dependency(dep, app_path):
    """Check if dependency exists inside the app."""
    frameworks_dir = os.path.join(app_path, "Contents", "Frameworks")
    dep_basename = os.path.basename(dep)
    dep_target = os.path.join(frameworks_dir, dep_basename)

    if not os.path.exists(dep_target):
        missing_deps.add(dep)

def patch_main_executable(exe_path):
    """Patch absolute dependencies inside the main executable to @rpath."""
    print(f"\n🔧 Patching main executable: {exe_path}")
    deps = get_dependencies(exe_path)
    for dep in deps:
        if dep.startswith(BIN_PATH) or dep.startswith(CRAFTROOT_PATH):
            dep_basename = os.path.basename(dep)
            if ".framework" in dep:
                framework_name = dep.split(".framework")[0].split("/")[-1]
                new_dep = f"@rpath/{framework_name}.framework/Versions/A/{framework_name}"
            else:
                new_dep = f"@rpath/{dep_basename}"

            print(f"⚡ Patching {dep} -> {new_dep}")
            run_command(["install_name_tool", "-change", dep, new_dep, exe_path])

    print("✅ Main executable patched.")

def process_app_bundle(app_path):
    """Walk through .app bundle and fix all executable/library dependencies."""
    print(f"🔍 Scanning: {app_path}")

    for root, dirs, files in os.walk(app_path):
        for file in files:
            file_path = os.path.join(root, file)

            # 🚫 Skip debug and object files
            if ".dSYM" in file_path or file_path.endswith(".o"):
                print(f"⚡ Skipping non-executable file: {file_path}")
                continue

            if is_macho(file_path):
                print(f"🛠 Processing Mach-O file: {file_path}")

                if CHECK_MISSING:
                    deps = get_dependencies(file_path)
                    for dep in deps:
                        if dep.startswith(CRAFTROOT_PATH) or dep.startswith(BIN_PATH):
                            check_missing_dependency(dep, app_path)
                else:
                    fix_rpath(file_path)
                    fix_dependencies(file_path, app_path)

    if CHECK_MISSING:
        if missing_deps:
            print("\n⚠️ Missing dependencies inside .app:")
            for dep in sorted(missing_deps):
                print(f" - {dep}")
            sys.exit(1)
        else:
            print("\n✅ No missing dependencies found!")

def verify_no_craftroot(app_path):
    """Verify that no CraftRoot paths are left in the binaries."""
    print("\n🔍 Verifying no CraftRoot paths left...")

    errors_found = False

    for root, dirs, files in os.walk(app_path):
        for file in files:
            file_path = os.path.join(root, file)
            if is_macho(file_path):
                deps = get_dependencies(file_path)
                for dep in deps:
                    if CRAFTROOT_PATH in dep or BIN_PATH in dep:
                        print(f"❌ Still found bad path in {file_path}: {dep}")
                        errors_found = True

    if errors_found:
        print("\n❌ External path leaks detected!")
        if not SKIP_ERRORS:
            sys.exit(1)
    else:
        print("✅ No external paths found! All clean.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path to .app> [--errors-skip] [--check-missing]")
        sys.exit(1)

    app_path = sys.argv[1]
    if not app_path.endswith(".app") or not os.path.isdir(app_path):
        print("Please provide a valid .app directory.")
        sys.exit(1)

    if "--errors-skip" in sys.argv:
        SKIP_ERRORS = True
        print("⚡ Running in --errors-skip mode!")

    if "--check-missing" in sys.argv:
        CHECK_MISSING = True
        print("🔍 Running in --check-missing mode!")

    process_app_bundle(app_path)

    if not CHECK_MISSING:
        # 🛠 Патчим главный исполняемый файл
        exe_path = os.path.join(app_path, "Contents", "MacOS", "kate")
        if os.path.exists(exe_path):
            patch_main_executable(exe_path)
        else:
            print(f"❗ No main executable found at {exe_path}")

        verify_no_craftroot(app_path)

    if error_files:
        print("\n⚠️ Files with errors during patching:")
        for file in sorted(set(error_files)):
            print(f" - {file}")
        print("\n⚠️ Some errors occurred!")
        sys.exit(1 if not SKIP_ERRORS else 0)
    else:
        print("\n✅ All files processed without critical errors.")
