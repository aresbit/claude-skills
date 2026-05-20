#!/usr/bin/env python3
"""
Add tracing instrumentation spans to Rust functions.

Reads Rust source from stdin or a file, identifies public and key internal
functions, and inserts `#[tracing::instrument]` attributes and span!() calls.

Usage:
    python3 instrument_rust.py < input.rs > output.rs
    python3 instrument_rust.py src/lib.rs --in-place
    python3 instrument_rust.py src/ --recursive --dry-run
"""

import sys
import re
import os

FN_RE = re.compile(
    r'^\s*(?:pub(?:\s*\(\s*crate\s*\))?\s+)?fn\s+(\w+)\s*[<(]',
    re.MULTILINE,
)

INSTRUMENT_TEMPLATE = '#[tracing::instrument(skip(self), fields())]\n'


def instrument_file(path: str) -> str:
    with open(path) as f:
        content = f.read()

    lines = content.split('\n')
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = FN_RE.match(line)
        if m and '#[tracing::instrument' not in lines[max(0, i - 3):i + 1].__str__():
            fn_name = m.group(1)
            if fn_name not in ('new', 'default', 'len', 'is_empty'):
                out.append(f'#[tracing::instrument(skip(self), fields())]')
        out.append(line)
        i += 1

    return '\n'.join(out)


def main():
    dry_run = '--dry-run' in sys.argv
    recursive = '--recursive' in sys.argv
    in_place = '--in-place' in sys.argv

    paths = [a for a in sys.argv[1:] if not a.startswith('--')]

    if not paths:
        # Read from stdin
        import fileinput
        content = ''.join(fileinput.input())
        lines = content.split('\n')
        out = []
        for i, line in enumerate(lines):
            m = FN_RE.match(line)
            if m:
                fn_name = m.group(1)
                if fn_name not in ('new', 'default', 'len', 'is_empty'):
                    out.append(f'#[tracing::instrument]')
            out.append(line)
        print('\n'.join(out))
        return

    if recursive:
        for path in paths:
            for root, _, files in os.walk(path):
                for f in files:
                    if f.endswith('.rs'):
                        full = os.path.join(root, f)
                        process_file(full, dry_run, in_place)
    else:
        for path in paths:
            if os.path.isdir(path):
                print(f"Use --recursive for directories: {path}", file=sys.stderr)
                sys.exit(1)
            process_file(path, dry_run, in_place)


def process_file(path: str, dry_run: bool, in_place: bool):
    result = instrument_file(path)
    if dry_run:
        print(f"[DRY RUN] Would instrument {path}")
    elif in_place:
        with open(path, 'w') as f:
            f.write(result)
        print(f"[OK] Instrumented {path}")
    else:
        print(result)


if __name__ == '__main__':
    main()
