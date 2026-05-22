#!/usr/bin/env python3
"""Solve a multiple (bounded) knapsack instance.

Usage:
    solve_multiple.py --capacity V --items "c1,w1,m1; c2,w2,m2; ..." [--verify]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cli import parse_items
from pack_primitives import brute_max_multiple, multiple_pack


def solve(items, V):
    F = [0.0] * (V + 1)
    for C, W, M in items:
        multiple_pack(F, int(C), W, int(M))
    return F[V]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capacity", "-V", type=int, required=True)
    ap.add_argument("--items", required=True,
                    help='format: "c,w,m; c,w,m; ..."')
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()

    items = parse_items(args.items)
    items = [(int(c), float(w), int(m)) for c, w, m in items]
    ans = solve(items, args.capacity)
    print(f"answer = {ans}")
    if args.verify:
        truth = brute_max_multiple(items, args.capacity)
        ok = abs(ans - truth) < 1e-9
        print(f"brute-force = {truth}  ({'OK' if ok else 'MISMATCH'})")


if __name__ == "__main__":
    main()
