# Question-form Variations

Once the variant is chosen, the **question** the problem asks can still vary. This file maps each question form to the modification of the master DP.

## 1. Output one optimal selection (chapter 9.1)

Use a 2-D `F` table and an auxiliary `G[i][v] ∈ {0, 1}`:

- `G[i][v] = 0` ⇒ optimum at `(i,v)` came from `F[i-1][v]` (didn't take item i).
- `G[i][v] = 1` ⇒ optimum came from `F[i-1][v - Cᵢ] + Wᵢ` (took item i).

Backtrace from `(N, V)`:

```python
def output_solution_01(items, V):
    N = len(items)
    F = [[0] * (V + 1) for _ in range(N + 1)]
    G = [[0] * (V + 1) for _ in range(N + 1)]
    for i in range(1, N + 1):
        C, W = items[i - 1]
        for v in range(V + 1):
            F[i][v] = F[i-1][v]
            G[i][v] = 0
            if v >= C and F[i-1][v - C] + W > F[i][v]:
                F[i][v] = F[i-1][v - C] + W
                G[i][v] = 1
    chosen, v = [], V
    for i in range(N, 0, -1):
        if G[i][v] == 1:
            chosen.append(i - 1)
            v -= items[i - 1][0]
    chosen.reverse()
    return F[N][V], chosen
```

To save memory, you can re-derive `G` on the fly from `F` without storing it: at each step check whether `F[i][v] == F[i-1][v]` (skipped) or matches the "took" branch.

## 2. Lex-smallest optimal selection (chapter 9.2)

"Lex-smallest" means among all optimal selections, return the one whose chosen-item-index list is lexicographically smallest.

**Trick:** renumber items as `x ← N + 1 − x` before running the DP. Then standard backtrace from `(N, V)` produces the lex-smallest plan in the original numbering.

The intuition: we want to **prefer** including item 1 when ties happen. By reversing the order, item N becomes the first decision (and the DP naturally prefers including it on ties), which corresponds to preferring item 1 in the original numbering.

When extracting, if both "took" and "didn't take" branches achieve the optimum at `(i, v)`, prefer the "took" branch. After collection, map indices back via `i ↦ N + 1 − i`.

## 3. Count total feasible schemes (chapter 9.3)

Replace `max` with `+` and use `F[0] = 1` (one way to make the empty pack), `F[v ≠ 0] = 0`.

```python
# Count of subsets summing to exactly each capacity v (01 case)
F = [0] * (V + 1)
F[0] = 1
for C, _ in items:
    for v in range(V, C - 1, -1):
        F[v] += F[v - C]
# answer for "exactly V": F[V]
# answer for "≤ V": sum(F)
```

For complete pack: change inner loop to ascending. For multiple pack: binary-split first.

This is exactly the **coin change — number of ways** problem (complete pack version).

## 4. Count optimal schemes (chapter 9.4)

Two arrays in parallel: `F[i][v]` = best value, `G[i][v]` = number of ways to achieve that best value.

```python
F = [[0] * (V + 1) for _ in range(N + 1)]
G = [[0] * (V + 1) for _ in range(N + 1)]
G[0][0] = 1                      # one way to do nothing
for v in range(V + 1):
    G[0][v] = 1                  # actually all "do nothing" schemes; if exact-fill, only G[0][0]=1
for i in range(1, N + 1):
    C, W = items[i - 1]
    for v in range(V + 1):
        skip_v = F[i-1][v]
        take_v = F[i-1][v - C] + W if v >= C else -1
        if skip_v >= take_v:
            F[i][v] = skip_v
            G[i][v] = G[i-1][v]
        if take_v >= skip_v and v >= C:
            if take_v > skip_v:
                G[i][v] = 0
            F[i][v] = take_v
            G[i][v] += G[i-1][v - C]
answer_value = F[N][V]
answer_count = G[N][V]
```

Symmetric structure: whenever a transition ties for the optimum, **sum** the counts of the contributing predecessors; whenever one branch strictly wins, copy its count.

## 5. Kth-best total value (chapter 9.5)

Each state holds a **sorted list of the top-K values** instead of a single best value. The transition merges two sorted lists and keeps only the first K.

```python
def kth_best_01(items, V, K):
    NEG = float('-inf')
    F = [[NEG] * K for _ in range(V + 1)]
    for v in range(V + 1):
        F[v][0] = 0                              # one "do nothing" plan, value 0
    for C, W in items:
        new_F = [row[:] for row in F]
        for v in range(V, C - 1, -1):
            a = F[v]                              # don't take: list at v
            b = [F[v - C][k] + W for k in range(K) if F[v - C][k] != NEG]
            # merge a and b descending, keep top K
            merged = []
            i = j = 0
            while len(merged) < K and (i < len(a) or j < len(b)):
                if i < len(a) and (j >= len(b) or a[i] >= b[j]):
                    merged.append(a[i]); i += 1
                else:
                    merged.append(b[j]); j += 1
            while len(merged) < K:
                merged.append(NEG)
            new_F[v] = merged
        F = new_F
    return F[V]                                   # top-K values for full capacity
```

**Distinct-strategy vs distinct-value:** if the problem says "two solutions with different items but the same total value count as the same Kth-best", deduplicate the merged list before truncating to K.

Complexity: `O(VNK)`.

## 6. Min-value / count items / etc.

- **Min total value with cost ≥ T:** swap roles of cost and value (treat value as cost, cost as value), or use `min` and init with `+∞` plus appropriate exact-fill semantics.
- **Min items used (with sum = T):** complete pack, `Wᵢ = 1`, `min`, exact-fill init.
- **Range query — for each v in [0..V], best value:** the answer is just `F[v]` for each `v` directly.

## Scripts

| Question form | Script |
|---|---|
| Output one optimal selection | `scripts/output_solution.py` |
| Count feasible schemes | `scripts/count_schemes.py` |
| Count optimal schemes | `scripts/count_optimal.py` |
| Kth best | `scripts/kth_optimal.py` |
