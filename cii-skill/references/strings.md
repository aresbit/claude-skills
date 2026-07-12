# Strings & formatting — `Fmt`, `Str`, `Text`

Three layers: `Fmt` is a type-safe, extensible `printf`; `Str` does non-destructive operations on ordinary C strings using a position model; `Text` is an immutable counted-string abstraction with explicit allocation control.

Headers: `headers/{fmt,str,text}.h`.

## The CII position model (used by `Str` and `Text`)

CII string operations index **between** characters, not at them. For a string of length `n`, positions run `0..n`. Position `i` sits just before character `i` (1-based char numbering), position `n` is the end. **Negative positions count from the right**: `-1` is the last gap (== `n`), `-2` is `n-1`, etc.

A substring is named by a pair `(i, j)` — the characters between positions `i` and `j`, *in either order* (`(i,j)` and `(j,i)` denote the same range). This is why nearly every `Str`/`Text` function takes `s, i, j`. `Str_sub(s, 0, -1)` is the whole string; `Str_sub(s, 1, 2)` is the first character.

Use `Str_pos`/`Text_pos` to normalize a possibly-negative position to its absolute `1..n+1` value.

## `Str` — non-destructive ops on C strings

Every `Str` function that returns a string **allocates a fresh `Mem` string** (NUL-terminated) and never mutates its arguments. You `FREE` results you no longer need.

```c
char *Str_sub (const char *s, int i, int j);                 /* the (i,j) substring */
char *Str_dup (const char *s, int i, int j, int n);          /* substring repeated n times */
char *Str_cat (const char *s1,int i1,int j1,
               const char *s2,int i2,int j2);                /* concatenation */
char *Str_catv(const char *s, ...);                          /* s,i,j, … ,NULL triples */
char *Str_reverse(const char *s, int i, int j);
char *Str_map (const char *s, int i, int j,
               const char *from, const char *to);            /* per-char translation */
int Str_pos(const char *s, int i);   int Str_len(const char *s, int i, int j);
int Str_cmp(const char *s1,int i1,int j1, const char *s2,int i2,int j2);
```

Search family — all return a **position** (0 if not found), operating on the `(i,j)` window:

```c
int Str_chr  /Str_rchr (s,i,j,c);     /* first/last position of char c */
int Str_upto /Str_rupto(s,i,j,set);   /* first/last pos of any char in set */
int Str_find /Str_rfind(s,i,j,str);   /* first/last pos where substring str occurs */
int Str_any  (s,i,set);               /* if char after i is in set, pos after it */
int Str_many /Str_rmany(s,i,j,set);   /* span of chars in set */
int Str_match/Str_rmatch(s,i,j,str);  /* anchored match of str, returns end pos */
```

`Str_fmt` is the conversion hook that lets `%s`-style codes use `Str` semantics inside `Fmt` (see below).

## `Text` — immutable counted strings

`Text_T` is a value `struct { int len; const char *str; }` — a length plus a pointer to (shared, immutable) bytes. Texts are **not NUL-terminated** and may share storage, so substrings and concatenations are cheap and never copy the underlying characters unnecessarily.

```c
typedef struct T { int len; const char *str; } Text_T;   /* a value, passed by copy */

T     Text_put(const char *str);          /* make a Text from a C string (copies in) */
char *Text_get(char *buf, int size, T s);  /* copy out to a C string (NUL-terminates) */
T     Text_box(const char *str, int len);  /* wrap existing bytes WITHOUT copying */
T Text_sub(T s, int i, int j);   int Text_pos(T s, int i);
T Text_cat(T s1, T s2);   T Text_dup(T s, int n);   T Text_reverse(T s);
T Text_map(T s, const T *from, const T *to);
int Text_cmp(T s1, T s2);
/* search family mirrors Str, returning positions */
int Text_chr/rchr/upto/rupto/any/many/rmany/find/rfind/match/rmatch(...);
```

Predefined character-set texts: `Text_cset` (all 256), `Text_ascii`, `Text_ucase`, `Text_lcase`, `Text_digits`, `Text_null` (empty).

### Allocation discipline — `Text_save`/`Text_restore`

`Text` allocates the bytes it owns from an internal stack-like region. Mark a point with `Text_save()`, allocate freely, then `Text_restore(&save)` to reclaim **all** texts created since the mark in one shot (like an arena scoped to text). `Text_box` does *not* allocate — it aliases caller-owned bytes, so those bytes must outlive the box.

```c
Text_save_T mark = Text_save();
T t = Text_cat(a, b);     /* allocations happen here */
... use t ...
Text_restore(&mark);      /* t and everything after mark is freed */
```

## `Fmt` — type-safe, extensible formatted output

A `printf` replacement that is type-checked through conversion functions and **extensible** with new codes. It raises `Fmt_Overflow` rather than silently truncating fixed buffers.

```c
void Fmt_print (const char *fmt, ...);              /* to stdout */
void Fmt_fprint(FILE *stream, const char *fmt, ...);
char *Fmt_string(const char *fmt, ...);             /* returns a fresh Mem string */
int  Fmt_sfmt(char *buf, int size, const char *fmt, ...);  /* into buf; Fmt_Overflow if too big */
void Fmt_fmt (int put(int c, void *cl), void *cl, const char *fmt, ...);  /* fully general sink */
T    Fmt_register(int code, T cvt);                 /* install a converter for a code char */
```

The core abstraction is the **`put` sink**: `int put(int c, void *cl)` consumes one character; `cl` is your closure (a `FILE *`, a buffer cursor, etc.). All output routes through a `put`, which is how `Fmt_print`/`Fmt_string`/`Fmt_sfmt` differ — they pass different `put`/`cl`.

The `vfmt`/`vsfmt`/`vstring` variants take a `va_list_box *` (CII boxes `va_list` in a struct so it is portably passable). Built-in helpers `Fmt_putd`/`Fmt_puts` emit numbers/strings honoring `flags`, `width`, `precision` inside a custom converter.

### Adding a conversion code

A converter has type `void (*Fmt_T)(int code, va_list_box *box, int put(int,void*), void *cl, unsigned char flags[256], int width, int precision)`. Pull your argument from `box->ap` with `va_arg`, then emit via `put`/`Fmt_putd`/`Fmt_puts`. Register it: `Fmt_register('D', mydate_cvt);` then use `"%D"`. This is how `Str_fmt`/`Text_fmt`/`AP_fmt`/`MP_fmt` plug their types into `Fmt`.

## Choosing

| Need | Use |
|------|-----|
| formatted output, or printing custom types | `Fmt` |
| manipulate ordinary `char *` C strings, non-destructively | `Str` |
| heavy substring/concat work, shared immutable text, scoped bulk free | `Text` |

Deep dives: docs ch14 (Fmt) ch15 (Str) ch16 (Text).
