#!/usr/bin/env python3
"""Solve a dependency knapsack (NOIP 金明的预算方案 style).

Format:
    --mains "c,w / c,w | c,w ; c,w / c,w ; ..."

Each main is "C,W / acc1_C,acc1_W | acc2_C,acc2_W | ..." (the "/" separates the
main from its accessory list; accessories are |-separated).
Mains are separated by ";". An empty accessory list is allowed (no "/" needed).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pack_primitives import grouped_pack, zero_one_pack


def parse_mains(spec):
    spec = spec.strip().rstrip(";")
    mains = []
    for chunk in spec.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "/" in chunk:
            main_part, acc_part = chunk.split("/", 1)
        else:
            main_part, acc_part = chunk, ""
        c, w = main_part.split(",")
        main = (int(c.strip()), float(w.strip()))
        accessories = []
        for a in acc_part.split("|"):
            a = a.strip()
            if not a:
                continue
            ac, aw = a.split(",")
            accessories.append((int(ac.strip()), float(aw.strip())))
        mains.append((main, accessories))
    return mains


def solve(mains, V):
    groups = []
    for (Ck, Wk), accessories in mains:
        if Ck > V:
            continue
        Fk = [0.0] * (V - Ck + 1)
        for Ca, Wa in accessories:
            zero_one_pack(Fk, Ca, Wa)
        group = [(Ck + t, Wk + Fk[t]) for t in range(len(Fk))]
        groups.append(group)
    F = grouped_pack(V, groups)
    return max(F)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capacity", "-V", type=int, required=True)
    ap.add_argument("--mains", required=True)
    args = ap.parse_args()
    mains = parse_mains(args.mains)
    print(f"answer = {solve(mains, args.capacity)}")


if __name__ == "__main__":
    main()
