#!/usr/bin/env python3
"""
Build a trimmed tools JSON file from the master tools.json definition.

This script reads tools.json in the current directory, optionally samples it
down to a user-configurable size, and writes the result to tools_limited.json.
Each output entry includes a "prompt" string and a "tools" array containing the
primary tool names. Use the --entries flag to pick how many merged sets to emit
and --merge-size to control how many tools are combined per set (defaults: 10
entries, single tool per set). Run this script before generate_tools.py so the
Java generator can consume the freshly written JSON.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from random import random, randint

TOOLS_JSON = Path("tools.json")
LIMITED_JSON = Path("tools_limited.json")


def load_tools() -> list[dict[str, str]]:
    if not TOOLS_JSON.exists():
        raise FileNotFoundError(f"Expected tools.json at {TOOLS_JSON}")
    with TOOLS_JSON.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError("tools.json must contain a list of tool definitions.")
    tools: list[dict[str, str]] = []
    for entry in data:
        if not isinstance(entry, dict):
            raise ValueError("Each tool definition must be an object.")
        name = entry.get("name")
        prompt = entry.get("prompt")
        if not name:
            raise ValueError("Each tool must include 'name'.")
        tools.append(
            {
                "name": name,
                "prompt": prompt or "",
            }
        )
    return tools


def evenly_sample_tools(tools: list[dict[str, str]], total_needed: int) -> list[dict[str, str]]:
    total = len(tools)
    if total == 0:
        return []
    if total_needed >= total:
        return tools
    if total_needed <= 0:
        raise ValueError("total_needed must be positive")
    if total_needed == 1:
        return [tools[0]]
    step = (total - 1) / (total_needed - 1)
    selected = []
    for i in range(total_needed):
        index = int(round(i * step))
        selected.append(tools[index])
    unique = []
    seen = set()
    for tool in selected:
        name = tool["name"]
        if name not in seen:
            unique.append(tool)
            seen.add(name)
        if len(unique) == total_needed:
            break
    return unique


def merge_tools(tools: list[dict[str, str]], merge_size: int) -> list[dict[str, str]]:
    if merge_size <= 0:
        raise ValueError("merge size must be positive")
    merged: list[dict[str, str]] = []
    for index in range(0, len(tools), merge_size):
        chunk = tools[index : index + merge_size]
        names = [item["name"] for item in chunk]
        prompts = [item["prompt"] for item in chunk if item.get("prompt")]
        merged.append(
            {
                "prompt": " ".join(prompts).strip(),
                "tools": names,
            }
        )
    return merged


def parse_args() -> tuple[int, int]:
    parser = argparse.ArgumentParser(
        description=(
            "Build a sampled tools_limited.json file from tools.json. "
            "Use --entries to control how many merged tool sets are emitted, "
            "and --merge-size to define how many individual tools are combined per set."
        )
    )
    parser.add_argument(
        "--entries",
        type=int,
        default=10,
        help="Number of merged tool sets to emit (default: 10).",
    )
    parser.add_argument(
        "--merge-size",
        type=int,
        default=1,
        help="Number of individual tools merged into each set (default: 1).",
    )
    args = parser.parse_args()
    if args.entries <= 0:
        raise SystemExit("--entries must be greater than zero")
    if args.merge_size <= 0:
        raise SystemExit("--merge-size must be greater than zero")
    return args.entries, args.merge_size


def write_limited_json(tools: list[dict[str, str]], entries: int, merge_size: int) -> None:
    payload = {
        "id": randint(100, 999),
        "entries": entries,
        "merge_size": merge_size,
        "tools": tools,
    }
    LIMITED_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    num_entries, merge_size = parse_args()
    tools = load_tools()
    total_tools_needed = num_entries * merge_size
    if total_tools_needed > len(tools):
        raise SystemExit(
            f"Requested {num_entries} entries of {merge_size} tools each "
            f"({total_tools_needed} total), but only {len(tools)} tools are available."
        )
    sampled_tools = evenly_sample_tools(tools, total_tools_needed)
    merged_tools = merge_tools(sampled_tools, merge_size)
    write_limited_json(merged_tools, num_entries, merge_size)


if __name__ == "__main__":
    main()
