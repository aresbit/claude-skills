#!/usr/bin/env python3
"""Count the number of *optimal* schemes for a 0/1 knapsack instance.

Usage:
    count_optimal.py --capacity V --items "c,w; c,w; ..."

Returns the max value AND the number of distinct subsets achieving it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cli import parse_items


def solve(items, V):
    NEG = float("-inf")
    N = len(items)
    F = [[NEG] * (V + 1) for _ in range(N + 1)]
    G = [[0] * (V + 1) for _ in range(N + 1)]
    F[0][0] = 0.0
    for v in range(V + 1):
        F[0][v] = 0.0
    G[0][0] = 1
    for v in range(1, V + 1):
        G[0][v] = 1  # "take nothing" is the unique scheme for any v when ≤V semantics
    for i in range(1, N + 1):
        C, W = items[i - 1]
        for v in range(V + 1):
            skip_v = F[i - 1][v]
            take_v = F[i - 1][v - C] + W if v >= C else NEG
            best = max(skip_v, take_v)
            F[i][v] = best
            cnt = 0
            if skip_v == best:
                cnt += G[i - 1][v]
            if v >= C and take_v == best:
                cnt += G[i - 1][v - C]
            G[i][v] = cnt
    return F[N][V], G[N][V]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capacity", "-V", type=int, required=True)
    ap.add_argument("--items", required=True)
    args = ap.parse_args()
    items = parse_items(args.items)
    items = [(int(c), float(w)) for c, w in items]
    val, cnt = solve(items, args.capacity)
    print(f"max_value = {val}")
    print(f"optimal_scheme_count = {cnt}")


if __name__ == "__main__":
    main()
