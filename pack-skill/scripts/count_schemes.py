#!/usr/bin/env python3
"""Count the number of feasible schemes for a knapsack instance.

Usage:
    count_schemes.py --capacity V --kind {01,complete} --items "c1,w1; c2,w2; ..."

For 01 pack: counts subsets summing to exactly V (ignore value field; just pass any).
For complete pack: counts multisets of item-types summing to exactly V.
The value field is ignored (replaced by 1 internally) — we are counting compositions.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cli import parse_items


def count_01(costs, V):
    F = [0] * (V + 1)
    F[0] = 1
    for C in costs:
        for v in range(V, C - 1, -1):
            F[v] += F[v - C]
    return F[V]


def count_complete(costs, V):
    F = [0] * (V + 1)
    F[0] = 1
    for C in costs:
        for v in range(C, V + 1):
            F[v] += F[v - C]
    return F[V]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capacity", "-V", type=int, required=True)
    ap.add_argument("--kind", choices=["01", "complete"], required=True)
    ap.add_argument("--items", required=True,
                    help='format: "c1[,w1]; c2[,w2]; ..." — value optional, ignored')
    args = ap.parse_args()
    items = parse_items(args.items)
    costs = [int(x[0]) for x in items]
    if args.kind == "01":
        print(f"count = {count_01(costs, args.capacity)}")
    else:
        print(f"count = {count_complete(costs, args.capacity)}")


if __name__ == "__main__":
    main()
