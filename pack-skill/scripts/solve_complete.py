#!/usr/bin/env python3
"""Solve a complete (unbounded) knapsack instance.

Usage:
    solve_complete.py --capacity V --items "c1,w1; c2,w2; ..." [--exact] [--verify]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cli import parse_items
from pack_primitives import NEG_INF, brute_max_complete, complete_pack


def solve(items, V, exact=False):
    F = [0.0] * (V + 1) if not exact else [0.0] + [NEG_INF] * V
    for C, W in items:
        complete_pack(F, int(C), W)
    if exact:
        ans = F[V]
        if ans == NEG_INF:
            return None
        return ans
    return F[V]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capacity", "-V", type=int, required=True)
    ap.add_argument("--items", required=True)
    ap.add_argument("--exact", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()

    items = parse_items(args.items)
    items = [(int(c), float(w)) for c, w in items]
    ans = solve(items, args.capacity, exact=args.exact)
    print(f"answer = {ans}")
    if args.verify and not args.exact:
        truth = brute_max_complete(items, args.capacity)
        ok = abs((ans or 0) - truth) < 1e-9
        print(f"brute-force = {truth}  ({'OK' if ok else 'MISMATCH'})")


if __name__ == "__main__":
    main()
