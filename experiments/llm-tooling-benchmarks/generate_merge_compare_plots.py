#!/usr/bin/env python3
"""
Generate comparison plots across merge sizes for fixed entry counts.

The script scans the data directory for summary files that follow this pattern:
    model_<model-name>_size<entries>_merge<merge>_summary.json

For every model and each entries (size) value that has more than one merge
variant, a line plot is produced where:
    * X-axis is the merge size.
    * Y-axis is a metric extracted from the JSON file (numeric values).
    * Each line corresponds to a distinct model.

Charts are written to charts/merge_compare/size<entries>_<metric>.png.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt

from prices import PRICES

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "charts" / "merge_compare"

FILENAME_PATTERN = re.compile(
    r"^model_(?P<model>.+)_size(?P<size>\d+)_merge(?P<merge>\d+)_summary\.json$"
)
SKIP_KEYS = {"number of runs"}


def load_summaries(data_dir: Path) -> Dict[int, Dict[str, Dict[int, Dict[str, float]]]]:
    """
    Return nested dictionary:
        size -> model -> merge -> {metric: value}
    Only includes sizes where merge > 1 or multiple merge variations exist.
    """
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    data: Dict[int, Dict[str, Dict[int, Dict[str, float]]]] = defaultdict(lambda: defaultdict(dict))

    for file_path in data_dir.glob("model_*_summary.json"):
        match = FILENAME_PATTERN.match(file_path.name)
        if not match:
            continue

        size = int(match.group("size"))
        merge_size = int(match.group("merge"))
        model = match.group("model")

        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"Skipping {file_path.name}: {exc}")
            continue

        metrics = {}
        for key, value in payload.items():
            if key in SKIP_KEYS:
                continue
            if isinstance(value, (int, float)):
                metrics[key] = float(value)

        if "avg_input_tokens" in metrics or "avg_output_tokens" in metrics:
            cost = compute_cost_usd(
                payload.get("model name") or model,
                metrics.get("avg_input_tokens", 0.0),
                metrics.get("avg_output_tokens", 0.0),
            )
            metrics.setdefault("avg_cost_usd", cost)

        if not metrics:
            continue

        data[size][model][merge_size] = metrics

    return data


def normalize_model_key(name: str) -> str:
    if not name:
        return ""
    normalized = name.strip().lower()
    if normalized in PRICES:
        return normalized
    tail = normalized.split(".")[-1].split("/")[-1]
    if tail in PRICES:
        return tail
    for key in PRICES:
        if key in normalized:
            return key
    return ""


def compute_cost_usd(model_name: str, avg_input_tokens: float, avg_output_tokens: float) -> float:
    key = normalize_model_key(model_name)
    if not key or key not in PRICES:
        return 0.0
    input_price, output_price = PRICES[key]
    input_cost = (avg_input_tokens or 0.0) * (input_price / 1_000_000.0)
    output_cost = (avg_output_tokens or 0.0) * (output_price / 1_000_000.0)
    return input_cost + output_cost


def collect_metric_names(data: Dict[int, Dict[str, Dict[int, Dict[str, float]]]]) -> List[str]:
    names = set()
    for size_data in data.values():
        for model_data in size_data.values():
            for metrics in model_data.values():
                names.update(metrics.keys())
    return sorted(names)


def plot_for_size(
    size: int,
    models: Dict[str, Dict[int, Dict[str, float]]],
    metric_names: List[str],
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for metric in metric_names:
        plt.figure()
        plotted = False
        for model, merge_map in sorted(models.items()):
            pairs = [(merge, metrics[metric]) for merge, metrics in merge_map.items() if metric in metrics]
            if len(pairs) < 2:
                # Need at least two merge points to form a line
                continue
            pairs.sort()
            merge_values = [merge for merge, _ in pairs]
            metric_values = [value for _, value in pairs]
            label = model.replace("/", "_")
            plt.plot(merge_values, metric_values, marker="o", linewidth=2, label=label)
            plotted = True

        if not plotted:
            plt.close()
            continue

        plt.xlabel("Merge size")
        plt.ylabel(metric.replace("_", " ").title())
        plt.title(f"Size {size} – {metric.replace('_', ' ').title()}")
        plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)
        plt.legend()
        plt.tight_layout()
        out_path = OUTPUT_DIR / f"size{size}_{metric}.png"
        plt.savefig(out_path, dpi=150)
        plt.close()
        print(f"Wrote {out_path.relative_to(BASE_DIR)}")


def main() -> None:
    data = load_summaries(DATA_DIR)
    if not data:
        print("No summary files found.")
        return

    metric_names = collect_metric_names(data)
    for size, models in sorted(data.items()):
        # Only plot if there is at least one model with >1 merge value
        if all(len(merge_map) < 2 for merge_map in models.values()):
            continue
        plot_for_size(size, models, metric_names)


if __name__ == "__main__":
    main()
