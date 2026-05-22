# 01 Pack (0/1 knapsack)

**Setup.** N items, knapsack capacity V. Item i has cost `Cᵢ` and value `Wᵢ`. Each item is taken 0 or 1 times. Maximize total value.

## State

```
F[i, v] = max value using items 1..i with cost ≤ v
F[i, v] = max(F[i-1, v], F[i-1, v - Cᵢ] + Wᵢ)
```

The two arguments to `max` correspond to the only two policies for item i: skip it (left), take it (right).

## 1-D recurrence — descending v

```python
def zero_one_pack(F, C, W):
    for v in range(len(F) - 1, C - 1, -1):
        if F[v - C] + W > F[v]:
            F[v] = F[v - C] + W

F = [0] * (V + 1)         # init: "cost ≤ V", value 0 is the empty plan
for C, W in items:
    zero_one_pack(F, C, W)
answer = F[V]
```

Descending order is mandatory. If you iterate ascending, you'd read `F[v − Cᵢ]` after it had already been updated this same iteration, meaning the item could be added twice — that is the complete-pack recurrence, not 0/1.

## Initialization

| Question | Init |
|---|---|
| cost ≤ V, max value | `F = [0] * (V+1)` |
| cost **exactly** V, max value | `F = [0] + [-INF] * V`, then read `F[V]` (`-INF` ⇒ infeasible) |
| subset-sum existence (cost = T) | bool array `F = [True] + [False]*T`; replace `+ W` by `or True` |
| count subsets summing to T | int array `F = [1] + [0]*T`; transition `F[v] += F[v-C]` |

## Constant-factor optimization (chapter 1.5)

Inner loop lower bound can be raised:

```python
suffix_value = sum(W for _, W in items)
for C, W in items:
    lo = max(C, V - suffix_value)
    for v in range(V, lo - 1, -1):
        F[v] = max(F[v], F[v - C] + W)
    suffix_value -= W
```

Below `V − Σⱼ≥ᵢ Wⱼ`, even taking everything remaining cannot fill enough, so item i cannot help fix `F[v]`. Apply only when constant factor matters.

## Complexity

- Time `O(NV)`.
- Space `O(V)` with the 1-D trick (`O(NV)` if you need to recover the chosen items via the 2-D `G` table).

## Worked example

```
Items: (C=2, W=3), (C=3, W=4), (C=4, W=5), (C=5, W=6); V = 8

After item 1: F = [0, 0, 3, 3, 3, 3, 3, 3, 3]
After item 2: F = [0, 0, 3, 4, 4, 7, 7, 7, 7]
After item 3: F = [0, 0, 3, 4, 5, 7, 8, 9, 9]
After item 4: F = [0, 0, 3, 4, 5, 7, 8, 9, 10]

Answer = F[8] = 10  (item 1 + item 2 + item 2? no — items are 0/1)
        Actually: item 2 (C=3,W=4) + item 4 (C=5,W=6) = 4+6 = 10. ✓
```

## When to choose 01 pack

- "Each item used at most once."
- Subset sum, partition equal subset sum, target sum.
- NOIP 采药, 装箱, 多米诺骨牌, 数字组合.

Use `scripts/solve_01.py` for a quick CLI run, or import `zero_one_pack` from `scripts/pack_primitives.py`.
