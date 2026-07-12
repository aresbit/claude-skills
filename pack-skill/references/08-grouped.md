# Grouped Pack (mutually exclusive groups)

**Setup.** N items partitioned into K groups. **At most one item per group** may be chosen. Each item has cost `Cᵢ` and value `Wᵢ`. Maximize total value with cost ≤ V.

## State

```
F[k, v] = max value using groups 1..k with cost ≤ v
F[k, v] = max{ F[k-1, v],                                    # take nothing from group k
                F[k-1, v - Cᵢ] + Wᵢ   for each item i in group k }
```

## 1-D recurrence — three nested loops

```python
F = [0] * (V + 1)
for group in groups:                          # for each group k
    for v in range(V, -1, -1):                # v descending (each group contributes ≤ 1 item, like 0/1)
        for C, W in group.items:              # over every item in group k
            if v >= C and F[v - C] + W > F[v]:
                F[v] = F[v - C] + W
answer = F[V]
```

**Loop order is non-negotiable.** The middle loop must be `v` **descending**, and the inner loop must iterate over items **inside one iteration** of `v`. This guarantees that during the update of `F[v]`, all branches read from the same "previous-group" snapshot `F[v−Cᵢ]` and only one branch can win.

If you swap the inner two loops (items outer, v inner), you'd be running independent 0/1 pack on each item, which lets you pick multiple items per group — wrong.

## Why descending v

Within one group, picking item `i` reduces `v` by `Cᵢ`. We must not let another item in the same group also use that reduced state, because that would mean picking two items from one group. Descending order ensures `F[v − Cᵢ]` is from the **previous-group** state, not the current group.

## Per-group optimization (chapter 2.3 trick reused)

Inside a group, if two items satisfy `Cᵢ ≤ Cⱼ` and `Wᵢ ≥ Wⱼ`, item j is strictly worse — remove it from the group before the DP.

## Complexity

- Time `O(V · Σ |groupₖ|) = O(V · N)`.
- Space `O(V)`.

## Worked example

```
Group 1: (C=2, W=3), (C=4, W=5)
Group 2: (C=3, W=4), (C=5, W=7)
V = 7

After group 1: F = [0, 0, 3, 3, 5, 5, 5, 5]
After group 2 (combine each item):
  candidate 1 (don't pick): F = unchanged
  candidate 2 (pick C=3,W=4): F[3]=max(3, F[0]+4)=4, F[4]=max(5, F[1]+4)=5, ..., F[7]=max(5, F[4]+4)=9
  candidate 3 (pick C=5,W=7): F[5]=max(5, F[0]+7)=7, F[6]=max(5, F[1]+7)=7, F[7]=max(9, F[2]+7)=10

Final F[7] = 10  (item from group 1 with C=2,W=3 + item from group 2 with C=5,W=7 = 10) ✓
```

## When to choose grouped pack

- "Items partitioned into K categories, at most one per category."
- Course scheduling where each time slot offers exclusive options.
- Multi-choice knapsack.
- Pre-step for dependency pack (chapter 7 reduces a main+accessories tree to a group).

Use `scripts/solve_grouped.py` for a CLI run.
