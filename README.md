# Cephla Flat‑field Tool

CLI + drag‑and‑drop GUI for BaSiC flat‑field corrections on microscopy TIFF stacks.

---

## Install

```bash
# clone → install in one step
pip install git+https://github.com/your-org/flatfield_tool.git

# or, from a checkout
pip install -r deps/dependencies.txt
```

*Python ≥ 3.9* · deps: numpy, scikit‑image, basicpy, PyQt5, matplotlib.

## Quick use

### GUI

```bash
python -m flatfield.gui.flatfield_gui
```

1. Drop the **flatfields** folder on *Apply* →
2. Drop acquisition folders.

Corrected images land in `~/Downloads/<acq>_ff/`.

### CLI

```bash
flatfield compute /path/to/acq
flatfield apply  /path/to/flatfields_*  /path/to/acq1 …
```

---

## Desktop shortcuts

### Linux (XDG *.desktop*)

1. Save file `~/.local/share/applications/flatfield.desktop`:

   ```ini
   [Desktop Entry]
   Type=Application
   Name=Cephla Flat‑field Tool
   Comment=Compute / apply flat‑field corrections (GUI)
   Exec=python3 -m flatfield.gui.flatfield_gui
   Icon=utilities-terminal
   Terminal=false
   Categories=Science;Graphics;
   ```
2. Make it executable: `chmod +x ~/.local/share/applications/flatfield.desktop`
3. Refresh the desktop database (`update-desktop-database`) or re‑log; then pin the launcher from the application menu.

### Windows (.bat + shortcut)

1. In the repo root create `run-flatfield-gui.bat`:

   ```bat
   @echo off
   REM Cephla Flat‑field Tool – launch GUI
   python -m flatfield.gui.flatfield_gui
   ```
2. Right‑click the file → *Send to → Desktop (create shortcut)*.
3. Rename / pin the shortcut to Start or the taskbar.

### macOS (.command)

1. Create `FlatfieldTool.command` (e.g., in the repo root):

   ```bash
   #!/usr/bin/env bash
   # Cephla Flat‑field Tool – launch GUI
   python3 -m flatfield.gui.flatfield_gui
   ```
2. `chmod +x FlatfieldTool.command`
3. Drag the script into the Dock.
