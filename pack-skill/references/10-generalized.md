# Generalized Items (泛化物品)

This is the unifying abstraction. Read it once and the rest of the variants look the same.

## Definition

A **generalized item** is a function `h: [0..V] → ℝ` (or extended ℝ with `-∞`). The interpretation: "if you allocate `v` units of capacity to this item, you can get value `h(v)`."

Concretely, a generalized item is just an array of length `V+1`.

Every concrete item / group / subtree corresponds to a generalized item:

| Concrete thing | Generalized item h(v) |
|---|---|
| 0/1 item (cost C, value W) | `h(C) = W`, `h(v) = 0` for `v ≠ C`. Or `h(v) = W·[v ≥ C]` if "≤ capacity" semantics. |
| Complete item (cost C, value W, unlimited) | `h(v) = (v // C) · W` for `v` divisible by C, else 0; or `h(v) = W·⌊v/C⌋`. |
| Multiple item (cost C, value W, M copies) | `h(v) = k·W` where `k = min(M, ⌊v/C⌋)` and `v − k·C` is "wasted". |
| Group | `h(v) = max(0, max_{i in group, Cᵢ ≤ v} Wᵢ)` |
| Subtree (chapter 7 general case) | computed recursively |
| Entire pack problem | `h(v) = optimal value of the whole pack with capacity v` |

## The sum operation (chapter 8.2)

Given two generalized items `h` and `l`, their **sum** `f = h ⊕ l` is:

```
f(v) = max{ h(k) + l(v − k) : 0 ≤ k ≤ v }
```

Interpretation: split capacity `v` between the two items optimally.

```python
def gsum(h, l):
    V = len(h) - 1
    NEG = float('-inf')
    f = [NEG] * (V + 1)
    for v in range(V + 1):
        for k in range(v + 1):
            if h[k] != NEG and l[v - k] != NEG:
                f[v] = max(f[v], h[k] + l[v - k])
    return f
```

- Identity: the generalized item `e(v) = 0` for all `v`.
- Associative and commutative.
- Complexity: `O(V²)` per sum.

## Why this matters

Every variant of knapsack is "sum these generalized items, then read the max over the range." The procedural shortcuts (zero_one_pack, complete_pack, ...) are optimized incremental versions of this sum for specific shapes of `h`.

- A 0/1 item has only two "interesting" inputs (`v < C` → 0, `v ≥ C` → consider `+W`), so its sum into `F` takes `O(V)` not `O(V²)`.
- A complete item has structure that lets the ascending `v` loop fold all `k=0,1,2,...` copies into `O(V)`.
- A multiple item, after binary splitting, becomes `O(log M)` 0/1 items.

When you hit a problem variant that doesn't fit any of those shortcuts (e.g., the value of an item is an arbitrary concave/convex function of how much capacity you allocate to it), you fall back to the explicit `O(V²)` `gsum` — that always works.

## When to think in generalized items

- The item's value-vs-cost relationship is non-linear (e.g., diminishing returns, tiered pricing).
- Items themselves are produced by another optimization (e.g., a subtree's best value at each allotted capacity).
- You need to reason about why the loop-direction trick is sound — it's the standard `O(V)` shortcut for a generalized-item sum with a special structure.

## Practical use: tree DP

In chapter 7's general dependency problem, each subtree at node `u` is summarized as a generalized item `h_u`. Combining children is exactly a sequence of `gsum` operations. See `09-dependency.md` for code.

## Practical use: knapsack itself

`F` at the end of the DP is `h_problem`, the generalized item representing the entire knapsack. To recover the answer:

- "Max value with cost ≤ V": `max(F[0..V])`.
- "Max value with cost exactly V": `F[V]` (`-∞` if infeasible).
- "Max value with cost in a set S": `max(F[s] for s in S)`.

The same `F` answers all these questions for free.

## No script

This file is purely conceptual; the practical primitives (`zero_one_pack`, `complete_pack`, etc.) already encode the optimized versions. Use the explicit `gsum` only when you genuinely need it.
