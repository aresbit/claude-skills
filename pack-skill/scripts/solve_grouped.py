#!/usr/bin/env python3
"""Solve a grouped knapsack (at most one item per group).

Usage:
    solve_grouped.py --capacity V --groups "c,w | c,w | c,w ; c,w | c,w ; ..."

Each group is a |-separated list of c,w pairs. Groups are separated by ;.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pack_primitives import grouped_pack


def parse_groups(spec):
    spec = spec.strip().rstrip(";")
    groups = []
    for chunk in spec.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        group = []
        for pair in chunk.split("|"):
            pair = pair.strip()
            if not pair:
                continue
            c, w = pair.split(",")
            group.append((int(c.strip()), float(w.strip())))
        groups.append(group)
    return groups


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capacity", "-V", type=int, required=True)
    ap.add_argument("--groups", required=True)
    args = ap.parse_args()
    groups = parse_groups(args.groups)
    F = grouped_pack(args.capacity, groups)
    print(f"answer = {F[args.capacity]}")


if __name__ == "__main__":
    main()
