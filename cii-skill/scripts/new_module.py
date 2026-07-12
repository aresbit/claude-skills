#!/usr/bin/env python3
"""Scaffold a CII-style module: a paired .h interface + .c implementation.

Generates code that follows the CII house style exactly — opaque `T` ADT,
two-level `Module_` naming, the `#define T … typedef struct T *T … #undef T`
idiom, `Module_new`/`Module_free(T *)` lifecycle, assert-guarded operations,
and Mem-based allocation. The point is to remove the boilerplate so you start
every new module already in the right shape.

Usage:
    python new_module.py Stack
    python new_module.py SymTable --out ./src --ops "put,get,length"
    python new_module.py Buffer --hint            # constructor takes an int hint
    python new_module.py Pair --transparent       # public struct (like List_T)

Each op in --ops becomes an `extern` declaration in the .h and a stub in the
.c with an `assert(self)` guard. Edit the signatures and fill in the bodies.
"""
import argparse
import re
import sys
from pathlib import Path


def derive_names(module: str) -> dict:
    """From a module name (e.g. 'SymTable') derive every name CII needs."""
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", module):
        sys.exit(f"error: '{module}' is not a valid C identifier for a module name")
    # File stem is the lowercased module name; clients #include "symtable.h".
    stem = module.lower()
    return {
        "module": module,              # SymTable
        "type": f"{module}_T",         # SymTable_T
        "stem": stem,                  # symtable
        "guard": f"{stem.upper()}_INCLUDED",  # SYMTABLE_INCLUDED
    }


def render_header(n: dict, ops: list[str], hint: bool, transparent: bool) -> str:
    L = []
    a = L.append
    a(f"#ifndef {n['guard']}")
    a(f"#define {n['guard']}")
    a(f"#define T {n['type']}")
    if transparent:
        # Public representation, like List_T — clients traverse the fields.
        a("typedef struct T *T;")
        a("struct T {")
        a("\tT next;")
        a("\tvoid *value;")
        a("};")
    else:
        a("typedef struct T *T;")
    a("")
    ctor = f"extern T    {n['module']}_new (int hint);" if hint \
        else f"extern T    {n['module']}_new (void);"
    a(ctor)
    a(f"extern void {n['module']}_free(T *{n['stem']});")
    for op in ops:
        a(f"extern void {n['module']}_{op}(T {n['stem']});  /* TODO: real signature & doc */")
    a("")
    a("#undef T")
    a("#endif")
    a("")
    return "\n".join(L)


def render_impl(n: dict, ops: list[str], hint: bool, transparent: bool) -> str:
    L = []
    a = L.append
    a("#include <stddef.h>")
    a('#include "assert.h"')
    a('#include "mem.h"')
    a(f'#include "{n["stem"]}.h"')
    a("")
    a(f"#define T {n['type']}")
    if not transparent:
        a("struct T {")
        a("\tint dummy;  /* TODO: replace with the real representation */")
        a("};")
        a("")
    sig = "int hint" if hint else "void"
    a(f"T {n['module']}_new({sig}) {{")
    a("\tT self;")
    if hint:
        a("\tassert(hint >= 0);")
    a("\tNEW0(self);          /* raises Mem_Failed on exhaustion; zero-initialized */")
    a("\t/* TODO: initialize self from the arguments */")
    a("\treturn self;")
    a("}")
    a("")
    a(f"void {n['module']}_free(T *{n['stem']}) {{")
    a(f"\tassert({n['stem']} && *{n['stem']});   /* checked runtime error: NULL handle */")
    a("\t/* TODO: free anything self owns before releasing it */")
    a(f"\tFREE(*{n['stem']});                /* frees the object and nulls the caller's pointer */")
    a("}")
    for op in ops:
        a("")
        a(f"void {n['module']}_{op}(T {n['stem']}) {{")
        a(f"\tassert({n['stem']});")
        a("\t/* TODO: implement */")
        a("}")
    a("")
    return "\n".join(L)


def main() -> None:
    p = argparse.ArgumentParser(description="Scaffold a CII-style .h/.c module pair.")
    p.add_argument("module", help="Module name in CamelCase, e.g. Stack or SymTable")
    p.add_argument("--out", default=".", help="Output directory (default: current dir)")
    p.add_argument("--ops", default="", help="Comma-separated extra operation names")
    p.add_argument("--hint", action="store_true",
                   help="Constructor takes an int size hint (like Table/Seq)")
    p.add_argument("--transparent", action="store_true",
                   help="Expose the representation publicly (like List_T)")
    p.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = p.parse_args()

    n = derive_names(args.module)
    ops = [o.strip() for o in args.ops.split(",") if o.strip()]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    targets = {
        out / f"{n['stem']}.h": render_header(n, ops, args.hint, args.transparent),
        out / f"{n['stem']}.c": render_impl(n, ops, args.hint, args.transparent),
    }
    for path in targets:
        if path.exists() and not args.force:
            sys.exit(f"error: {path} already exists (use --force to overwrite)")
    for path, content in targets.items():
        path.write_text(content)
        print(f"wrote {path}")

    print(f"\nNext: define `struct T` in {n['stem']}.c, fill in {n['module']}_new, "
          f"and give each operation its real signature + documented errors.")
    print(f"Compile a client with:  gcc -I. client.c {n['stem']}.c mem.c except.c assert.c -o client")


if __name__ == "__main__":
    main()
