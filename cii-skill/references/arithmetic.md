# Arithmetic — `AP`, `MP`, `Arith`

Two big-number packages plus a small portable-arithmetic helper.

- `AP` — **arbitrary precision** signed integers (grow as needed). Easiest to use; objects are heap-allocated and opaque.
- `MP` — **fixed multiple precision**: every number is exactly `n` bits, chosen once via `MP_set`. Closer to hardware (two's-complement, modular wraparound), used to model machine words of arbitrary width.
- `Arith` — portable, well-defined integer `div`/`mod`/`floor`/`ceiling`/`min`/`max` (C's `/` and `%` are implementation-defined for negatives; `Arith` isn't).

Headers: `headers/{ap,mp,arith}.h`.

## `Arith` — well-defined integer arithmetic

```c
int Arith_max(int x,int y);   int Arith_min(int x,int y);
int Arith_div(int x,int y);   int Arith_mod(int x,int y);     /* floored division */
int Arith_floor(int x,int y); int Arith_ceiling(int x,int y);
```

Use these whenever the sign of an operand can be negative and you need the mathematical (floored) result, independent of platform. `Arith_div`/`Arith_mod` satisfy `Arith_div(x,y)*y + Arith_mod(x,y) == x` with `Arith_mod` having the sign of `y`.

## `AP` — arbitrary-precision integers

`AP_T` is opaque and heap-allocated; results are **new** objects you must `AP_free`. Numbers grow to whatever size the value needs.

```c
T AP_new(long n);   T AP_fromstr(const char *s, int base, char **end);
long  AP_toint(T x);   char *AP_tostr(char *buf, int size, int base, T x);
void  AP_free(T *z);
T AP_neg(T x);
T AP_add(T x,T y);  T AP_sub(T x,T y);  T AP_mul(T x,T y);
T AP_div(T x,T y);  T AP_mod(T x,T y);            /* floored, like Arith */
T AP_pow(T x,T y,T p);                            /* x^y, or x^y mod p if p != NULL */
T AP_addi/subi/muli/divi(T x, long y);  long AP_modi(T x, long y);   /* mixed with long */
T AP_lshift(T x,int s);  T AP_rshift(T x,int s);
int AP_cmp(T x,T y);   int AP_cmpi(T x, long y);   /* <0, 0, >0 */
void AP_fmt(...);                                  /* Fmt converter; register for a code */
```

Idioms:
- Every binary op allocates; in a loop, `AP_free` intermediates or you leak. A `tmp = AP_add(a,b); AP_free(&a); a = tmp;` pattern is common.
- `AP_fromstr(s, base, &end)` parses in any base 2..36 and sets `*end` past the last consumed char (like `strtol`).
- Plug into `Fmt`: `Fmt_register('A', AP_fmt);` then `Fmt_print("%A\n", x);` (the exact code char is your choice).

## `MP` — fixed multiple precision (modeling N-bit machine arithmetic)

`MP_T` is `unsigned char *` — a raw little array of bytes representing exactly the current width. **You choose the width once** with `MP_set(n)` (n bits); all operations are modulo 2^n (unsigned) or two's-complement (signed), exactly like an n-bit CPU. The caller **owns and supplies the destination** `z` (no allocation per op): `MP_add(z, x, y)` writes into `z` and returns it.

```c
int MP_set(int n);                 /* set word width to n bits; returns previous */
T MP_new(unsigned long u);         /* allocate one word initialized to u */
T MP_fromint(T z,long v);  T MP_fromintu(T z,unsigned long u);
long MP_toint(T x);   unsigned long MP_tointu(T x);
T MP_cvt(int m,T z,T x);  T MP_cvtu(int m,T z,T x);   /* widen/narrow to m bits into z */

/* signed (two's-complement, raise MP_Overflow on signed overflow) */
T MP_add/sub/mul/div/mod/neg(T z, T x[, T y]);
/* unsigned (modular wraparound, no overflow) */
T MP_addu/subu/mulu/divu/modu(T z,T x,T y);
T MP_mul2u/mul2(T z,T x,T y);      /* double-width product */
/* mixed with long / unsigned long */
T MP_addi/subi/muli/divi(T z,T x,long y);   long MP_modi(T x,long y);
T MP_addui/subui/mului/divui(...);          unsigned long MP_modui(...);
/* compares */  int MP_cmp/cmpi/cmpu/cmpui(...);
/* bitwise */   T MP_and/or/xor/not(...);  T MP_andi/ori/xori(...);
/* shifts */    T MP_lshift/rshift(T z,T x,int s);  T MP_ashift(...);   /* arithmetic shift */
/* I/O */       T MP_fromstr(T z,const char *s,int base,char **end);
                char *MP_tostr(char *buf,int size,int base,T x);
                void MP_fmt(...);   void MP_fmtu(...);
```

Exceptions: `MP_Overflow` (signed op overflowed the fixed width), `MP_Dividebyzero`.

Key distinctions from `AP`:
- **Fixed width**: results wrap (unsigned) or overflow-raise (signed); they never grow. This is the point — `MP` models hardware of a chosen word size (e.g. simulate 24-bit or 256-bit machine integers).
- **Caller-allocated destinations**: pass a `z` you made with `MP_new`; ops reuse it. No per-op `free`; free your words once at the end with `FREE`.
- Signed vs unsigned are *different functions* (`MP_add` vs `MP_addu`), not a type distinction.

## Choosing

| Need | Use |
|------|-----|
| big integers that just grow (crypto-ish, factorials, exact math) | `AP` |
| model a CPU of a specific bit width, modular/two's-complement semantics | `MP` |
| portable floored div/mod/floor/ceiling on `int` | `Arith` |

`Calc` (docs ch19, `code/calc.c`) and `mpcalc` are full worked examples: an interactive arbitrary-precision calculator built on `AP`/`MP`, exercising the parser + the arithmetic interface end to end. Read them for a realistic client. Deep dives: docs ch17 (XP/AP) ch18 (MP) ch19 (Calc).
