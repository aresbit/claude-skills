# State design, initialization, and 1-D compression

These three decisions are shared by every variant. Get them right once and the rest is mechanical.

## 1. The master 2-D state

```
F[i, v] = best aggregate achievable using only items 1..i with cost ≤ v (or = v if "fill exactly")
```

Every variant differs only in **what set of policies for item i** is admissible in the transition:

```
F[i, v] = combine{ F[i-1, v - k·Cᵢ] + value(k) : k is a legal copy count for item i }
```

- 01 pack → `k ∈ {0, 1}`
- complete pack → `k ∈ {0, 1, 2, ...}`
- multiple pack → `k ∈ {0, 1, ..., Mᵢ}`
- grouped pack → `k` selects which item-within-group (or none)
- dependency pack → `k` selects an "accessory subset" pre-computed as a generalized item

## 2. Initialization — exact fill vs ≤ capacity

This is the most common silent bug.

| Question | Init |
|---|---|
| "Max value with total cost **at most** V" | `F[0..V] = 0` |
| "Max value with total cost **exactly** V" | `F[0] = 0`, `F[1..V] = -∞` |
| "Min cost to..." | swap `+∞` for `-∞`; replace `max` with `min` |
| "Count schemes" (any sum) | `F[0] = 1`, `F[1..V] = 0` |

Why this works: `F[v]` is the optimal value of the "legal start state" of an empty knapsack with capacity `v`. If we require exact fill, the only legal empty state is `v=0`; every other `v>0` is illegal until something fills it, hence `-∞`. If we don't, `v=0` with "take nothing, value 0" is legal for every capacity, hence `0` everywhere.

## 3. Space compression — `F[i,v]` → `F[v]`

The 2-D recurrence only ever reads row `i−1`. We can drop the `i` index and reuse one 1-D array if we choose the right `v` direction.

| Item type | `v` direction | Why |
|---|---|---|
| 0/1 | **descending**: `v` from V down to `Cᵢ` | When updating `F[v]` we need `F[v − Cᵢ]` from the **old** (i.e., i−1) row. Descending order means by the time we touch `v − Cᵢ`, it has not yet been written this iteration. |
| Unbounded | **ascending**: `v` from `Cᵢ` up to V | We want `F[v − Cᵢ]` to be the **new** value (already including item i) so further copies can stack. Ascending order propagates this. |
| Bounded | binary-split into 0/1 sub-items | Then use descending. |

Memorize: **descending = no reuse, ascending = unlimited reuse**.

## 4. Reusable 1-D primitives

These three procedures encapsulate the loop direction so callers never get it wrong. They are defined in `scripts/pack_primitives.py`.

```python
def zero_one_pack(F, C, W):
    # F is a list of length V+1, modified in place.
    for v in range(len(F) - 1, C - 1, -1):
        if F[v - C] + W > F[v]:
            F[v] = F[v - C] + W

def complete_pack(F, C, W):
    for v in range(C, len(F)):
        if F[v - C] + W > F[v]:
            F[v] = F[v - C] + W

def multiple_pack(F, C, W, M):
    # If M copies could already overflow capacity, treat as unbounded.
    if C * M >= len(F) - 1:
        complete_pack(F, C, W)
        return
    # Binary split: 1, 2, 4, ..., 2^(k-1), M - 2^k + 1
    k = 1
    while k < M:
        zero_one_pack(F, k * C, k * W)
        M -= k
        k *= 2
    if M > 0:
        zero_one_pack(F, M * C, M * W)
```

## 5. The constant-factor optimization (chapter 1.5)

For 01 pack, the inner loop's lower bound can be raised to `max(Cᵢ, V − Σⱼ≥ᵢ Wⱼ)`. Below that, the answer cannot involve item i because there is not enough remaining weight to be filled by future items. Apply only when the suffix sum is cheap to maintain. Helpful for tight CPU loops; harmless to skip.

## 6. Sanity checklist before running

- [ ] Is `F` initialized correctly for the exact / ≤ semantics?
- [ ] For each item, did I call the procedure that matches its copy count?
- [ ] Is the **outer loop** over items, and the **inner loop** over `v`?
  - Exception: **grouped pack** has three nested loops, see `08-grouped.md`.
- [ ] Did I read off the final answer from the right cell? (`F[V]` for exact, `max(F[0..V])` for ≤ V — these coincide unless using exact-fill init.)
- [ ] Did I brute-force a tiny instance (N ≤ 15) and diff? `pack_primitives.py` has `brute_max_01`, `brute_max_complete`, `brute_max_multiple`.
