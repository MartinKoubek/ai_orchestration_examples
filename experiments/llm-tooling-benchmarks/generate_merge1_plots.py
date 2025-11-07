#!/usr/bin/env python3
"""
Generate line plots for merge-size 1 experiment summaries.

The script scans the data directory for files that follow the pattern:
    model_<model-name>_size<entries>_merge1_summary.json

For every numeric metric present in the JSON (excluding "number of runs"),
it builds a line chart where:
    * X-axis is the size value extracted from the filename.
    * Each line corresponds to a distinct model.
    * Y-axis is the metric value.

Charts are written to charts/merge1/<metric>.png.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt

from prices import PRICES

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "summary"
OUTPUT_DIR = BASE_DIR / "charts" / "merge1"

FILENAME_PATTERN = re.compile(
    r"^model_(?P<model>.+)_size(?P<size>\d+)_merge(?P<merge>\d+)_summary\.json$"
)
SKIP_KEYS = {"number of runs"}


def normalize_model_key(model: str) -> str:
    """Attempt to match a model name to a key in PRICES."""
    if not model:
        return ""
    normalized = model.strip().lower()
    if normalized in PRICES:
        return normalized
    tail = normalized.split(".")[-1].split("/")[-1]
    if tail in PRICES:
        return tail
    for key in PRICES:
        if key in normalized:
            return key
    return ""


def compute_cost_usd(model: str, avg_input_tokens: float, avg_output_tokens: float) -> float:
    key = normalize_model_key(model)
    if not key or key not in PRICES:
        return 0.0
    input_price, output_price = PRICES[key]
    input_cost = (avg_input_tokens or 0.0) * (input_price / 1_000_000.0)
    output_cost = (avg_output_tokens or 0.0) * (output_price / 1_000_000.0)
    return input_cost + output_cost


def load_merge1_summaries(data_dir: Path) -> Dict[str, Dict[int, Dict[str, float]]]:
    """Return nested dict model -> size -> metric -> value for merge-size == 1 summaries."""
    results: Dict[str, Dict[int, Dict[str, float]]] = {}
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    for file_path in data_dir.glob("model_*_summary.json"):
        match = FILENAME_PATTERN.match(file_path.name)
        if not match:
            continue

        merge_size = int(match.group("merge"))
        if merge_size != 1:
            continue

        model = match.group("model")
        size = int(match.group("size"))

        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"Skipping {file_path.name}: {exc}")
            continue

        metrics: Dict[str, float] = {}
        for key, value in data.items():
            if key in SKIP_KEYS:
                continue
            if isinstance(value, (int, float)):
                metrics[key] = float(value)

        if "avg_input_tokens" in metrics or "avg_output_tokens" in metrics:
            cost = compute_cost_usd(
                data.get("model name") or model,
                metrics.get("avg_input_tokens", 0.0),
                metrics.get("avg_output_tokens", 0.0),
            )
            metrics.setdefault("avg_cost_usd", cost)

        if not metrics:
            continue

        results.setdefault(model, {})[size] = metrics

    return results


def collect_metric_names(data: Dict[str, Dict[int, Dict[str, float]]]) -> List[str]:
    names = set()
    for model_data in data.values():
        for metrics in model_data.values():
            names.update(metrics.keys())
    return sorted(names)


def plot_metrics(data: Dict[str, Dict[int, Dict[str, float]]]) -> None:
    if not data:
        print("No merge=1 summaries found.")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    metric_names = collect_metric_names(data)

    for metric in metric_names:
        plt.figure()
        for model, size_map in sorted(data.items()):
            pairs = [(size, metrics[metric]) for size, metrics in size_map.items() if metric in metrics]
            if not pairs:
                continue
            pairs.sort()
            sizes = [size for size, _ in pairs]
            values = [value for _, value in pairs]
            label = model.replace("/", "_")
            label = label.split("_id")[0]
            plt.plot(sizes, values, marker="o", linewidth=2, label=label)

        plt.xlabel("Size")
        plt.ylabel(metric.replace("_", " ").title())
        plt.title(f"{metric.replace('_', ' ').title()} (merge size = 1)")
        plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)
        plt.legend()
        plt.tight_layout()
        out_path = OUTPUT_DIR / f"{metric}.png"
        plt.savefig(out_path, dpi=150)
        plt.close()
        print(f"Wrote {out_path.relative_to(BASE_DIR)}")


def main() -> None:
    data = load_merge1_summaries(DATA_DIR)
    plot_metrics(data)


if __name__ == "__main__":
    main()
