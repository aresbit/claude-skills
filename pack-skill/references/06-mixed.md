# Mixed Pack (01 + complete + bounded)

**Setup.** Same knapsack, but each item declares its **own** copy-count policy: some items are 0/1, some unbounded, some bounded `Mᵢ`.

## Insight

The three procedures `zero_one_pack`, `complete_pack`, `multiple_pack` are designed to be composable. They all read and write the same 1-D array `F`, and they all preserve the invariant that after the call, `F[v]` is the optimal value using only the items processed so far. So you can simply dispatch per item:

```python
F = [0] * (V + 1)
for item in items:
    kind = item.kind  # "01", "complete", or "multiple"
    if kind == "01":
        zero_one_pack(F, item.C, item.W)
    elif kind == "complete":
        complete_pack(F, item.C, item.W)
    elif kind == "multiple":
        multiple_pack(F, item.C, item.W, item.M)
answer = F[V]
```

## Complexity

- Time: sum of the per-item costs. Dominated by `O(VN)` plus `O(V Σ log Mᵢ)` from any bounded items.

## Notes

- This works because each procedure restores the "correct DP relative to all items seen so far" invariant. There is no interaction between item kinds beyond reading the shared `F`.
- The order in which items are processed does not affect the final answer (only intermediate `F` values).
- If using "exact fill" semantics, initialize once before the loop; nothing else changes.

## When to choose mixed pack

- Problem explicitly mixes "single use" and "unlimited" and "limited supply" items.
- 装箱 / 限购 / 类型不同的商品组合.
- Hidden in problems where some "items" are really groups with different supply.

Use `scripts/solve_mixed.py` for a CLI run.
