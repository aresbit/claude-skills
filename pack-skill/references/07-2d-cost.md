# 2-D Cost Pack (two capacities)

**Setup.** Each item consumes **two** costs `Cᵢ` (from capacity V) AND `Dᵢ` (from capacity U). Choose items to maximize total value.

## State

```
F[i, v, u] = max value using items 1..i with first cost ≤ v AND second cost ≤ u
F[i, v, u] = max(F[i-1, v, u], F[i-1, v - Cᵢ, u - Dᵢ] + Wᵢ)
```

Same idea, one extra dimension.

## 1-D in items, 2-D in capacity

Compress on `i`. The two cost dimensions are independent of each other.

```python
F = [[0] * (U + 1) for _ in range(V + 1)]
for C, D, W in items:                     # for each 0/1 item
    for v in range(V, C - 1, -1):
        for u in range(U, D - 1, -1):
            if F[v - C][u - D] + W > F[v][u]:
                F[v][u] = F[v - C][u - D] + W
answer = F[V][U]
```

- Both `v` and `u` iterate **descending** for 0/1 items.
- Both iterate **ascending** for complete items.
- For bounded items, binary-split as in chapter 3.

## Hidden 2nd dimension — "at most K items" (chapter 5.3)

If the problem says "max value, weight ≤ V, **at most K items in total**", then the 2nd cost is uniformly `Dᵢ = 1` and the 2nd capacity is `U = K`. Same code path.

## Generalization — complex / fractional cost (chapter 5.4)

Two-dimensional cost is a special case of cost in a "product domain". As long as cost arithmetic supports comparison (`≤`) and addition, the same DP works. The complexity is the size of the cost lattice (here `V·U`). Use this lens when a problem has weird cost structure (e.g., cost on a 2-D grid).

## Complexity

- Time `O(N·V·U)`.
- Space `O(V·U)`.

## Worked example

```
Items: (C=2, D=1, W=3), (C=2, D=2, W=4), (C=3, D=1, W=5)
V=5, U=3

After item 1: F[2][1] = 3, F[2..5][1..3] propagates
After item 2: best is to take items 1+2 (C=4, D=3, W=7) → F[4][3] = 7
After item 3: items 1+3 (C=5, D=2, W=8) → F[5][2] = 8 (better)

answer = F[5][3] = 8
```

## When to choose 2-D pack

- Two independent budget axes (money + time, weight + volume).
- "≤ K items" constraint on top of a normal knapsack.
- Resource-allocation problems with two scarce resources.

Use `scripts/solve_2d.py` for a CLI run.
