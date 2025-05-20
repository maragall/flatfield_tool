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

## Desktop Shortcut Setup

You can create a desktop shortcut (with the project icon) to launch the `flatfield_tool` GUI. First, ensure you have an icon file available in the project:

* Copy your icon (a `.png` file) into the `flatfield/gui/` directory of the project. For example:
  `~/Downloads/flatfield_tool/flatfield/gui/flatfield_icon.png` on macOS/Linux or
  `C:\Users\YourName\Downloads\flatfield_tool\flatfield\gui\flatfield_icon.png` on Windows.

Then follow the instructions for your operating system below.

### Windows

1. **Convert the icon (optional):** If your icon file is in PNG format, convert it to Windows `.ico` format. You can use an online converter or an image editing tool. Save the resulting `flatfield_icon.ico` file in the `flatfield/gui/` directory.
2. **Create a batch file:** Open Command Prompt and run:

   ```batch
   cd C:\Users\YourName\Downloads\flatfield_tool
   echo @echo off > start_flatfield.bat
   echo python -m flatfield.gui.flatfield_gui >> start_flatfield.bat
   ```

   This creates a file `start_flatfield.bat` that launches the GUI.
3. **Create a shortcut:** Right-click `start_flatfield.bat` in File Explorer and choose *Create shortcut*. Drag or copy the new shortcut to your Desktop.
4. **Set the icon:** Right-click the Desktop shortcut, select *Properties → Shortcut → Change Icon*, and browse to the `flatfield_icon.ico` file in the `flatfield/gui/` folder. Click *OK* to apply.
5. **Launch:** Double-click the shortcut to launch the `flatfield_tool` GUI.

### macOS

1. **Create a shell script:** Open Terminal and run:

   ```bash
   cd ~/Downloads/flatfield_tool
   echo "#!/bin/bash" > flatfield.command
   echo "python3 -m flatfield.gui.flatfield_gui" >> flatfield.command
   chmod +x flatfield.command
   ```

   This creates an executable `flatfield.command` script on your Desktop.
2. **Move to Desktop:** Copy the script to your Desktop:

   ```bash
   cp flatfield.command ~/Desktop/
   ```
3. **Set the icon:**

   * Open Finder and locate `flatfield.command` on your Desktop.
   * Select the file and choose *File → Get Info* (or press `Cmd+I`).
   * In a separate Finder window, open `flatfield_icon.png` from the `flatfield/gui/` folder.
   * Click the icon thumbnail in the Get Info window (top-left) and press `Cmd+V` to paste the image as the new icon.

Now, double-clicking the `flatfield.command` script on the Desktop will open the flatfield GUI. You can rename it (e.g., **Flatfield Tool**) in Finder if desired.

### Linux

1. **Create a `.desktop` file:** Open a terminal and run:

   ```bash
   cd ~/Downloads/flatfield_tool
   echo "[Desktop Entry]" > flatfield_tool.desktop
   echo "Name=Flatfield Tool" >> flatfield_tool.desktop
   echo "Comment=Launch Flatfield Tool GUI" >> flatfield_tool.desktop
   echo "Exec=python3 -m flatfield.gui.flatfield_gui" >> flatfield_tool.desktop
   echo "Icon=$(pwd)/flatfield/gui/flatfield_icon.png" >> flatfield_tool.desktop
   echo "Terminal=false" >> flatfield_tool.desktop
   echo "Type=Application" >> flatfield_tool.desktop
   echo "Categories=Graphics;" >> flatfield_tool.desktop
   chmod +x flatfield_tool.desktop
   mv flatfield_tool.desktop ~/Desktop/
   ```

   Make sure the `Icon=` path points to your `flatfield_icon.png` in the project directory.
2. **Trust and launch:** On some systems, you may need to right-click the new Desktop icon and select *Allow Launching* (or *Allow executing file as program* in Properties). After this, double-clicking the shortcut will launch the GUI.


