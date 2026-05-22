#!/usr/bin/env python3
"""Compute the top-K total values achievable in a 0/1 knapsack.

Usage:
    kth_optimal.py --capacity V --k K --items "c,w; c,w; ..."

Each state holds a sorted descending list of the top-K values.  Transition
merges two sorted lists and keeps the first K.  O(VNK).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cli import parse_items

NEG = float("-inf")


def merge_top_k(a, b, K):
    out = []
    i = j = 0
    while len(out) < K and (i < len(a) or j < len(b)):
        if i < len(a) and (j >= len(b) or a[i] >= b[j]):
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    while len(out) < K:
        out.append(NEG)
    return out


def solve(items, V, K):
    F = [[NEG] * K for _ in range(V + 1)]
    for v in range(V + 1):
        F[v][0] = 0.0
    for C, W in items:
        new_F = [row[:] for row in F]
        for v in range(V, C - 1, -1):
            shifted = [x + W for x in F[v - C] if x != NEG]
            new_F[v] = merge_top_k(F[v], shifted, K)
        F = new_F
    return F[V]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capacity", "-V", type=int, required=True)
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("--items", required=True)
    args = ap.parse_args()
    items = parse_items(args.items)
    items = [(int(c), float(w)) for c, w in items]
    top = solve(items, args.capacity, args.k)
    print("top-K values (descending):")
    for r, v in enumerate(top, 1):
        print(f"  rank {r}: {v}")


if __name__ == "__main__":
    main()
