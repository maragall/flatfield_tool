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

### Linux — XDG `.desktop` launcher (GNOME/KDE/XFCE, etc.)

1. **Create the file** `~/.local/share/applications/flatfield.desktop` with the following contents:

   ```ini
   [Desktop Entry]
   Type=Application
   Name=Cephla Flat‑field Tool
   Comment=Compute / apply flat‑field corrections (GUI)
   Exec=python3 -m flatfield.gui.flatfield_gui
   Icon=utilities-terminal   # replace with a custom icon path if desired
   Terminal=false
   Categories=Science;Graphics;
   ```
2. **Mark it executable**:

   ```bash
   chmod +x ~/.local/share/applications/flatfield.desktop
   ```
3. **Refresh** the application database:

   ```bash
   update-desktop-database ~/.local/share/applications || true
   ```
4. **Launch & pin**: open your desktop’s app menu, search for *Cephla Flat‑field Tool*, then drag it to the dock / favourites.

> **Wayland users:** the steps are identical—only the display server differs.

###   Windows 10 / 11

1. In the project root (or any folder on disk) create **`run-flatfield-gui.bat`**:

   ```bat
   @echo off
   REM Cephla Flat‑field Tool – launch GUI
   python -m flatfield.gui.flatfield_gui
   ```

   *If your Python executable is not on PATH, replace **`python`** with the full path to **`python.exe`** (e.g. **`C:\Users\<you>\AppData\Local\Programs\Python\Python312\python.exe`**).*
2. **Create a shortcut**:

   * Right‑click `run-flatfield-gui.bat` → *Send to* → *Desktop (create shortcut)*.
3. **Optional polish**:

   * Rename the shortcut to *Cephla Flat‑field Tool*.
   * Right‑click → *Properties* → *Shortcut* tab → *Change Icon…* → browse to a `.ico` file of your choice.
   * *Pin to Start* or *Pin to taskbar* for quick access.

> Running via the batch file avoids an unwanted console window. For a fully silent start use `pythonw` instead of `python`.

###   macOS (12 Monterey +)

#### Option A — `.command` script (simplest)

1. Create **`FlatfieldTool.command`** in the repository root:

   ```bash
   #!/usr/bin/env bash
   # Cephla Flat‑field Tool – launch GUI
   python3 -m flatfield.gui.flatfield_gui
   ```
2. Make it executable:

   ```bash
   chmod +x FlatfieldTool.command
   ```
3. Drag `FlatfieldTool.command` into the Dock (to the right of the divider).

#### Option B — Automator App (nicer icon & Spotlight‑searchable)

1. Open **Automator.app** → *New Document* → *Application*.
2. Add *Run Shell Script* action with:

   ```bash
   python3 -m flatfield.gui.flatfield_gui
   ```
3. Save as **`Cephla Flat‑field Tool.app`** in `/Applications`.
4. (Optional) Replace the generic icon: *Get Info* on the `.app`, then drag‑and‑drop a `512×512 ICNS` file onto the icon thumbnail.
5. Launch once, then right‑click the Dock icon → *Options* → *Keep in Dock*.

