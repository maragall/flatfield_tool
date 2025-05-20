#!/usr/bin/env python3
"""create_desktop_shortcut.py – generate a Desktop launcher for the
Cephla Flat‑field Tool GUI on **Ubuntu** (XDG‑compliant) and **Windows**.

Run from the project root:
    python3 create_desktop_shortcut.py

The script detects the current OS and writes a shortcut that executes
``python -m flatfield.gui.flatfield_gui`` with the project icon found at
``flatfield/gui/flatfield_icon.png``.

Imports used (kept here for dependency audit):
    import os, sys, platform, subprocess, shutil
    from pathlib import Path
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def _ensure_icon(icon_png: Path) -> None:
    if not icon_png.exists():
        sys.exit(f"[ERROR] Icon PNG not found: {icon_png}")


def _windows_shortcut(project_root: Path, icon_png: Path, desktop: Path) -> None:
    """Create a .bat launcher **and** a .lnk shortcut on Windows."""
    bat_path = desktop / "flatfield_tool.bat"
    bat_path.write_text(
        "@echo off\n"
        "python -m flatfield.gui.flatfield_gui\n",
        encoding="utf-8",
    )

    # PowerShell command for .lnk creation (avoids extra deps like pywin32).
    lnk_path = desktop / "Flatfield Tool.lnk"
    ps_cmd = (
        f"$WshShell = New-Object -ComObject WScript.Shell; "
        f"$Shortcut = $WshShell.CreateShortcut(\"{lnk_path}\"); "
        f"$Shortcut.TargetPath = \"{bat_path}\"; "
        f"$Shortcut.IconLocation = \"{icon_png}\"; "
        f"$Shortcut.WorkingDirectory = \"{project_root}\"; "
        f"$Shortcut.Save()"
    )
    subprocess.run([
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        ps_cmd,
    ], check=True)
    print(f"[OK] Windows shortcut created → {lnk_path}")


def _ubuntu_shortcut(icon_png: Path, desktop: Path) -> None:
    """Create a XDG .desktop launcher on Ubuntu/Linux."""
    desktop_file = desktop / "flatfield_tool.desktop"
    desktop_file.write_text(
        (
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=Cephla Flat‑field Tool\n"
            "Comment=Launch the Flat‑field GUI\n"
            "Exec=python3 -m flatfield.gui.flatfield_gui\n"
            f"Icon={icon_png}\n"
            "Terminal=false\n"
            "Categories=Graphics;Science;\n"
        ),
        encoding="utf-8",
    )
    desktop_file.chmod(0o755)
    print(f"[OK] Ubuntu shortcut created → {desktop_file}")


def main() -> None:
    project_root = Path(__file__).resolve().parent
    icon_png = project_root / "flatfield" / "gui" / "icon.png"
    _ensure_icon(icon_png)

    desktop = Path.home() / "Desktop"
    desktop.mkdir(exist_ok=True)

    system = platform.system().lower()
    if system == "windows":
        _windows_shortcut(project_root, icon_png, desktop)
    elif system == "linux":
        _ubuntu_shortcut(icon_png, desktop)
    else:
        sys.exit(f"[ERROR] Unsupported OS: {system}. Only Windows and Ubuntu are handled.")


if __name__ == "__main__":
    main()
