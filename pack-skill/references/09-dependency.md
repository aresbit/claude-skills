# Dependency Pack (主件 + 附件, tree-shaped)

**Setup.** Each item is either a **main** (主件) item or an **accessory** (附件) of some main item. Choosing an accessory requires choosing its main. Simplest form: each accessory belongs to exactly one main, no nesting. General form: a **forest** where each non-root node has exactly one parent.

This is the structure of NOIP 2006 金明的预算方案.

## Simplified problem — main + accessories, no nesting

For each main item `k`, let its accessory set be `Aₖ`. The naive policy space for one main is `2^|Aₖ| + 1` (don't pick main; pick main and any subset of `Aₖ`) — exponential.

### Key reduction: convert each main + accessory set into a grouped pack item

For main item `k` with cost `Cₖ`, value `Wₖ`, and accessory set `Aₖ`:

1. Run **01 pack over `Aₖ`** with capacity `V − Cₖ`. This produces an array `Fₖ[0..V − Cₖ]` where `Fₖ[t]` = max accessory value using accessories with total cost ≤ `t`.
2. Build a **group of `V − Cₖ + 1` items**, where the t-th item in the group has cost `Cₖ + t` and value `Wₖ + Fₖ[t]`. These items are mutually exclusive — they're alternative ways to "take main k plus some accessories".
3. Plus one extra option "don't take main k at all" — implicit by not picking anything from this group.

Then run **grouped pack** (chapter 6) over all the resulting groups.

```python
def solve_dependency_flat(V, mains):
    # mains: list of (Ck, Wk, accessories) where accessories = [(C, W), ...]
    groups = []
    for Ck, Wk, accessories in mains:
        if Ck > V:
            continue
        # 01 pack over accessories, capacity V - Ck
        Fk = [0] * (V - Ck + 1)
        for Ca, Wa in accessories:
            for t in range(len(Fk) - 1, Ca - 1, -1):
                if Fk[t - Ca] + Wa > Fk[t]:
                    Fk[t] = Fk[t - Ca] + Wa
        group = [(Ck + t, Wk + Fk[t]) for t in range(len(Fk))]
        groups.append(group)
    return grouped_pack(V, groups)
```

### Why this works (chapter 7 insight)

The exponential blow-up "which subset of accessories?" collapses because we only care about the **cost-vs-value frontier** of accessory subsets, not which subset specifically. The 01 pack on the accessory set computes that frontier in `O(|Aₖ| · V)`. Then we slot the frontier into the grouped-pack engine, which automatically handles the "pick one configuration of (main + subset of accessories) OR pick none" choice.

## General case — tree DP with 泛化物品

When accessories can themselves have sub-accessories (the dependency structure is a forest), do a post-order tree DP. Each subtree corresponds to a **generalized item** (chapter 8): a function `h: [0..V] → max value of that subtree given capacity v allotted to it`.

For a node `u` with children `c₁, c₂, ...`, the generalized item of the subtree rooted at u is computed by:

1. Initialize `h_u` so that `h_u(v) = -∞` for `v < C_u` and `h_u(v) = W_u` for `v ≥ C_u` (must include u itself).
2. For each child `cⱼ`, compute `h_{cⱼ}` recursively. Sum it into `h_u` as a generalized-item sum (see chapter 8): `h_u(v) ← max{ h_u(k) + h_{cⱼ}(v − k) : 0 ≤ k ≤ v }`.
3. **Crucially**, before summing in any child, we must guarantee `u` itself was chosen — so the "child not chosen" branch in `h_{cⱼ}` should map to value 0 at cost 0 (cleanly OR'd into the child's generalized item). This is automatic if `h_{cⱼ}(0) = 0` after computing it for the subtree.

Then the answer is `max(h_root(v) for v in [0..V])`. For a forest, take the generalized-item sum across all roots.

```python
def dependency_tree(V, items, parent):
    # items[i] = (C, W); parent[i] = index of parent main or -1 if root
    children = {i: [] for i in range(len(items))}
    for i, p in enumerate(parent):
        if p >= 0:
            children[p].append(i)

    NEG = float('-inf')

    def subtree(u):
        Cu, Wu = items[u]
        h = [NEG] * (V + 1)
        if Cu <= V:
            for v in range(Cu, V + 1):
                h[v] = Wu
        for c in children[u]:
            hc = subtree(c)                       # subtree generalized item
            hc[0] = max(hc[0], 0)                  # "don't pick child" branch
            new_h = [NEG] * (V + 1)
            for v in range(V + 1):
                if h[v] == NEG:
                    continue
                for k in range(V - v + 1):
                    if hc[k] != NEG:
                        cand = h[v] + hc[k]
                        if cand > new_h[v + k]:
                            new_h[v + k] = cand
            h = new_h
        return h

    answer = 0
    for u, p in enumerate(parent):
        if p < 0:
            hu = subtree(u)
            hu[0] = max(hu[0], 0)
            answer = max(answer, max(hu))
    return answer
```

## NOIP 2006 金明的预算方案 — concrete pattern

In that problem each main has **at most 2 accessories**, so the simplified form (no nesting) applies. The cleanest writeup explicitly enumerates the 4 cases per main: (none), (main only), (main + acc1), (main + acc2), (main + both) — which is exactly the grouped pack of size 5 per main.

## Complexity

- Simplified case: `O(V · N)` after the per-main 01 packs.
- General tree: `O(V² · N)` (the generalized-item sum dominates).

## When to choose dependency pack

- "Item i can only be chosen if item j is chosen."
- 主件 / 附件 problems.
- Tree DP where each subtree's contribution depends on a budget.
- Project / task dependency problems with a global budget.

Use `scripts/solve_dependency.py` for a CLI run.
