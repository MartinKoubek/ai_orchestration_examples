#!/usr/bin/env python3
"""
Aggregate JSON summary metrics by averaging numeric values across ID-suffixed files.

Example input files inside the data directory:
    model_openai.gpt-4.1-nano_size1_merge2_id211_summary.json
    model_openai.gpt-4.1-nano_size1_merge2_id218_summary.json

Running the script produces:
    model_openai.gpt-4.1-nano_size1_merge2_summary.json

Only numeric fields are averaged; non-numeric fields must match across the group
and are copied through unchanged. The aggregated JSON includes a "number of runs"
field indicating how many files contributed to the summary.
"""

from __future__ import annotations

import argparse
import json
import math
import os.path
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

SUMMARY_PATTERN = re.compile(r"^(?P<prefix>.+)_id[^_]+_summary\.json$")


def is_number(value: Any) -> bool:
    """Return True for JSON numeric values (ints/floats) but exclude booleans."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object at the top level.")
    return data


def collect_groups(data_dir: Path) -> dict[str, list[Path]]:
    groups: dict[str, list[Path]] = defaultdict(list)
    for path in data_dir.glob("*.json"):
        match = SUMMARY_PATTERN.match(path.name)
        if match:
            prefix = match.group("prefix")
            groups[prefix].append(path)
    return groups


def average_group(files: Iterable[Path]) -> tuple[dict[str, Any], list[str]]:
    sums: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    non_numeric: dict[str, Any] = {}
    key_order: list[str] = []
    warnings: list[str] = []

    file_list = list(files)
    if not file_list:
        return {}, warnings

    for path in sorted(file_list):
        data = read_json(path)
        for key in data:
            if key not in key_order:
                key_order.append(key)
        for key, value in data.items():
            if is_number(value):
                sums[key] += float(value)
                counts[key] += 1
            else:
                if key in non_numeric:
                    if value != non_numeric[key]:
                        warnings.append(
                            f"Inconsistent non-numeric value for '{key}' in {path.name}; using first encountered."
                        )
                else:
                    non_numeric[key] = value
        for key in sums:
            if counts[key] == 0:
                warnings.append(f"Numeric key '{key}' missing in {path.name}.")

    result: dict[str, Any] = {}
    total_files = len(file_list)
    for key in key_order:
        if key in sums:
            count = counts[key]
            if count == 0:
                continue
            result[key] = sums[key] / count
            if count != total_files:
                warnings.append(
                    f"Key '{key}' appears in {count}/{total_files} files; averaged over available values."
                )
        elif key in non_numeric:
            result[key] = non_numeric[key]

    # Include numeric keys that never appeared in key_order (if any).
    for key, total in sums.items():
        if key not in result and counts[key]:
            result[key] = total / counts[key]

    result["number of runs"] = total_files

    return result, warnings


def write_summary(output_path: Path, data: dict[str, Any]) -> None:
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")


def aggregate_directory(data_dir: Path, summary_dir: Path) -> None:
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory '{data_dir}' does not exist.")
    if not data_dir.is_dir():
        raise NotADirectoryError(f"Data directory '{data_dir}' is not a directory.")

    os.makedirs(summary_dir, exist_ok=True)

    groups = collect_groups(data_dir)
    if not groups:
        print(f"No matching summary files found in {data_dir}")
        return

    for prefix, files in sorted(groups.items()):
        output_path = summary_dir / f"{prefix}_summary.json"
        averaged, warnings = average_group(files)
        if not averaged:
            print(f"Skipping {prefix}: no data to write.")
            continue
        write_summary(output_path, averaged)
        print(f"Wrote {output_path.name} ({len(files)} files averaged)")
        for message in warnings:
            print(f"  warning: {message}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Average numeric fields across *_id*_summary.json files in the provided directory."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Directory containing the summary JSON files (default: ./data).",
    )

    parser.add_argument(
        "--summary-dir",
        type=Path,
        default=Path("summary"),
        help="Directory will create summary JSON files (default: ./data).",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    aggregate_directory(args.data_dir.resolve(), args.summary_dir.resolve())


if __name__ == "__main__":
    main()
