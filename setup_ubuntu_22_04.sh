#!/usr/bin/env bash
set -e

# 1) install system libs for Qt & OpenGL
sudo apt-get update && sudo apt-get install -y \
    libgl1 libxcb-icccm4 libxcb-image0 libxcb-render-util0 libxkbcommon-x11-0

# 2) ensure conda is present
if ! command -v conda &>/dev/null; then
  echo "Installing Miniconda..."
  MINI_DIR="$HOME/miniconda3"
  wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
  bash miniconda.sh -b -p "$MINI_DIR"
  rm miniconda.sh
  source "$MINI_DIR/bin/activate"
else
  source "$(conda info --base)/bin/activate"
fi

# 3) create & activate env
conda env create --file environment.yml
conda activate cephla-flatfield-tool

# 4) done
echo "    Environment ready! To use:"
echo "    conda activate cephla-flatfield-tool"
echo "    python -m flatfield.gui.flatfield_gui"
