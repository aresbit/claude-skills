# Memory — `Mem` and `Arena`

Two allocators. Use `Mem` for ordinary object-by-object allocation; use `Arena` when many allocations share one lifetime and you want to free them in O(1) all at once. Never call `malloc`/`free` directly in CII code.

Headers: `headers/mem.h`, `headers/arena.h`.

## `Mem` — the production allocator

A thin, instrumented wrapper over `malloc` that **never returns NULL** — on exhaustion it raises `Mem_Failed`, so client code is free of `if (p == NULL)` checks. Every call records `__FILE__`/`__LINE__` for leak/error reporting.

Always use the macros, not the underlying `Mem_alloc` functions:

| Macro | Meaning |
|-------|---------|
| `NEW(p)` | allocate `sizeof *p` bytes, assign to `p` (uninitialized) |
| `NEW0(p)` | same, zero-filled |
| `ALLOC(n)` | allocate `n` bytes, returns `void *` |
| `CALLOC(c, n)` | allocate `c*n` zeroed bytes |
| `RESIZE(p, n)` | resize the block `p` points to, reassign `p` |
| `FREE(p)` | free `p` **and set `p = NULL`** |

```c
struct node *p;
NEW(p);                 /* p points to one uninitialized struct node */
NEW0(p);                /* ... zero-initialized */
FREE(p);                /* freed; p is now NULL (use-after-free becomes NULL-deref) */
```

Because `NEW` derives the size from `*p`, you never write `sizeof(struct node)` and never get the type wrong. `FREE` nulling the pointer is deliberate — pair it with `assert(p)` guards to turn use-after-free into an immediate, checked error.

There is a debugging implementation (`memchk`) that detects double-frees, leaks, and frees of non-heap pointers; the production one (`mem.c`) is lean. They share the same interface — link whichever you want.

## `Arena` — region / arena allocation

An `Arena_T` owns a growing list of large blocks. You allocate from it cheaply (bump a pointer) and **cannot free individual objects** — you free or dispose the whole arena at once. This is ideal for phase-scoped data: a parse tree, a per-request scratch space, a compiler pass.

```c
Arena_T arena = Arena_new();
Sym  *s  = Arena_alloc (arena, sizeof *s, __FILE__, __LINE__);
char *buf = Arena_calloc(arena, n, 1,     __FILE__, __LINE__);
...
Arena_free(&arena_thing);   /* frees all objects, keeps arena reusable... see below */
Arena_dispose(&arena);      /* frees everything incl. the arena; *ap = NULL */
```

API (`headers/arena.h`):

| Function | Effect |
|----------|--------|
| `Arena_new()` | create an empty arena; raises `Arena_NewFailed` |
| `Arena_alloc(a, n, file, line)` | bump-allocate `n` bytes; raises `Arena_Failed` |
| `Arena_calloc(a, c, n, file, line)` | zeroed `c*n` bytes |
| `Arena_free(a)` | release all objects but **keep the arena alive** (blocks recycled for reuse) |
| `Arena_dispose(ap)` | free all objects *and* the arena; sets `*ap = NULL` |

Pass `__FILE__, __LINE__` explicitly (Arena has no convenience macros in the base interface). The win is twofold: allocation is nearly free, and deallocation is one call with no chance of leaking or double-freeing the individual objects. The tradeoff: memory is held until the whole arena is freed, so don't put long-lived and short-lived data in the same arena.

## Choosing between them

| Use `Mem` when | Use `Arena` when |
|----------------|------------------|
| objects have independent, unpredictable lifetimes | many objects live and die together as a phase |
| you need to free and reclaim individually | you want O(1) bulk free and zero per-object bookkeeping |
| building a general container (CII containers use `Mem`) | building scratch/AST/per-request data |

Deeper dive (allocation algorithm, alignment via a `union align`, the debugging allocator): docs ch05 (Mem) and ch06 (Arena).
