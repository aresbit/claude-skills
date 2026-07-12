#!/usr/bin/env python3
"""Output one optimal item selection for a 0/1 knapsack.

Usage:
    output_solution.py --capacity V --items "c,w; c,w; ..." [--lex-smallest]

With --lex-smallest, returns the lexicographically smallest selection
(among optima) as a 1-indexed item list.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cli import parse_items


def solve(items, V):
    N = len(items)
    F = [[0.0] * (V + 1) for _ in range(N + 1)]
    for i in range(1, N + 1):
        C, W = items[i - 1]
        for v in range(V + 1):
            F[i][v] = F[i - 1][v]
            if v >= C and F[i - 1][v - C] + W > F[i][v]:
                F[i][v] = F[i - 1][v - C] + W
    chosen = []
    v = V
    for i in range(N, 0, -1):
        C, W = items[i - 1]
        if v >= C and F[i][v] == F[i - 1][v - C] + W and (F[i][v] != F[i - 1][v] or True):
            # prefer "took" if both branches tie? For plain output, either is fine;
            # we just need consistency with the F table.
            if F[i][v] != F[i - 1][v]:
                chosen.append(i)
                v -= C
            # if F[i][v] == F[i-1][v], we prefer "skip" to match lex-smallest later
    chosen.reverse()
    return F[N][V], chosen


def solve_lex_smallest(items, V):
    """Renumber x -> N+1-x, then prefer 'took' branch on ties to get lex-smallest."""
    N = len(items)
    rev = list(reversed(items))
    F = [[0.0] * (V + 1) for _ in range(N + 1)]
    for i in range(1, N + 1):
        C, W = rev[i - 1]
        for v in range(V + 1):
            F[i][v] = F[i - 1][v]
            if v >= C and F[i - 1][v - C] + W > F[i][v]:
                F[i][v] = F[i - 1][v - C] + W
    chosen_rev = []
    v = V
    for i in range(N, 0, -1):
        C, W = rev[i - 1]
        took = v >= C and F[i - 1][v - C] + W == F[i][v]
        skip = F[i - 1][v] == F[i][v]
        if took and (not skip):
            chosen_rev.append(i)
            v -= C
        elif took and skip:
            # tie: prefer 'took' so that, in original numbering, smaller index gets in
            chosen_rev.append(i)
            v -= C
        # else: skip
    # map back: i in reversed numbering corresponds to N+1-i in original (1-indexed)
    chosen = sorted(N + 1 - i for i in chosen_rev)
    return F[N][V], chosen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capacity", "-V", type=int, required=True)
    ap.add_argument("--items", required=True)
    ap.add_argument("--lex-smallest", action="store_true")
    args = ap.parse_args()
    items = parse_items(args.items)
    items = [(int(c), float(w)) for c, w in items]
    if args.lex_smallest:
        val, chosen = solve_lex_smallest(items, args.capacity)
    else:
        val, chosen = solve(items, args.capacity)
    print(f"max_value = {val}")
    print(f"chosen_items (1-indexed) = {chosen}")


if __name__ == "__main__":
    main()
