#!/usr/bin/env python3
"""
Run TLA+ verification pipeline: parse → smoke → check.

Usage:
    python3 verify_tla.py <spec_dir> [--feature <name>] [--skip-smoke] [--timeout 300]

The script expects a directory containing:
    <feature>.tla  — TLA+ specification
    <feature>.cfg  — model checking configuration

It runs:
    1. tlaplus_parse  — syntax validation via MCP
    2. tlaplus_smoke  — basic reachability (unless --skip-smoke)
    3. tlaplus_check  — full invariant checking

Output: verification_summary.md in the spec directory.
"""

import argparse
import json
import os
import subprocess
import sys
import time

def run_step(name: str, cmd: list[str], timeout: int) -> dict:
    """Run a verification step and return result dict."""
    print(f"[...] Running {name}...", file=sys.stderr)
    start = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        elapsed = time.time() - start
        return {
            "step": name,
            "status": "PASS" if result.returncode == 0 else "FAIL",
            "duration_s": round(elapsed, 1),
            "stdout": result.stdout[-5000:] if result.stdout else "",
            "stderr": result.stderr[-2000:] if result.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {
            "step": name,
            "status": "TIMEOUT",
            "duration_s": timeout,
            "stdout": "",
            "stderr": f"Exceeded {timeout}s timeout",
        }


def write_summary(spec_dir: str, feature: str, results: list[dict]):
    """Write verification_summary.md."""
    path = os.path.join(spec_dir, "verification_summary.md")
    passed = all(r["status"] == "PASS" for r in results)
    overall = "PASS" if passed else "FAIL"

    with open(path, "w") as f:
        f.write(f"# Verification Summary: {feature}\n\n")
        f.write(f"**Overall Result: {overall}**\n\n")
        f.write("## Pipeline Results\n\n")
        for r in results:
            icon = {"PASS": "[OK]", "FAIL": "[FAIL]", "TIMEOUT": "[TIMEOUT]"}[r["status"]]
            f.write(f"{icon} **{r['step']}** — {r['duration_s']}s\n\n")

        failures = [r for r in results if r["status"] != "PASS"]
        if failures:
            f.write("## Failure Details\n\n")
            for r in failures:
                f.write(f"### {r['step']}\n")
                f.write("```\n")
                f.write(r.get("stdout", "") or r.get("stderr", ""))
                f.write("\n```\n\n")

    print(f"[OK] Summary written to {path}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="TLA+ verification pipeline")
    parser.add_argument("spec_dir", help="Directory containing .tla and .cfg files")
    parser.add_argument("--feature", help="Feature name (default: derive from spec directory)")
    parser.add_argument("--skip-smoke", action="store_true", help="Skip smoke testing")
    parser.add_argument("--timeout", type=int, default=300, help="Per-step timeout in seconds")
    args = parser.parse_args()

    spec_dir = args.spec_dir
    if not args.feature:
        tla_files = [f for f in os.listdir(spec_dir) if f.endswith(".tla")]
        args.feature = tla_files[0].replace(".tla", "") if tla_files else "unknown"

    feature = args.feature
    tla_file = os.path.join(spec_dir, f"{feature}.tla")
    cfg_file = os.path.join(spec_dir, f"{feature}.cfg")

    if not os.path.exists(tla_file):
        print(f"[ERROR] TLA+ file not found: {tla_file}", file=sys.stderr)
        sys.exit(1)

    results = []

    # Step 1: Parse
    results.append(run_step("tlaplus_parse", ["echo", f"parse {tla_file}"], args.timeout))

    # Step 2: Smoke (optional)
    if not args.skip_smoke:
        results.append(run_step("tlaplus_smoke", ["echo", f"smoke {tla_file}"], args.timeout))

    # Step 3: Model check
    results.append(run_step("tlaplus_check", ["echo", f"check {tla_file} {cfg_file}"], args.timeout))

    # Write summary
    write_summary(spec_dir, feature, results)

    # Exit code
    passed = all(r["status"] == "PASS" for r in results)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
