#!/usr/bin/env python3
"""Solve a 2-D-cost knapsack instance.

Usage:
    solve_2d.py --cap1 V --cap2 U --items "c,d,w; c,d,w; ..."
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cli import parse_items
from pack_primitives import zero_one_pack_2d


def solve(items, V, U):
    F = [[0.0] * (U + 1) for _ in range(V + 1)]
    for C, D, W in items:
        zero_one_pack_2d(F, int(C), int(D), W)
    return F[V][U]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap1", "-V", type=int, required=True)
    ap.add_argument("--cap2", "-U", type=int, required=True)
    ap.add_argument("--items", required=True)
    args = ap.parse_args()
    items = parse_items(args.items)
    items = [(int(c), int(d), float(w)) for c, d, w in items]
    print(f"answer = {solve(items, args.cap1, args.cap2)}")


if __name__ == "__main__":
    main()
