"""
Convert an OpenSim .mot (or coordinate .sto with same header layout) to Excel.

Usage (single file):
  python backend/mot_to_excel.py --input path/to/motion.mot --output path/to/out.xlsx
  python backend/mot_to_excel.py --input path/to/motion.mot --output_dir D:/exports

Usage (whole folder — all *.mot):
  python backend/mot_to_excel.py --input path/to/Motionfiles --output_dir path/to/SpreadSheet

Default (no arguments): converts all *.mot from MOTIONFILES_INPUT_DIR -> EXCEL_OUTPUT_DIR
  python backend/mot_to_excel.py

Requires: pandas, openpyxl
  pip install pandas openpyxl
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
from io import StringIO
from typing import List

import pandas as pd

# ---------------------------------------------------------------------------
# Explicit paths (edit here for your PC). Used when you run this script with
# no command-line arguments.
# ---------------------------------------------------------------------------
MOTIONFILES_INPUT_DIR = r"C:\OpenSim 4.5\Resources\Models\WristModel\Motionfiles"
EXCEL_OUTPUT_DIR = r"C:\OpenSim 4.5\Resources\Models\WristModel\Motionfiles\SpreadSheet"


def _find_endheader_index(lines: List[str]) -> int:
    for i, line in enumerate(lines):
        if line.strip().lower() == "endheader":
            return i
    raise ValueError("Could not find 'endheader' in file (not a standard OpenSim .mot/.sto?).")


def load_opensim_mot_sto(path: str) -> pd.DataFrame:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    endheader_idx = _find_endheader_index(lines)
    col_line = lines[endheader_idx + 1].strip()
    col_names = col_line.split()

    data_start = endheader_idx + 2
    data_text = "".join(lines[data_start:]).strip()
    if not data_text:
        raise ValueError(f"No data rows after header in: {path}")

    df = pd.read_csv(
        StringIO(data_text),
        sep=r"\s+",
        header=None,
        names=col_names,
        engine="python",
    )
    return df


def mot_to_excel(input_path: str, output_path: str) -> None:
    df = load_opensim_mot_sto(input_path)
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    df.to_excel(output_path, index=False, engine="openpyxl")
    print(f"Wrote {len(df)} rows x {len(df.columns)} columns -> {output_path}")


def convert_mot_folder(input_dir: str, output_dir: str, recursive: bool = False) -> None:
    """Convert every *.mot in input_dir to .xlsx in output_dir."""
    input_path = os.path.abspath(input_dir)
    out_root = os.path.abspath(output_dir)
    os.makedirs(out_root, exist_ok=True)

    pattern = os.path.join(input_path, "**", "*.mot") if recursive else os.path.join(input_path, "*.mot")
    mot_files = sorted(glob.glob(pattern, recursive=recursive))
    if not mot_files:
        raise SystemExit(f"No .mot files found in: {input_path}")

    ok, fail = 0, 0
    for mot in mot_files:
        base = os.path.splitext(os.path.basename(mot))[0]
        output_path = os.path.join(out_root, f"{base}.xlsx")
        try:
            mot_to_excel(mot, output_path)
            ok += 1
        except Exception as e:
            print(f"[SKIP] {mot}: {e}", file=sys.stderr)
            fail += 1
    print(f"Done: {ok} converted, {fail} skipped -> {out_root}")


def run_with_default_paths() -> None:
    """Batch convert using MOTIONFILES_INPUT_DIR -> EXCEL_OUTPUT_DIR."""
    print(f"Input folder:  {MOTIONFILES_INPUT_DIR}")
    print(f"Output folder: {EXCEL_OUTPUT_DIR}")
    convert_mot_folder(MOTIONFILES_INPUT_DIR, EXCEL_OUTPUT_DIR, recursive=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert OpenSim .mot/.sto to Excel.")
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to one .mot/.sto file, or a folder of .mot files",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Full path to output .xlsx (single file input only)",
    )
    parser.add_argument(
        "--output_dir",
        "-d",
        help="Output folder: for a single input file writes <basename>.xlsx here; "
        "for a folder input, writes one .xlsx per .mot",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="With folder input, also search subfolders for *.mot",
    )
    args = parser.parse_args()

    input_path = os.path.abspath(args.input)

    if os.path.isdir(input_path):
        if not args.output_dir:
            raise SystemExit("Folder input requires --output_dir (e.g. ...\\Motionfiles\\SpreadSheet)")
        if args.output:
            raise SystemExit("Use --output_dir only when --input is a folder (not --output)")

        convert_mot_folder(input_path, args.output_dir, recursive=args.recursive)
        return

    if not os.path.isfile(input_path):
        raise SystemExit(f"Input not found: {input_path}")

    if not args.output and not args.output_dir:
        raise SystemExit("Single file input requires --output or --output_dir")

    if args.output:
        output_path = os.path.abspath(args.output)
        if not output_path.lower().endswith(".xlsx"):
            output_path += ".xlsx"
    else:
        base = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(os.path.abspath(args.output_dir), f"{base}.xlsx")

    mot_to_excel(input_path, output_path)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        run_with_default_paths()
    else:
        main()
