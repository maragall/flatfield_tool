from __future__ import annotations
"""
Flat-field GUI with **two drag-and-drop tabs**:

* **Apply** – manifest (.npy/.json **or** folder) *plus* one acquisition folder
* **Compute** – unchanged logic: drop an acquisition folder to build profiles

UI tweaks requested 2025-05-19
--------------------------------
• Drop-box prompts are now un-bolded (plain text).
• When a valid payload is dropped the dashed outline becomes solid **and**
  the prompt changes to a success message (different for manifest vs acq).

Both tabs share the same threaded worker infrastructure and minimal progress
reporting.  Style constants are grouped at the top for easy tweaking.
"""

import logging
from pathlib import Path
from typing import Callable, Optional
import shutil
import numpy as np  # noqa: F401 – required by apply_flatfields/compute_flatfields
from PyQt5.QtCore import QThread, Qt, QTimer, pyqtSignal as Signal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMessageBox,
    QProgressBar,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from flatfield.functions.apply import apply_flatfields
from flatfield.functions.compute import compute_flatfields


# ──────────────────────────────── Styling ────────────────────────────────
DOWNLOADS = Path.home() / "Downloads"

_DASHED_STYLE = (
    "border: 2px dashed #999; border-radius: 8px; text-align: center; padding: 32px;"
)
_SOLID_STYLE = (
    "border: 2px solid  #999; border-radius: 8px; text-align: center; padding: 32px;"
)
_FLASH_OK_STYLE = (
    "border: 2px solid  #1faa00; background-color: rgba(31, 170, 0, 0.10);"
)
_FLASH_ERR_STYLE = (
    "border: 2px solid  #d32f2f; background-color: rgba(211, 47, 47, 0.10);"
)



# ─────────────────────────── Worker wrapper ──────────────────────────────
class _WorkerThread(QThread):
    progress = Signal(int, int)
    finished = Signal(Path)
    errored = Signal(str)

    def __init__(self, fn: Callable, *args, **kwargs):
        super().__init__()
        self._fn = fn
        self._args = args
        self._kwargs = kwargs

    def run(self):
        try:
            self._kwargs["progress_cb"] = lambda c, t: self.progress.emit(c, t)
            result = self._fn(*self._args, **self._kwargs)
            self.finished.emit(Path(result) if result else Path())
        except Exception as exc:  # pragma: no-cover – surfaced via GUI
            logging.exception("Worker crashed")
            self.errored.emit(str(exc))


# ──────────────────────────── Drop target ────────────────────────────────
class _DropTarget(QWidget):
    """Reusable drag-and-drop zone with success/error feedback."""

    files_dropped = Signal(list)  # list[Path]

    def __init__(self, prompt: str, success: str):
        super().__init__()
        self._prompt = prompt
        self._success = success

        self.setAcceptDrops(True)
        self._label = QLabel(prompt, self)
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setWordWrap(True)
        self._label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.addWidget(self._label)
        self.setStyleSheet(_DASHED_STYLE)

    # ――― D-n-D events ―――
    def dragEnterEvent(self, e: QDragEnterEvent):  # noqa: N802
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e: QDropEvent):  # noqa: N802
        paths = [Path(u.toLocalFile()) for u in e.mimeData().urls()]
        self.files_dropped.emit(paths)

    # ――― Visual feedback ―――
    def mark_success(self):
        """Solid outline + green flash."""
        self.setStyleSheet(_SOLID_STYLE)
        self._label.setText(self._success)
        self._flash(ok=True)

    def mark_error(self, msg: str):
        """Keep dashed outline, turn prompt red, flash red."""
        self.setStyleSheet(_DASHED_STYLE)
        self._label.setText(msg)
        self._flash(ok=False)

    def reset(self):
        """Restore dashed outline and original prompt."""
        self.setStyleSheet(_DASHED_STYLE)
        self._label.setText(self._prompt)

    # ――― helpers ―――
    def _flash(self, ok: bool):
        orig = self.styleSheet()
        extra = _FLASH_OK_STYLE if ok else _FLASH_ERR_STYLE
        self.setStyleSheet(orig + extra)
        QTimer.singleShot(300, lambda: self.setStyleSheet(orig))
    

# ───────────────────────────── Apply tab ────────────────────────────────
class _ApplyTab(QWidget):
    """Drop manifest first (or its folder), then one acquisition folder."""

    def __init__(self):
        super().__init__()
        self._worker: Optional[_WorkerThread] = None
        self._manifest: Optional[Path] = None
        self._acqs: list[Path] = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self._manifest_drop = _DropTarget(
            "Drop flat-field folder", "Flatfield file successfully dropped"
        )
        self._manifest_drop.files_dropped.connect(self._on_manifest_drop)

        self._acq_drop = _DropTarget(
            "Drop one acquisition folder", "Acquisition folder successfully dropped"
        )
        self._acq_drop.files_dropped.connect(self._on_acq_drop)

        self._prog = QProgressBar(self)
        self._prog.hide()
        self._status = QLabel("", self)
        self._status.setAlignment(Qt.AlignCenter)

        layout.addWidget(self._manifest_drop)
        layout.addWidget(self._acq_drop)
        layout.addWidget(self._prog)
        layout.addWidget(self._status)

    # ――― Manifest / acquisition handling ―――
    def _on_manifest_drop(self, paths: list[Path]):
        logging.debug(f"[MANIFEST DROP] got: {paths}")
        for p in paths:
            if self._try_set_manifest(p):
                logging.debug(f"[MANIFEST] set to {self._manifest}")
                self._manifest_drop.mark_success()
                break
        else:  # loop fell through → nothing valid
            self._manifest_drop.mark_error("Drop a flat-field folder")
        self._try_start()


    def _on_acq_drop(self, paths: list[Path]):
        logging.debug(f"[ACQ DROP] got: {paths}")
        dirs = [p for p in paths if p.is_dir()]
        if not dirs:
            self._acq_drop.mark_error("Drop one acquisition folder")
            return
        self._acqs.extend(dirs)
        logging.debug(f"[ACQS] now: {self._acqs}")
        self._acq_drop.mark_success()
        self._try_start()

    # ――― Job orchestration ―――
