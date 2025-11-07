#!/usr/bin/env python3
"""
End-to-end experiment runner for the LangChain tools workflow.

The script iterates over a hard-coded list of experiment configurations,
where each tuple is (entries, merge_size, repetitions). For every repetition
it performs the following steps:
    1. generate_tools_json.py --entries <entries> --merge-size <merge_size>
    2. generate_java_tools.py
    3. mvn exec:java -Dexec.mainClass=com.martinkoubek.llm_tooling_benchmarks.ExperimentLangchainTools

Once all experiments are complete it post-processes results by invoking
average_statistics.py and prices.py.

Edit the EXPERIMENTS list below to customize the runs.
"""

from __future__ import annotations

import subprocess
import os
from pathlib import Path


# (entries, merge_size, repetitions)
EXPERIMENTS: list[tuple[int, int, int]] = [
    # (1, 1, 100),
    # (5, 1, 20),
    # (10, 1, 10),
    # (15, 1, 5),
    # (20, 1, 4),
    # (40, 1, 3),
    (60, 1, 2),
    # (80, 1, 2),
    #(100, 1, 1),
    # (100, 1, 1),
    # (120, 1, 1),
    # (30, 1, 2),
    # (60, 1, 2),
    # (90, 1, 2),
    # (120, 1, 2),

    # (60, 2, 2),
    # (60, 3, 2),
    # (60, 4, 2),
    # (60, 5, 2),
    # (60, 10, 2),
    # (30, 10, 2),

]


SCRIPT_DIR = Path(__file__).resolve().parent
# Project root is seven levels up from this script (src/main/java/...)
PROJECT_ROOT = SCRIPT_DIR.parents[1]
PYTHON = "python3"
MAIN_CLASS = "com.martinkoubek.llm_tooling_benchmarks.ExperimentLangchainTools"


def run_command(command: list[str], cwd: Path) -> None:
    """Run a subprocess command and raise if it fails."""
    print(f"\n>>> Running: {' '.join(command)} (cwd={cwd})")
    subprocess.run(command, cwd=str(cwd), check=True)


def main() -> None:
    env = os.environ.copy()
    env["JAVA_HOME"] = "/opt/jdk21"

    for entries, merge_size, repetitions in EXPERIMENTS:
        print(f"\n=== entries={entries}, merge_size={merge_size}, repetitions={repetitions} ===")
        for iteration in range(1, repetitions + 1):
            print(f"\n--- Iteration {iteration}/{repetitions} ---")
            run_command(
                [PYTHON, "generate_tools_json.py", "--entries", str(entries), "--merge-size", str(merge_size)],
                SCRIPT_DIR,
            )
            run_command([PYTHON, "generate_java_tools.py"], SCRIPT_DIR)
            run_command(
                ["mvn", "-q", "-DskipTests", "package"],
                PROJECT_ROOT,
            )
            run_command(
                ["mvn", "-q", "exec:java", f"-Dexec.mainClass={MAIN_CLASS}"],
                PROJECT_ROOT,
            )

    print("\n=== Post-processing summaries ===")
    run_command([PYTHON, "average_statistics.py"], SCRIPT_DIR)
    run_command([PYTHON, "generate_merge1_plots.py"], SCRIPT_DIR)
    run_command([PYTHON, "generate_merge_compare_plots.py"], SCRIPT_DIR)
    print("\nAll experiments completed.")


if __name__ == "__main__":
    main()
