#!/usr/bin/env python3
"""create_desktop_shortcut.py – generate a Desktop launcher for the
Cephla Flat‑field Tool GUI on **Ubuntu** (XDG‑compliant) and **Windows**.

Run from the project root:
    python3 create_desktop_shortcut.py

The script detects the current OS and writes a shortcut that executes
``python -m flatfield.gui.flatfield_gui`` with the project icon found at
``flatfield/gui/flatfield_icon.png`` (fallback ``icon.png``).
"""

from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path

# ────────────────────────────── helpers ───────────────────────────────────

def _find_icon(project_root: Path) -> Path:
    """Return the first valid PNG icon in flatfield/gui/."""
    for name in ("flatfield_icon.png", "icon.png"):
        p = project_root / "flatfield" / "gui" / name
        if p.exists():
            return p
    sys.exit("[ERROR] No icon PNG found in flatfield/gui/ (expected flatfield_icon.png or icon.png)")

# Windows --------------------------------------------------------------

def _windows_shortcut(project_root: Path, icon_png: Path, desktop: Path) -> None:
    """Create a .bat launcher *and* a .lnk shortcut on Windows."""
    bat_path = project_root / "start_flatfield_gui.bat"
    bat_content = (
        "@echo off\r\n"
        f"cd /d \"{project_root}\"\r\n"
        "python -m flatfield.gui.flatfield_gui\r\n"
    )
    bat_path.write_text(bat_content, encoding="utf-8")

    lnk_path = desktop / "Flatfield Tool.lnk"
    ps_cmd = (
        "$WshShell = New-Object -ComObject WScript.Shell; "
        f"$Shortcut = $WshShell.CreateShortcut('{lnk_path}'); "
        f"$Shortcut.TargetPath = '{bat_path}'; "
        f"$Shortcut.IconLocation = '{icon_png}'; "
        f"$Shortcut.WorkingDirectory = '{project_root}'; "
        "$Shortcut.Save()"
    )
    subprocess.run([
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy","Bypass",
        "-Command", ps_cmd,
    ], check=True)
    print(f"[OK] Windows shortcut created → {lnk_path}")

# Ubuntu / Linux -------------------------------------------------------

def _ubuntu_shortcut(project_root: Path, icon_png: Path, desktop: Path) -> None:
    """Create an XDG .desktop launcher on Ubuntu/Linux."""
    desktop_file = desktop / "flatfield_tool.desktop"
    python_exec = sys.executable  # absolute path to interpreter

    desktop_content = "\n".join([
        "[Desktop Entry]",
        "Type=Application",
        "Name=Cephla Flat-field",
        "Comment=Launch the Flat-field GUI",
        f"Path={project_root}",
        f"Exec={python_exec} -m flatfield.gui.flatfield_gui",
        f"Icon={icon_png}",
        "Terminal=false",
        "Categories=Graphics;Science;",
        ""
    ])

    desktop_file.write_text(desktop_content, encoding="utf-8")
    desktop_file.chmod(0o755)
    print(f"[OK] Ubuntu shortcut created → {desktop_file}")

# ─────────────────────────────── main ───────────────────────────────────

def main() -> None:
    project_root = Path(__file__).resolve().parent
    icon_png = _find_icon(project_root)

    desktop = Path.home() / "Desktop"
    desktop.mkdir(exist_ok=True)

    os_name = platform.system().lower()
    if os_name == "windows":
        _windows_shortcut(project_root, icon_png, desktop)
    elif os_name == "linux":
        _ubuntu_shortcut(project_root, icon_png, desktop)
    else:
        sys.exit("[ERROR] Unsupported OS: only Windows and Ubuntu are handled.")


if __name__ == "__main__":
    main()
