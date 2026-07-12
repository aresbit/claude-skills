# Multiple Pack (bounded knapsack)

**Setup.** N item types, knapsack capacity V. Type i has cost `Cᵢ`, value `Wᵢ`, and **at most `Mᵢ` copies** available. Maximize total value.

## State

```
F[i, v] = max{ F[i-1, v - k·Cᵢ] + k·Wᵢ : 0 ≤ k ≤ Mᵢ, k·Cᵢ ≤ v }
```

The naive evaluation is `O(V · Σ Mᵢ)`, which is fine when copy counts are small but blows up for large `Mᵢ`.

## Binary splitting — the canonical trick (chapter 3.3)

Split type i with `Mᵢ` copies into `O(log Mᵢ)` virtual 0/1 items with coefficients `1, 2, 4, ..., 2^(k-1), Mᵢ − 2ᵏ + 1` where `k = ⌊log₂(Mᵢ+1)⌋`. Any integer in `[0, Mᵢ]` is expressible as a subset sum of these coefficients, so choosing a subset of the virtual items reproduces every legal copy count.

Example: `Mᵢ = 13` → split into coefficients `1, 2, 4, 6` (because `2³=8 > 13−2³+1=6` is the remainder term).

```python
def multiple_pack(F, C, W, M):
    if C * M >= len(F) - 1:
        complete_pack(F, C, W)            # already enough copies to act unbounded
        return
    k = 1
    while k < M:
        zero_one_pack(F, k * C, k * W)
        M -= k
        k *= 2
    if M > 0:
        zero_one_pack(F, M * C, M * W)
```

## Complexity

- Time `O(V · Σ log Mᵢ)` per the pseudocode above.
- Memory `O(V)`.
- A more advanced `O(VN)` algorithm exists using a monotonic deque on each residue class mod `Cᵢ` (see chapter 3.4); use it when `Σ log Mᵢ` is too slow.

## `O(VN)` feasibility variant (chapter 3.4)

When the question is "can these items fill capacity v?" (not maximize value), there is a clean `O(VN)` algorithm. `g[i,j] = max copies of item i left after filling capacity j using items 1..i`, with `−1` meaning infeasible. Transition:

```
g[i][j]   = Mᵢ if g[i-1][j] ≥ 0
            else if there exists C such that g[i][j-Cᵢ] > 0:
                g[i-1][j-Cᵢ] >= 0 → g[i][j] = max(g[i-1][j-Cᵢ], g[i][j-Cᵢ] - 1)
```

In code:

```python
g = [[-1] * (V + 1) for _ in range(N + 1)]
g[0][0] = 0
for i in range(1, N + 1):
    Ci, Mi = items[i-1]
    for j in range(V + 1):
        g[i][j] = Mi if g[i-1][j] >= 0 else -1
    for j in range(V + 1 - Ci):
        if g[i][j] > 0:
            g[i][j + Ci] = max(g[i][j + Ci], g[i][j] - 1)
# answer: any j with g[N][j] >= 0 is reachable
```

## Worked example

```
Items: (C=1, W=1, M=5), (C=2, W=3, M=3); V = 6

Item 1 split: coefficients 1, 2, 2 (since M=5: 1, 2, then remainder 2)
  → 0/1 items (C=1,W=1), (C=2,W=2), (C=2,W=2)
Item 2 split: coefficients 1, 2 (since M=3: 1, then remainder 2)
  → 0/1 items (C=2,W=3), (C=4,W=6)

Running zero_one_pack five times yields F[6] = 9
(three of item 2: 6 cost, 9 value; or two of item 2 + two of item 1; etc.)
```

## When to choose multiple pack

- "At most M copies of each."
- 货车装载 / 多重背包模板.
- Mixed market scenarios with finite supply per SKU.

Use `scripts/solve_multiple.py` for a quick CLI run, or import `multiple_pack` from `scripts/pack_primitives.py`.
