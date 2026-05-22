"""Shared CLI helpers for pack-skill solver scripts."""

from __future__ import annotations

from typing import List, Tuple


def parse_items(spec: str) -> List[Tuple[float, ...]]:
    """Parse 'c1,w1[,m1]; c2,w2[,m2]; ...' into a list of tuples.

    Each segment is a comma-separated tuple of numbers. Whitespace is ignored.
    """
    spec = spec.strip().rstrip(";")
    out = []
    if not spec:
        return out
    for chunk in spec.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = [p.strip() for p in chunk.split(",")]
        nums = []
        for p in parts:
            if "." in p or "e" in p or "E" in p:
                nums.append(float(p))
            else:
                nums.append(int(p))
        out.append(tuple(nums))
    return out
