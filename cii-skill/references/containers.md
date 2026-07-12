# Containers — `List`, `Stack`, `Table`, `Set`, `Array`, `Seq`, `Ring`, `Bit`

All CII containers store **`void *` elements** (except `Bit`, which stores bits, and `Array`, which stores fixed-size values inline). They are not type-parametric: you cast on the way in and out. Keyed containers (`Table`, `Set`) take a client `cmp` and `hash` — pair them with `Atom` keys so equality is pointer identity.

Two recurring idioms:
- **apply/closure iteration**: `X_map(x, apply, cl)` calls `apply(elem…, cl)` for each element; `cl` threads your state through.
- **`toArray(end)`**: returns a freshly `Mem`-allocated `void *[]` of the elements, terminated by the sentinel `end` (usually `NULL`); you `FREE` it.

Headers: `headers/{list,stack,table,set,array,arrayrep,seq,ring,bit}.h`.

---

## `List` — singly-linked list (transparent)

Unusually, `List_T`'s representation is **public**: `struct T { T rest; void *first; }`. This lets you walk it directly. `NULL` is the empty list.

```c
T   List_push   (T list, void *x);     /* prepend x, return new head */
T   List_pop    (T list, void **x);    /* remove head into *x, return rest */
T   List_list   (void *x, ...);        /* build from NULL-terminated args */
T   List_append (T list, T tail);      /* destructive concat */
T   List_copy   (T list);
T   List_reverse(T list);              /* in-place reverse, returns new head */
int List_length (T list);
void List_free  (T *list);             /* free all cells (not the elements) */
void List_map   (T list, void apply(void **x, void *cl), void *cl);
void **List_toArray(T list, void *end);
```

Walk it directly: `for (T p = list; p; p = p->rest) use(p->first);`. `List_free` frees the cells, never the pointed-to data — you own element lifetimes.

## `Stack` — LIFO stack

```c
T     Stack_new (void);
int   Stack_empty(T stk);
void  Stack_push (T stk, void *x);
void *Stack_pop  (T stk);     /* checked error if empty */
void  Stack_free (T *stk);
```

Minimal, opaque counterpart to `List`. `Stack_pop` on an empty stack is a checked runtime error (`assert`).

## `Table` — hash table (key → value mapping)

```c
T    Table_new (int hint, int cmp(const void *x, const void *y),
                          unsigned hash(const void *key));
void *Table_put(T t, const void *key, void *value);   /* returns prior value or NULL */
void *Table_get(T t, const void *key);                /* value or NULL */
void *Table_remove(T t, const void *key);             /* removed value or NULL */
int   Table_length(T t);
void  Table_map (T t, void apply(const void *key, void **value, void *cl), void *cl);
void **Table_toArray(T t, void *end);   /* key0,val0, key1,val1, …, end */
void  Table_free(T *t);
```

- `hint` is an advisory size estimate; pass a rough expected count (e.g. 0 is fine).
- Pass `cmp`/`hash` matching your keys. For atom keys, `cmp` returns `x != y` and `hash` returns `(unsigned)key` (pointer identity). For C-string keys, supply `strcmp`-based functions.
- `Table_put` returns the previous value for that key (or NULL), so you can detect/replace duplicates.
- `Table_toArray` lays out **alternating key,value** pairs ending in `end`.
- Iteration order is unspecified; `Table_map`'s `apply` may modify the value in place via `*value`.

## `Set` — hash set with set algebra

```c
T    Set_new (int hint, int cmp(const void *x, const void *y),
                        unsigned hash(const void *x));
int  Set_member(T s, const void *member);
void Set_put   (T s, const void *member);   /* idempotent */
void *Set_remove(T s, const void *member);
int  Set_length(T s);
void Set_map   (T s, void apply(const void *member, void *cl), void *cl);
void **Set_toArray(T s, void *end);
T Set_union(T s, T t);  T Set_inter(T s, T t);
T Set_minus(T s, T t);  T Set_diff (T s, T t);   /* diff = symmetric difference */
void Set_free(T *s);
```

Same `cmp`/`hash` contract as `Table`. The four set operations return **new** sets; the operands may even use different (compatible) `cmp`/`hash`, and either may be `NULL` (treated as empty) — but not both.

## `Array` — dynamic array of fixed-size elements

Unlike the `void *` containers, `Array` stores `length` elements **of `size` bytes each, inline** (value semantics), and is resizable.

