#!/usr/bin/env python3
"""Solve a mixed knapsack (each item declares its own copy policy).

Usage:
    solve_mixed.py --capacity V --items "kind:c,w[,m]; kind:c,w[,m]; ..."

where kind is one of: 01, complete, multiple (multiple requires the M field).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pack_primitives import complete_pack, multiple_pack, zero_one_pack


def parse_mixed(spec):
    spec = spec.strip().rstrip(";")
    items = []
    for chunk in spec.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        kind, rest = chunk.split(":", 1)
        parts = [p.strip() for p in rest.split(",")]
        nums = [float(p) if ("." in p or "e" in p or "E" in p) else int(p) for p in parts]
        items.append((kind.strip(), nums))
    return items


def solve(items, V):
    F = [0.0] * (V + 1)
    for kind, nums in items:
        if kind == "01":
            C, W = nums
            zero_one_pack(F, int(C), W)
        elif kind == "complete":
            C, W = nums
            complete_pack(F, int(C), W)
        elif kind == "multiple":
            C, W, M = nums
            multiple_pack(F, int(C), W, int(M))
        else:
            raise ValueError(f"unknown item kind: {kind}")
    return F[V]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capacity", "-V", type=int, required=True)
    ap.add_argument("--items", required=True)
    args = ap.parse_args()
    items = parse_mixed(args.items)
    print(f"answer = {solve(items, args.capacity)}")


if __name__ == "__main__":
    main()
