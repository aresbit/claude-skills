# Error handling — `Except` and `assert`

CII splits errors into two kinds and handles them with two mechanisms. Getting this split right is the single most important CII habit.

- **Checked runtime error** → the *caller broke the contract* (bad argument, empty pop, out-of-range index). Use `assert`. It is a bug; aborting is correct.
- **Exception** → a condition the program may legitimately recover from (out of memory, overflow, parse failure, I/O error). Use `RAISE`/`TRY`.

Header: `headers/except.h`, `headers/assert.h`.

## Exceptions: `Except_T` and the `TRY` macros

An exception is a statically-allocated value of type `Except_T` (a struct wrapping a `reason` string). Declare each exception as a `const Except_T` with external linkage so its *address* is its identity:

```c
const Except_T Mem_Failed = { "Allocation Failed" };
```

### Raising

```c
RAISE(e);     /* e is an Except_T lvalue; records __FILE__/__LINE__ and longjmps */
RERAISE;      /* re-raise the exception currently being handled, preserving origin */
```

`RAISE` with no active handler calls a default handler that prints `reason`, file, and line, then aborts.

### Handling — the five-clause statement

```c
TRY
    stmts;                 /* the protected body */
EXCEPT(e1)
    handler-for-e1;        /* runs if e1 was raised in the body */
EXCEPT(e2)
    handler-for-e2;
ELSE
    handler-for-any-other; /* catch-all */
FINALLY
    cleanup;               /* always runs, raised or not */
END_TRY;
```

All clauses are optional except `TRY`/`END_TRY`. Common shapes: `TRY … EXCEPT(e) … END_TRY` and `TRY … FINALLY … END_TRY`. Inside a handler, the variable `Except_frame.exception` points to the raised exception.

### Critical pitfalls

- **Never `return`, `break`, `continue`, or `goto` out of a `TRY` body.** The macros maintain a stack of `Except_Frame`s via `setjmp`; jumping out leaves the stack corrupted. To return from inside a `TRY`, use the provided `RETURN` macro, which pops the frame first. (`break`/`continue` targeting a loop *outside* the TRY are likewise unsafe.)
- **Variables modified in the body and used in a handler must be `volatile`**, or `setjmp` semantics leave them indeterminate after a `longjmp`.
- Exceptions are matched by **address**, so every `Except_T` must be a single shared object (declare in a header as `extern const Except_T X;`, define once in a `.c`).

### Defining your own exception

```c
/* foo.h */  extern const Except_T Foo_Overflow;
/* foo.c */  const Except_T Foo_Overflow = { "Foo overflow" };
/* use   */  if (would_overflow) RAISE(Foo_Overflow);
```

## Assertions: `assert`

CII replaces the standard `assert`. Include `"assert.h"` (the CII one), **not** `<assert.h>`. On failure it does `RAISE(Assert_Failed)` instead of calling `abort` directly, so an assertion failure flows through the same exception machinery (and can, in principle, be caught — though normally you let it abort). Defining `NDEBUG` compiles assertions out, exactly like the standard.

Use it to validate the *interface contract* at the top of every public function:

```c
void *Array_get(T array, int i) {
    assert(array);
    assert(i >= 0 && i < array->length);   /* checked runtime error */
    return array->array + i*array->size;
}
```

Do not use `assert` for recoverable conditions (e.g. a malloc failure) — that is what exceptions are for.

## Quick decision guide

| Situation | Mechanism |
|-----------|-----------|
| NULL handle, bad index, empty-container pop, contract violation | `assert` |
| Out of memory | `RAISE(Mem_Failed)` (done for you by `Mem`) |
| Arithmetic overflow / divide-by-zero | `RAISE(..._Overflow / ..._Dividebyzero)` |
| Parse/format/IO failure the caller may retry | custom exception + `TRY` |

The exceptions exported by CII modules: `Assert_Failed` (assert.h), `Mem_Failed` (mem.h), `Arena_NewFailed`/`Arena_Failed` (arena.h), `Fmt_Overflow` (fmt.h), `MP_Overflow`/`MP_Dividebyzero` (mp.h), `Thread_Failed`/`Thread_Alerted` (thread.h).
