# Flat‑field Tool: Microscopy TIFF stacks -> Squid acquisitions

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
