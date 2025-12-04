#!/usr/bin/env python3
"""Split a large pitch trajectories CSV into per-pitch CSV files.

Behavior:
- Reads the input CSV, preserving the header.
- Starts a new output file whenever the first column `time_diff` is exactly 0.0.
- If the file begins with rows before the first 0.0, those rows are placed into the first output file.

Usage:
    python scripts/split_pitches.py --input Data/SlidersTrajectoriesAustin.csv --outdir Data/split
"""

from __future__ import annotations
import argparse
import csv
import os
from pathlib import Path
from typing import List


def write_pitch(outdir: Path, base: str, idx: int, header: List[str], rows: List[List[str]]) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    filename = f"{base}_pitch_{idx:03d}.csv"
    outpath = outdir / filename
    with outpath.open("w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    return outpath


def split_file(input_path: Path, outdir: Path) -> None:
    base = input_path.stem
    pitch_idx = 0
    current_rows: List[List[str]] = []
    header: List[str] = []

    with input_path.open("r", encoding='utf-8', newline='') as fh:
        reader = csv.reader(fh)
        try:
            header = next(reader)
        except StopIteration:
            print("Input file is empty")
            return

        for row in reader:
            if not row:
                continue
            # Defensive: strip whitespace from first column
            t_str = row[0].strip()
            try:
                t = float(t_str)
            except Exception:
                # If parsing fails, treat as non-zero value and include it
                t = None

            # If we see an explicit 0.0, start a new pitch
            if t == 0.0:
                # If we already have buffered rows, write them as the previous pitch
                if current_rows:
                    pitch_idx += 1
                    path = write_pitch(outdir, base, pitch_idx, header, current_rows)
                    print(f"Wrote {path} ({len(current_rows)} rows)")
                    current_rows = []
                # Start a new pitch with this 0.0 row
                current_rows.append(row)
            else:
                # If we haven't started any pitch yet, start one so we don't lose pre-zero rows
                if not current_rows:
                    pitch_idx += 1
                current_rows.append(row)

    # After loop, write remaining buffer if present
    if current_rows:
        path = write_pitch(outdir, base, pitch_idx if pitch_idx>0 else 1, header, current_rows)
        print(f"Wrote {path} ({len(current_rows)} rows)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Split pitch trajectories CSV into per-pitch CSV files")
    parser.add_argument("--input", "-i", required=True, help="Path to input CSV file")
    parser.add_argument("--outdir", "-o", default="Data/split", help="Output directory for per-pitch CSVs")
    args = parser.parse_args()

    input_path = Path(args.input)
    outdir = Path(args.outdir)

    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    split_file(input_path, outdir)


if __name__ == "__main__":
    main()
