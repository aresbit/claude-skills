# Design principles — inventing good CII interfaces (ch1–2)

This is the *why* behind the house style in SKILL.md. Read it when designing a new module rather than just consuming an existing one.

## Interfaces vs. implementations

An **interface** specifies *what* a module does — the types, functions, and the contract (preconditions, postconditions, which errors are checked vs. raised). An **implementation** provides *how*. The interface is the only thing clients depend on; any implementation honoring it is interchangeable. The goal is **reuse**: a well-designed interface is used unchanged by many clients and survives multiple implementations.

A good interface is:
- **Small and orthogonal** — few functions, each doing one thing, composing cleanly. Resist adding an operation that clients can build from existing ones.
- **Complete** — clients never need to know the representation to get their job done. If they must reach behind the curtain, the interface is missing something.
- **Honest about errors** — every function documents what it checks (`assert`) and what it raises (exceptions).

## Abstract data types and opaque pointers

Most CII modules export one ADT as an **opaque pointer** (`typedef struct T *T;` with the real `struct T` defined only in the `.c`). Clients manipulate values of type `Module_T` solely through the functions. Benefits:
- The representation can change without recompiling clients (only relinking).
- Clients *cannot* corrupt invariants by touching fields.
- Lifetime is explicit and centralized in `Module_new` / `Module_free`.

When you *do* want clients to see the representation (rare, for performance or layering), provide it in a **separate** interface — e.g. `arrayrep.h` exposes `Array_T`'s fields for code that builds arrays over existing storage, while `array.h` stays opaque. `List_T` is the other exception: its cons-cell representation is public because direct traversal is the point. Make exposure a deliberate, separately-included decision, never the default.

## Naming and namespace discipline

C has no namespaces, so CII manufactures them with the `Module_` prefix. Rules:
- Every exported function, type, and variable begins with `Module_` (or `Module` for the type, as `Module_T`).
- The exported type is `Module_T`; inside the interface and implementation it is abbreviated to `T` via `#define T Module_T` … `#undef T` so the source reads cleanly without leaking the macro.
- Exception objects are `Module_Reason` (`Mem_Failed`, `Fmt_Overflow`).
- Nothing else has external linkage. Helper functions in the `.c` are `static`.

This makes name collisions across modules essentially impossible and makes every symbol's origin obvious at the call site.

## Checked vs. unchecked errors (and why two mechanisms)

CII deliberately uses **two** error mechanisms because the two failure kinds need different responses:

| | Checked runtime error | Exception |
|--|----------------------|-----------|
| Cause | client violated the contract (a bug) | environmental condition (out of memory, overflow, EOF) |
| Mechanism | `assert(e)` → `Assert_Failed` → abort | `RAISE(e)` → `TRY/EXCEPT` |
| Right response | fix the calling code | recover or propagate at runtime |
| Compiled out by `NDEBUG`? | yes | no |

The discipline: **validate the contract with `assert` at the top of every public function**, and reserve exceptions for conditions a correct client still cannot prevent. Don't blur them — using exceptions for contract violations hides bugs; using `assert` for out-of-memory makes failures uncatchable. See `references/error-handling.md`.

## Resource ownership conventions

- **Constructor/destructor pairing**: `Module_new(...)` allocates and returns a `T`; `Module_free(T *)` releases it and nulls the caller's handle. Whole-region modules use `Module_dispose` (`Arena_dispose`).
- **Element ownership**: `void *` containers store and return *your* pointers; they never free the pointed-to data. Freeing a `List`/`Table`/`Set` frees its own cells/nodes only — element lifetimes are yours.
- **Returned strings/arrays** from `Str`/`Fmt`/`*_toArray` are fresh `Mem` allocations the client must `FREE`.

## Designing a new module — checklist

1. Name the abstraction and its one exported type `Module_T`.
2. List the operations a client genuinely needs; cut anything derivable.
3. For each, decide arguments, return value, checked errors, and raised exceptions — write these as comments in the `.h`.
4. Keep the representation out of the `.h` (opaque) unless exposure is a deliberate, separately-headered choice.
5. In the `.c`: `#define T`, define `struct T`, guard every function with `assert`, allocate through `Mem`/`Arena`, make helpers `static`.
6. Provide `Module_new` / `Module_free`.

Full treatment with the design rationale, examples, and exercises: docs ch01 (Introduction) and ch02 (Interfaces and Implementations).