```c
T    Array_new (int length, int size);   /* length elems of size bytes, zeroed */
int  Array_length(T a);   int Array_size(T a);
void *Array_get(T a, int i);             /* pointer to element i */
void *Array_put(T a, int i, void *elem); /* copy *elem into slot i, return elem */
void Array_resize(T a, int length);
T    Array_copy  (T a, int length);
void Array_free(T *a);
```

`Array_get`/`put` bounds-check `i` (checked error). `Array_get` returns a pointer *into* the array — copy the value out; it is invalidated by `Array_resize`. The `arrayrep.h` interface exposes the representation (`length`, `size`, `char *array`) for clients that need to build an `Array` over existing storage via `ArrayRep_init` — an example of CII's "exposed representation" interface layering.

## `Seq` — extensible sequence (deque + indexable)

A growable, double-ended, index-addressable sequence of `void *`. Combines a dynamic array's O(1) indexing with a deque's O(1) ends.

```c
T Seq_new(int hint);   T Seq_seq(void *x, ...);   /* NULL-terminated literal */
int   Seq_length(T s);
void *Seq_get(T s, int i);          void *Seq_put(T s, int i, void *x);  /* 0..len-1 */
void *Seq_addlo(T s, void *x);      void *Seq_addhi(T s, void *x);       /* grow ends */
void *Seq_remlo(T s);               void *Seq_remhi(T s);                /* shrink ends */
void  Seq_free(T *s);
```

Indices for `get`/`put` are `0..length-1` (checked). `addhi`/`remhi` give a stack; `addlo`+`remhi` (or vice-versa) give a queue. Implemented as a `Ring`-backed circular buffer over a resizable array.

## `Ring` — circular sequence with rotation and positional insert

Like `Seq` but with arbitrary positional `add`/`remove` and rotation; indices wrap.

```c
T Ring_new(void);   T Ring_ring(void *x, ...);
int   Ring_length(T r);
void *Ring_get(T r, int i);          void *Ring_put(T r, int i, void *x);
void *Ring_add(T r, int pos, void *x);   /* pos in 1..len+1, or use addlo/addhi */
void *Ring_addlo(T r, void *x);      void *Ring_addhi(T r, void *x);
void *Ring_remove(T r, int i);       void *Ring_remlo(T r);   void *Ring_remhi(T r);
void  Ring_rotate(T r, int n);       /* rotate left (n>0) or right (n<0), wrapping */
void  Ring_free(T *r);
```

`Ring_rotate(r, n)` renumbers so that what was at index `n` becomes index 0. `Ring_add`'s `pos` uses 1-based "between elements" positions (see ch12 for the exact convention).

## `Bit` — bit vectors / dense integer sets

A fixed-length vector of `length` bits (indices `0..length-1`), doubling as a set of small integers with fast bitwise set algebra.

```c
T   Bit_new(int length);    int Bit_length(T s);   int Bit_count(T s);  /* # of 1s */
int Bit_get(T s, int n);    int Bit_put(T s, int n, int bit);  /* returns prior bit */
void Bit_clear(T s, int lo, int hi);   /* set range [lo,hi] to 0 */
void Bit_set  (T s, int lo, int hi);   /* …to 1 */
void Bit_not  (T s, int lo, int hi);   /* flip range */
int  Bit_lt(T s, T t);   int Bit_eq(T s, T t);   int Bit_leq(T s, T t);  /* set ⊆ tests */
void Bit_map(T s, void apply(int n, int bit, void *cl), void *cl);
T Bit_union(T s, T t);  T Bit_inter(T s, T t);
T Bit_minus(T s, T t);  T Bit_diff (T s, T t);
void Bit_free(T *s);
```

Ranges are **inclusive** `[lo, hi]`. `Bit_lt`/`Bit_leq` test proper/improper subset. The binary ops require operands of equal length and return a new same-length `Bit_T`.

---

## Picking a container

| Need | Use |
|------|-----|
| key → value lookup | `Table` (atom keys for speed) |
| membership / set algebra over arbitrary objects | `Set` |
| dense set of small integers, bit manipulation | `Bit` |
| resizable typed array (value semantics) | `Array` |
| indexable deque / queue / stack of pointers | `Seq` |
| circular buffer, rotation, positional insert | `Ring` |
| cons-cell list, direct field access, FP-style | `List` |
| simple LIFO | `Stack` |

Deep dives with annotated implementations: docs ch07 (List) ch08 (Table) ch09 (Set) ch10 (Array) ch11 (Seq) ch12 (Ring) ch13 (Bit).
