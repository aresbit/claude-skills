# Recognizing the variant

Run this decision tree on the problem before writing any code.

## Step 1 — Is it a knapsack at all?

A problem belongs to this family iff **all four** hold:

- There is a finite **collection of items** (or item types).
- Each chosen item consumes some **non-negative cost(s)** from a bounded **capacity**.
- Each chosen item contributes a **value** to an aggregate (sum, min, max, count).
- Choices are **decoupled by item index** — you can decide item `i`'s policy assuming item `1..i−1` policies are already settled.

If "decoupled by index" fails (e.g., adjacency matters, ordering matters, geometry matters), it is probably **not** a knapsack — try a different DP family.

## Step 2 — How many copies of each item?

| Per-item legal copy count | Variant | Reference |
|---|---|---|
| Exactly 0 or 1 | **01 pack** | `03-zero-one.md` |
| 0..∞ | **complete pack** | `04-complete.md` |
| 0..Mᵢ (finite, possibly > 1) | **multiple pack** | `05-multiple.md` |
| Some items 0/1, others ∞, others ≤Mᵢ | **mixed pack** | `06-mixed.md` |

Shortcut: if `Mᵢ · Cᵢ ≥ V` for some item, treat that item as if it were a complete-pack item.

## Step 3 — How many cost dimensions?

| # of cost dimensions per item | Variant |
|---|---|
| 1 (weight, capacity) | base case — already handled by step 2 |
| 2 (e.g., weight AND volume, money AND time) | **2-D cost pack** — `07-2d-cost.md` |
| ≥3 | same idea, add one more state dim per cost |

A hidden 2nd dimension: "at most U items in total" → treat each item as costing 1 in a 2nd dimension capped at U.

## Step 4 — Are items related to each other?

| Relationship | Variant | Reference |
|---|---|---|
| Independent | base | step 2 / step 3 |
| Items partitioned into K groups, at most one per group | **grouped pack** | `08-grouped.md` |
| Item i requires item j be chosen first (forest of "main + accessories") | **dependency pack** | `09-dependency.md` |
| General tree DP on items | tree DP using 泛化物品 sum | `09-dependency.md`, `10-generalized.md` |

## Step 5 — What does the question ask?

| Question form | Adjustment |
|---|---|
| Max total value with cost ≤ V | base — return `F[V]` |
| Max value, **must fill exactly** | init `F[0]=0, F[1..V]=-∞`; return `F[V]` (`-∞` ⇒ infeasible) |
| Min total value | replace `max` with `min`; init with `+∞` |
| Max number of items | set every `Wᵢ = 1` |
| Min cost to reach value ≥ T | swap roles of cost and value |
| **Count feasible schemes** | replace `max` with `+`; init `F[0]=1` (everything else 0) — see `11-variations.md` |
| **Count optimal schemes** | dual array `G[i,v]`; propagate counts only along optimal transitions — see `11-variations.md` |
| **Output the chosen items** | trace back from `F[N][V]`; or store `G[i,v]` = which branch won — see `11-variations.md` |
| **Lex-smallest plan** | renumber items `x ← N+1−x` first — see `11-variations.md` |
| **Kth best total value** | each state holds a sorted size-K list; merge in transitions, cost `O(VNK)` — see `11-variations.md` |

## Step 6 — Disguised knapsack patterns

These are the most common non-obvious cases. If the problem looks like one of these, treat it as the listed variant.

| Problem statement | Real variant | Notes |
|---|---|---|
| Subset sum / "can we pick a subset summing to T" | 01 pack with `V = T`, "fill exactly" init | `F[T]` becomes 0 if reachable, `-∞` otherwise. Use a boolean array directly for speed. |
| Partition into two equal-sum subsets | subset sum with `T = S/2` | Reject if `S` is odd. |
| Coin change — minimum coins | complete pack, `Wᵢ = 1`, `min`, "fill exactly" | Each coin denomination = one item, `Cᵢ` = denom value. |
| Coin change — number of ways | complete pack, replace `max` with `+`, init `F[0]=1` | Outer loop coins, inner loop amount ascending. |
| Cutting rod | complete pack | `Cᵢ = length i`, `Wᵢ = price[i]`. |
| Target sum with +/- signs | subset sum | `target = (S + want)/2`; reject if odd or `|want|>S`. |
| Last stone weight II | subset sum | minimize `|S − 2·subset|`. |
| NOIP 装箱问题 | 01 pack, fill exactly | A box of size V, items with sizes; find min leftover. |
| NOIP 采药 / 背包问题 | 01 pack | Direct. |
| NOIP 金明的预算方案 | dependency pack with ≤2 accessories | See `09-dependency.md`. |
| Multiple cost budgets (money + time) | 2-D cost pack | See `07-2d-cost.md`. |
| "Choose ≤K items, max value, cap weight ≤W" | 2-D cost pack | 2nd dim is item count cap K. |

## Recognition antipatterns (NOT knapsack)

- **TSP / assignment / matching** — choices are coupled by a graph, not by an item index. Use bitmask DP / flow.
- **Longest increasing subsequence** — state is "last picked value", not "remaining capacity". Use sequence DP.
- **Interval scheduling weighted** — close cousin, but state is "last interval index sorted by end time", not capacity. Use interval DP.
- **Stock buy/sell with k transactions** — looks knapsack-ish but the "items" are time steps and the constraint is causal ordering. Use sequence DP with a `holding / not holding` state.

If unsure, write down: "What is the state? What is the transition for item i? Is the only thing that connects past and future the **residual capacity**?" If yes, knapsack.
