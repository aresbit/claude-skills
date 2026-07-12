# Complete Pack (unbounded knapsack)

**Setup.** N item **types**, knapsack capacity V. Type i has cost `Cᵢ` and value `Wᵢ`; **unlimited copies** of each type are available.

## State

```
F[i, v] = max value using item types 1..i with cost ≤ v
F[i, v] = max(F[i-1, v], F[i, v - Cᵢ] + Wᵢ)
```

Note the second branch is `F[i, ...]` (same row), not `F[i-1, ...]` — adding one more copy of type i. This is exactly what makes it unbounded.

## 1-D recurrence — ascending v

```python
def complete_pack(F, C, W):
    for v in range(C, len(F)):
        if F[v - C] + W > F[v]:
            F[v] = F[v - C] + W

F = [0] * (V + 1)
for C, W in items:
    complete_pack(F, C, W)
answer = F[V]
```

Ascending order is mandatory. Reading `F[v − C]` finds the value **after** type i has potentially already been added at smaller v, which is what allows multiple copies to compound.

## Two pre-processing optimizations (chapter 2.3)

These cut item count without changing the answer:

1. **Drop strictly worse items.** If two types satisfy `Cᵢ ≤ Cⱼ` AND `Wᵢ ≥ Wⱼ`, type j is dominated — drop it. Adversarial inputs may not have any such pairs, so this is not a worst-case improvement, but it is cheap and helps on random data.

2. **Drop overweight items.** Any type with `Cᵢ > V` can be removed immediately. Then among items of equal cost, keep only the one with maximum value (counting-sort style, `O(V + N)`).

## Reduction to 01 pack — binary splitting (chapter 2.4)

If you only have a 0/1 pack engine, you can simulate unbounded by splitting type i into items of cost `Cᵢ·2ᵏ`, value `Wᵢ·2ᵏ` for `k = 0, 1, 2, ...` while `Cᵢ·2ᵏ ≤ V`. This gives `O(log(V/Cᵢ))` items per type — the same trick that makes multiple pack `O(VN log M)`. But the direct ascending-`v` loop is `O(VN)`, which is strictly better.

## Initialization

Same rules as 01 pack: `F[0..V] = 0` for "≤ V", or `F[0]=0, F[1..V]=-∞` for "exactly V".

## Complexity

- Time `O(NV)`.
- Space `O(V)`.

## Worked example — coin change min coins (each denom unlimited)

```
Denominations [1, 3, 4], target = 6.  Treat as Cᵢ = denom, Wᵢ = 1, minimize sum.

F = [0, INF, INF, INF, INF, INF, INF]  (exact fill)
After C=1: F = [0, 1, 2, 3, 4, 5, 6]
After C=3: F = [0, 1, 2, 1, 2, 3, 2]
After C=4: F = [0, 1, 2, 1, 1, 2, 2]

answer = F[6] = 2  (one 3 + one 3, or two 3s, total 2 coins). ✓
```

## When to choose complete pack

- "Each item available in unlimited supply."
- Coin change (min coins / count ways).
- Cutting rod.
- Currency / change-making problems.
- Integer compositions with given parts.

Use `scripts/solve_complete.py` for a quick CLI run, or import `complete_pack` from `scripts/pack_primitives.py`.
