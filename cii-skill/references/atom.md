# `Atom` — immutable interned strings

An **atom** is a pointer to a unique, immutable, NUL-terminated sequence of bytes. CII guarantees that two atoms are equal *if and only if their pointers are equal* — so string comparison collapses to `==`, and atoms make ideal hash-table/set keys.

Header: `headers/atom.h`.

```c
extern       int   Atom_length(const char *str);            /* length of an atom */
extern const char *Atom_new   (const char *str, int len);   /* intern len bytes */
extern const char *Atom_string(const char *str);            /* intern a C string */
extern const char *Atom_int   (long n);                     /* intern decimal of n */
```

## Semantics

- `Atom_string("foo")` and `Atom_string("foo")` return the **same pointer**. Once created, an atom is never moved or freed — atoms live for the life of the program (this is intentional; it is why identity comparison is sound).
- `Atom_new(str, len)` interns exactly `len` bytes (may contain embedded NULs); a terminating NUL is added. `Atom_string(s)` is `Atom_new(s, strlen(s))`.
- `Atom_int(n)` returns the atom of the decimal text of `n` — handy for using integers as table keys.
- The returned `const char *` must be treated as immutable; never cast away `const` and write through it.

## Idiom: atoms as keys

Because equal strings share one pointer, a hash table keyed on atoms can compare keys with pointer equality and hash on the pointer value:

```c
const char *key = Atom_string(name);
Table_put(t, key, value);
...
void *v = Table_get(t, Atom_string(name));   /* same pointer → found */
```

Use the `atomcmp`/`atomhash`-style functions (compare/hash on the pointer) when constructing such a `Table`/`Set`. See `references/containers.md`.

## When to use

- Symbol tables, identifier interning in compilers/interpreters.
- Any time you compare the same strings repeatedly — pay the hashing cost once at intern time, then compare with `==`.
- **Not** for large or short-lived string data: atoms are never reclaimed, so interning megabytes of transient text is a leak. For mutable/region-scoped strings use `Str`/`Text` (`references/strings.md`).

Implementation note: atoms are stored in a fixed bucket hash table of variable-length records; the string bytes are stored inline after the header (a flexible/struct-hack array member). Deep dive and the integer-to-string algorithm: docs ch03.
