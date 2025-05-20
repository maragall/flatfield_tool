# Microscopy TIFF stacks → Squid acquisitions

## Install

**Clone the Repository:**

   ```bash
   git clone https://github.com/maragall/flatfield_tool.git
   cd flatfield_tool
   ```

**Install Dependencies with `uv`:**

   You can install it using pip:

   ```bash
   pip install uv
   ```

   Then, install the project dependencies:

   ```bash
   uv pip install -r pyproject.toml
   ```

### GUI

```bash
python -m flatfield.gui.flatfield_gui
```

### CLI

```bash
flatfield compute /path/to/acq
flatfield apply  /path/to/flatfields_*  /path/to/acq1 …
```

## Desktop Shortcut Setup (Ubuntu/Windows)

```bash
python3 create_desktop_shortcut.py
```
