"""Reusable knapsack primitives from 崔添翼《背包问题九讲》.

The three in-place 1-D procedures (zero_one_pack, complete_pack,
multiple_pack) are designed to be composed:

    F = [0] * (V + 1)
    for item in items:
        match item.kind:
            "01"       -> zero_one_pack(F, item.C, item.W)
            "complete" -> complete_pack(F, item.C, item.W)
            "multiple" -> multiple_pack(F, item.C, item.W, item.M)

After the loop, F[v] = optimal value of "cost <= v" with all items so far.
For exact-fill semantics, initialize F = [0] + [-INF] * V instead of zeros.

Brute-force checkers are bundled so callers can verify any DP on small N.
"""

from __future__ import annotations

from itertools import product
from typing import Iterable, List, Sequence, Tuple

INF = float("inf")
NEG_INF = float("-inf")


# ---------------------------------------------------------------------------
# Core 1-D primitives
# ---------------------------------------------------------------------------

def zero_one_pack(F: List[float], C: int, W: float) -> None:
    """Add one 0/1 item (cost C, value W) to F in place."""
    if C < 0:
        raise ValueError("cost must be non-negative")
    V = len(F) - 1
    for v in range(V, C - 1, -1):
        cand = F[v - C] + W
        if cand > F[v]:
            F[v] = cand


def complete_pack(F: List[float], C: int, W: float) -> None:
    """Add one unbounded item (cost C, value W) to F in place."""
    if C <= 0:
        raise ValueError("complete-pack cost must be positive (else infinite loop)")
    V = len(F) - 1
    for v in range(C, V + 1):
        cand = F[v - C] + W
        if cand > F[v]:
            F[v] = cand


def multiple_pack(F: List[float], C: int, W: float, M: int) -> None:
    """Add one bounded item (cost C, value W, at most M copies) to F in place.

    Uses binary splitting: 1, 2, 4, ..., 2^(k-1), M - 2^k + 1.
    Degenerates to complete_pack when M copies cannot fit anyway.
    """
    if M <= 0 or C < 0:
        return
    V = len(F) - 1
    if C == 0:
        # zero-cost item: just take all M copies for free if W > 0
        if W > 0:
            for v in range(V + 1):
                F[v] += M * W
        return
    if C * M >= V:
        complete_pack(F, C, W)
        return
    k = 1
    while k < M:
        zero_one_pack(F, k * C, k * W)
        M -= k
        k *= 2
    if M > 0:
        zero_one_pack(F, M * C, M * W)


# ---------------------------------------------------------------------------
# Generalized-item sum (chapter 8)
# ---------------------------------------------------------------------------

def gsum(h: Sequence[float], l: Sequence[float]) -> List[float]:
    """Generalized-item sum: f(v) = max(h(k) + l(v-k)) for 0<=k<=v.

    Both inputs must have the same length V+1. Uses NEG_INF to mark
    infeasible inputs. O(V^2) per call.
    """
    if len(h) != len(l):
        raise ValueError("generalized items must share the same V")
    V = len(h) - 1
    f = [NEG_INF] * (V + 1)
    for v in range(V + 1):
        for k in range(v + 1):
            if h[k] == NEG_INF or l[v - k] == NEG_INF:
                continue
            cand = h[k] + l[v - k]
            if cand > f[v]:
                f[v] = cand
    return f


# ---------------------------------------------------------------------------
# Brute force checkers (use ONLY for small N to verify DP correctness)
# ---------------------------------------------------------------------------

def brute_max_01(items: Sequence[Tuple[int, float]], V: int) -> float:
    """Enumerate 2^N subsets of 0/1 items. Returns max value with cost<=V."""
    n = len(items)
    if n > 25:
        raise ValueError("brute_max_01: N too large; use the DP instead")
    best = 0.0
    for mask in range(1 << n):
        total_c = total_w = 0.0
        for i, (c, w) in enumerate(items):
            if mask >> i & 1:
                total_c += c
                total_w += w
        if total_c <= V and total_w > best:
            best = total_w
    return best