# ────────────────────── _ApplyTab._try_start (updated) ──────────────────────
    def _try_start(self):
        if self._worker or not (self._manifest and self._acqs):
            return

        # one Downloads-folder per acquisition
        out_dirs = [DOWNLOADS / f"{acq.name}_ff" for acq in self._acqs]

        for acq, out_root in zip(self._acqs, out_dirs):
            # ① copy the *entire* acquisition tree first (skip TIFFs – they’ll be
            #    overwritten by the corrected versions)
            shutil.copytree(
                acq,
                out_root,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("*.tif", "*.tiff", "*.tif*", "*.tiff*"),
            )

            # ② copy any JSON that lives next to the acquisition
            for js in acq.glob("*.json"):
                shutil.copy2(js, out_root / js.name)

        # hand off to the worker – it will overwrite the TIFFs in place
        self._status.setText("Applying…")
        self._prog.setRange(0, 0)
        self._prog.show()

        self._worker = _WorkerThread(
            apply_flatfields,
            flatfield_source=self._manifest,
            acq_dirs=self._acqs,
            out_dirs=out_dirs,
        )
        self._wire_worker()
        self._worker.start()


    def _wire_worker(self):
        assert self._worker
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(lambda p: self._reset_state(f"Completed → {p}"))
        self._worker.errored.connect(lambda msg: (
            QMessageBox.critical(self, "Error", msg),
            self._reset_state("")
        ))

    # ――― Helpers ―――
    @staticmethod
    def _find_manifest(directory: Path) -> Optional[Path]:
        for pat in ("*.json", "*.npy"):
            hits = list(directory.glob(pat))
            if hits:
                return hits[0]
        return None

    def _try_set_manifest(self, p: Path) -> bool:
        if p.is_file() and p.suffix in {".npy", ".json"}:
            self._manifest = p
            self._status.setText(f"Manifest: {p.name}")
            return True
        if p.is_dir():
            found = self._find_manifest(p)
            if found:
                self._manifest = found
                self._status.setText(f"Manifest: {found.name}")
                return True
        return False

    # ――― Progress / reset ―――
    def _on_progress(self, cur: int, tot: int):
        self._prog.setRange(0, tot)
        self._prog.setValue(cur)

    def _reset_state(self, status: str):
        self._prog.hide()
        self._status.setText(status)
        self._manifest = None
        self._acqs = []  # cleared (was _acq bug)
        self._worker = None
        # Visual reset if user repeats another round in same session:
        self._manifest_drop.reset()
        self._acq_drop.reset()


# ───────────────────────── Compute tab (unchanged) ──────────────────────
class _ComputeTab(QWidget):
    """Drag one acquisition folder → generates flat-field profiles."""

    def __init__(self):
        super().__init__()
        self._worker: Optional[_WorkerThread] = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        self._drop = _DropTarget(
            "Drop acquisition folder", "Acquisition folder successfully dropped"
        )
        self._drop.files_dropped.connect(self._on_drop)
        self._prog = QProgressBar(self)
        self._prog.hide()
        self._status = QLabel("", self)
        self._status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._drop)
        layout.addWidget(self._prog)
        layout.addWidget(self._status)

    def _on_drop(self, paths: list[Path]):
        acqs = [p for p in paths if p.is_dir()]
        if not acqs:
            self._drop.mark_error("Drop an acquisition folder")
            return
        self._drop.mark_success()
        self._kickoff(acqs[0])

    def _kickoff(self, acq: Path):
        out_dir = DOWNLOADS / f"flatfields_{acq.name}"
        out_dir.mkdir(exist_ok=True)
        self._status.setText("Computing…")
        self._prog.setRange(0, 0)
        self._prog.show()

        self._worker = _WorkerThread(
            compute_flatfields,
            acq_dir=acq,
            out_dir=out_dir,
            max_per_channel=48,
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(lambda _p: self._done(out_dir))
        self._worker.errored.connect(lambda msg: (
            QMessageBox.critical(self, "Error", msg),
            self._done("")
        ))
        self._worker.start()

    def _on_progress(self, cur: int, tot: int):
        self._prog.setRange(0, tot)
        self._prog.setValue(cur)

    def _done(self, out_dir: Path):
        self._prog.hide()
        self._status.setText(f"Done → {out_dir}")
        self._worker = None


# ───────────────────────────― Main window ───────────────────────────────
class FlatfieldGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cephla Flat-field Tool (Drag-and-Drop)")
        tabs = QTabWidget(self)
        tabs.addTab(_ApplyTab(), "Apply")
        tabs.addTab(_ComputeTab(), "Compute")
        layout = QVBoxLayout(self)
        layout.addWidget(tabs)
        self.setFixedSize(500, 430)


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    app = QApplication(sys.argv)
    gui = FlatfieldGUI()
    gui.show()
    sys.exit(app.exec())
