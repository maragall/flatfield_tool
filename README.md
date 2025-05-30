# Microscopy TIFF stacks → Squid acquisitions

## Install

**Clone the Repository:**

   ```bash
   git clone https://github.com/maragall/flatfield_tool.git
   cd flatfield_tool
   ```

**Create & Activate Conda Environment:**

```bash
conda create -n flatfield python=3.10 -y
conda activate flatfield
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
   ```bash
   pip install basicpy
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