def brute_max_complete(items: Sequence[Tuple[int, float]], V: int) -> float:
    """Enumerate unbounded multiplicities up to V/C each. Slow."""
    n = len(items)
    bounds = [V // c if c > 0 else 0 for c, _ in items]
    best = 0.0
    for ks in product(*[range(b + 1) for b in bounds]):
        cost = sum(k * c for k, (c, _) in zip(ks, items))
        if cost > V:
            continue
        val = sum(k * w for k, (_, w) in zip(ks, items))
        if val > best:
            best = val
    return best


def brute_max_multiple(items: Sequence[Tuple[int, float, int]], V: int) -> float:
    """items: (C, W, M) triples."""
    bounds = [min(M, V // C if C > 0 else 0) for C, _, M in items]
    best = 0.0
    for ks in product(*[range(b + 1) for b in bounds]):
        cost = sum(k * c for k, (c, _, _) in zip(ks, items))
        if cost > V:
            continue
        val = sum(k * w for k, (_, w, _) in zip(ks, items))
        if val > best:
            best = val
    return best


# ---------------------------------------------------------------------------
# 2-D cost variant (chapter 5)
# ---------------------------------------------------------------------------

def zero_one_pack_2d(F: List[List[float]], C: int, D: int, W: float) -> None:
    V = len(F) - 1
    U = len(F[0]) - 1
    for v in range(V, C - 1, -1):
        row_src = F[v - C]
        row_dst = F[v]
        for u in range(U, D - 1, -1):
            cand = row_src[u - D] + W
            if cand > row_dst[u]:
                row_dst[u] = cand


def complete_pack_2d(F: List[List[float]], C: int, D: int, W: float) -> None:
    V = len(F) - 1
    U = len(F[0]) - 1
    for v in range(C, V + 1):
        row_src = F[v - C]
        row_dst = F[v]
        for u in range(D, U + 1):
            cand = row_src[u - D] + W
            if cand > row_dst[u]:
                row_dst[u] = cand


# ---------------------------------------------------------------------------
# Grouped pack (chapter 6)
# ---------------------------------------------------------------------------

def grouped_pack(V: int, groups: Iterable[Sequence[Tuple[int, float]]]) -> List[float]:
    """Each group is a list of (C, W). Picks at most one item per group.

    Returns the final 1-D F of length V+1.
    """
    F = [0.0] * (V + 1)
    for group in groups:
        for v in range(V, -1, -1):
            best = F[v]
            for C, W in group:
                if v >= C and F[v - C] + W > best:
                    best = F[v - C] + W
            F[v] = best
    return F


if __name__ == "__main__":
    # tiny self-test
    items = [(2, 3.0), (3, 4.0), (4, 5.0), (5, 6.0)]
    F = [0.0] * 9
    for C, W in items:
        zero_one_pack(F, C, W)
    assert F[8] == 10.0, F
    assert F[8] == brute_max_01(items, 8)

    coins = [(1, 1.0), (3, 1.0), (4, 1.0)]
    F = [0.0] + [NEG_INF] * 6  # exact-fill, min coins -> negate trick
    # we want MIN; do it directly:
    G = [INF] * 7
    G[0] = 0
    for C, _ in coins:
        for v in range(C, 7):
            if G[v - C] + 1 < G[v]:
                G[v] = G[v - C] + 1
    assert G[6] == 2.0, G

    # multiple pack sanity
    items_m = [(1, 1.0, 5), (2, 3.0, 3)]
    F = [0.0] * 7
    for C, W, M in items_m:
        multiple_pack(F, C, W, M)
    assert F[6] == brute_max_multiple(items_m, 6), (F[6], brute_max_multiple(items_m, 6))

    print("pack_primitives self-test passed.")
