import argparse
import logging
import sys
from pathlib import Path

# flat-field sub-commands
from flatfield.flatfield.compute import compute_flatfields
from flatfield.flatfield.apply   import apply_flatfields

# -----------------------------------------------------------------------------
# CLI parsing
# -----------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flatfield",
        description="Compute or apply flat‑field correction profiles for Cephla acquisitions.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    # compute ----------------------------------------------------------------
    p_compute = sub.add_parser("compute", help="Generate flatfield profiles (.npy + preview PNG)")
    p_compute.add_argument("acq_dir", type=Path, help="Acquisition directory")
    p_compute.add_argument("--max-per-channel", type=int, default=48, help="Max tiles per channel for BaSiC")
    p_compute.add_argument("--out", type=Path, help="Output directory for flatfields (default: <acq_dir>/flatfields)")

    # apply ------------------------------------------------------------------
    p_apply = sub.add_parser("apply", help="Apply existing flatfield profiles to one or more acquisitions")
    p_apply.add_argument("flatfield", type=Path, help="flatfield_manifest.json or directory containing .npy files")
    p_apply.add_argument("acq_dirs", nargs="+", type=Path, help="One or more acquisition directories to correct")
    p_apply.add_argument("--suffix", default="_ff", help="Suffix to append to corrected acquisition directory name")

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    return parser


def main(argv: list[str] | None = None) -> None:  # noqa: D401 – simple interface
    argv = argv if argv is not None else sys.argv[1:]
    parser = _build_parser()
    ns = parser.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if ns.verbose else logging.INFO)

    if ns.cmd == "compute":
        compute_flatfields(
            acq_dir=ns.acq_dir,
            max_per_channel=ns.max_per_channel,
            out_dir=ns.out,
            progress_cb=lambda i, t: logging.info("%d/%d channels done…", i, t),
        )
    elif ns.cmd == "apply":
        apply_flatfields(
            flatfield_source=ns.flatfield,
            acq_dirs=ns.acq_dirs,
            suffix=ns.suffix,
            progress_cb=lambda a, b: logging.info("%d/%d images corrected…", a, b),
        )
    else:  # pragma: no cover – argparser enforces
        parser.error(f"Unknown command {ns.cmd}")


if __name__ == "__main__":
    main()
