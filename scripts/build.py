import platform
import subprocess
import sys
import shutil
import os
from pathlib import Path

def build_windows():
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "RF_Simulator_3D",
        "--icon", "resources/icons/app_icon.ico",
        "--add-data", "resources;resources",
        "--add-data", "templates;templates",
        "--distpath", "dist/windows",
        "--workpath", "build/windows",
        "src/main.py"
    ]
    subprocess.run(cmd)

def build_macos():
    cmd = [
        "pyinstaller",
        "--windowed",
        "--name", "RF Simulator 3D",
        "--icon", "resources/icons/app_icon.icns",
        "--add-data", "resources:resources",
        "--add-data", "templates:templates",
        "--distpath", "dist/macos",
        "--workpath", "build/macos",
        "--osx-bundle-identifier", "com.yourcompany.rfsimulator",
        "src/main.py"
    ]
    subprocess.run(cmd)
    app_path = "dist/macos/RF Simulator 3D.app"
    if Path(app_path).exists():
        resources_dir = Path(app_path) / "Contents" / "Resources"
        shutil.copytree("resources", resources_dir / "resources", dirs_exist_ok=True)
        shutil.copytree("templates", resources_dir / "templates", dirs_exist_ok=True)

def build_linux():
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", "rf-simulator-3d",
        "--add-data", "resources:resources",
        "--add-data", "templates:templates",
        "--distpath", "dist/linux",
        "--workpath", "build/linux",
        "src/main.py"
    ]
    subprocess.run(cmd)

def create_installers():
    if platform.system() == "Windows":
        subprocess.run([
            "iscc", "/Odist/windows", "installer/windows_installer.iss"
        ])
    if platform.system() == "Darwin":
        app_path = "dist/macos/RF Simulator 3D.app"
        dmg_path = "dist/macos/RF_Simulator_3D.dmg"
        subprocess.run([
            "hdiutil", "create",
            "-volname", "RF Simulator 3D",
            "-srcfolder", app_path,
            "-ov", dmg_path
        ])
    if platform.system() == "Linux":
        subprocess.run([
            "fpm", "-s", "dir", "-t", "deb",
            "-n", "rf-simulator-3d",
            "-v", "1.0.0",
            "-C", "dist/linux",
            "--prefix", "/usr/bin",
            "rf-simulator-3d"
        ])

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    if target in ["windows", "all"]:
        print("Building for Windows...")
        build_windows()
    if target in ["macos", "all"]:
        print("Building for macOS...")
        build_macos()
    if target in ["linux", "all"]:
        print("Building for Linux...")
        build_linux()
    print("Creating installers...")
    create_installers()
    print("Build completed successfully!")
